from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aigc_detection.eval.m4_audit import (  # noqa: E402
    aggregate_seed_audit,
    load_reference_artifacts,
    load_seed_metrics,
    render_aggregate_markdown,
    render_run_status_markdown,
)


DEFAULT_MANIFEST = (
    REPO_ROOT
    / "data"
    / "mirrored"
    / "br_gen"
    / "subsets"
    / "restricted_pilot"
    / "manifest"
    / "formal_manifest.jsonl"
)
DEFAULT_BASELINE_EVAL_DIR = REPO_ROOT / "outputs" / "m4" / "restricted_pilot" / "eval_baseline"
DEFAULT_BASELINE_PREDICTIONS = (
    REPO_ROOT / "outputs" / "m4" / "restricted_pilot" / "predictions_baseline.jsonl"
)
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "outputs" / "m4" / "multi_seed_audit"
DEFAULT_LOCAL_MODULE_CONFIG = REPO_ROOT / "configs" / "model" / "local_module.yaml"
DEFAULT_HF_MODEL_REPO = (
    REPO_ROOT / "external" / "Community-Forensics" / "weights" / "commfor-model-384"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the M4 multi-seed stability audit for the no-train local probe."
    )
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--baseline-eval-dir", default=str(DEFAULT_BASELINE_EVAL_DIR))
    parser.add_argument("--baseline-predictions", default=str(DEFAULT_BASELINE_PREDICTIONS))
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--hf-model-repo", default=str(DEFAULT_HF_MODEL_REPO))
    parser.add_argument("--model-size", default="small", choices=("small", "tiny"))
    parser.add_argument("--input-size", type=int, default=384, choices=(224, 384))
    parser.add_argument("--patch-size", type=int, default=16, choices=(16, 32))
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--device", default="auto", choices=("auto", "cpu", "cuda"))
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--seeds", default="0,1,2,3,4")
    parser.add_argument("--progress-every", type=int, default=100)
    parser.add_argument("--local-module-config", default=str(DEFAULT_LOCAL_MODULE_CONFIG))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    manifest_path = Path(args.manifest).resolve()
    baseline_eval_dir = Path(args.baseline_eval_dir).resolve()
    baseline_predictions_path = Path(args.baseline_predictions).resolve()
    output_root = Path(args.output_root).resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    reference = load_reference_artifacts(baseline_eval_dir)
    _validate_reference(reference, manifest_path)

    seeds = _parse_seeds(args.seeds)
    run_id = _make_run_id(output_root)
    run_dir = output_root / run_id
    run_dir.mkdir(parents=False, exist_ok=False)

    print(
        f"[M4 multi-seed] run_id={run_id} | baseline_reuse=yes | seeds={len(seeds)} | output={run_dir}",
        flush=True,
    )
    print(f"[M4 multi-seed] manifest={manifest_path}", flush=True)
    print(f"[M4 multi-seed] baseline eval dir={baseline_eval_dir}", flush=True)
    print(f"[M4 multi-seed] baseline predictions={baseline_predictions_path}", flush=True)

    started_at = datetime.now(timezone.utc)
    seed_runs: list[dict[str, Any]] = []

    for index, seed in enumerate(seeds, start=1):
        seed_dir = run_dir / f"seed_{index - 1:03d}"
        seed_dir.mkdir(parents=False, exist_ok=False)
        print(
            f"[M4 multi-seed] seed {index}/{len(seeds)} -> {seed} | output={seed_dir}",
            flush=True,
        )
        seed_record = _run_single_seed(
            seed=seed,
            seed_index=index - 1,
            total_seeds=len(seeds),
            seed_dir=seed_dir,
            manifest_path=manifest_path,
            args=args,
        )
        seed_runs.append(seed_record)
        current_summary = {
            "run_id": run_id,
            "scope": reference.get("evaluation_scope"),
            "manifest_path": str(manifest_path),
            "output_root": str(output_root),
            "seed_runs": seed_runs,
            "status": _status_from_seed_runs(seed_runs),
        }
        _write_text(run_dir / "run_status.md", render_run_status_markdown(current_summary))

    completed_at = datetime.now(timezone.utc)
    aggregate_error: str | None = None
    try:
        summary = aggregate_seed_audit(
            run_id=run_id,
            manifest_path=manifest_path,
            output_root=output_root,
            reference=reference,
            seed_runs=seed_runs,
            baseline_eval_dir=baseline_eval_dir,
            baseline_predictions_path=baseline_predictions_path,
        )
    except ValueError as error:
        aggregate_error = str(error)
        summary = {
            "run_id": run_id,
            "scope": reference.get("evaluation_scope"),
            "manifest_path": str(manifest_path),
            "output_root": str(output_root),
            "baseline": {
                "eval_dir": str(baseline_eval_dir),
                "predictions_path": str(baseline_predictions_path),
                "reference": reference,
            },
            "seed_runs": seed_runs,
            "status": _status_from_seed_runs(seed_runs),
            "aggregate": {
                "numeric_metrics": {},
                "subtlety": {
                    "baseline": reference["subtlety"]["status"],
                    "local_statuses": [],
                    "local_status_counts": {},
                    "all_same": False,
                },
                "error": aggregate_error,
            },
        }
    summary["started_at_utc"] = started_at.isoformat().replace("+00:00", "Z")
    summary["completed_at_utc"] = completed_at.isoformat().replace("+00:00", "Z")
    summary["requested_seeds"] = seeds
    summary["baseline_reference"] = reference

    _write_json(run_dir / "summary.json", summary)
    _write_json(
        run_dir / "manifest.json",
        _build_manifest_payload(
            summary=summary,
            args=args,
            manifest_path=manifest_path,
            baseline_eval_dir=baseline_eval_dir,
            baseline_predictions_path=baseline_predictions_path,
        ),
    )
    _write_json(run_dir / "aggregate_metrics.json", summary["aggregate"])
    if summary["aggregate"]["numeric_metrics"]:
        _write_text(run_dir / "aggregate_metrics.md", render_aggregate_markdown(summary))
    else:
        _write_text(
            run_dir / "aggregate_metrics.md",
            "\n".join(
                [
                    "# M4 Multi-Seed Local Probe Audit",
                    "",
                    f"- Run ID: `{summary['run_id']}`",
                    f"- Scope: `{summary.get('scope')}`",
                    f"- Manifest: `{summary['manifest_path']}`",
                    f"- Output root: `{summary['output_root']}`",
                    f"- Successful seeds: `{summary['status']['successful_seeds']}` / `{summary['status']['total_seeds']}`",
                    f"- Failed seeds: `{summary['status']['failed_seeds']}`",
                    "",
                    "No successful seeds were available for aggregation.",
                    f"Aggregate error: `{summary['aggregate']['error']}`",
                    "",
                ]
            ),
        )
    _write_text(run_dir / "run_status.md", render_run_status_markdown(summary))

    print(f"[M4 multi-seed] aggregate metrics: {run_dir / 'aggregate_metrics.json'}", flush=True)
    print(f"[M4 multi-seed] aggregate markdown: {run_dir / 'aggregate_metrics.md'}", flush=True)
    print(f"[M4 multi-seed] run status: {run_dir / 'run_status.md'}", flush=True)
    print(
        f"[M4 multi-seed] success={summary['status']['successful_seeds']} | failure={summary['status']['failed_seeds']}",
        flush=True,
    )
    return 0 if summary["status"]["successful_seeds"] > 0 else 1


def _run_single_seed(
    *,
    seed: int,
    seed_index: int,
    total_seeds: int,
    seed_dir: Path,
    manifest_path: Path,
    args: argparse.Namespace,
) -> dict[str, Any]:
    started_at = datetime.now(timezone.utc)
    stage_status = {"export": "pending", "eval": "pending"}
    stage_durations: dict[str, float] = {}

    export_output = seed_dir / "predictions_local_module.jsonl"
    eval_dir = seed_dir / "eval"
    export_log = seed_dir / "export.log"
    eval_log = seed_dir / "eval.log"

    export_command = [
        sys.executable,
        "-u",
        str(REPO_ROOT / "scripts" / "export_community_forensics_predictions.py"),
        "--manifest",
        str(manifest_path),
        "--output",
        str(export_output),
        "--device",
        args.device,
        "--batch-size",
        str(args.batch_size),
        "--num-workers",
        str(args.num_workers),
        "--use-local-module",
        "--local-module-config",
        str(Path(args.local_module_config).resolve()),
        "--seed",
        str(seed),
        "--progress-every",
        str(args.progress_every),
        "--hf-model-repo",
        args.hf_model_repo,
        "--model-size",
        args.model_size,
        "--input-size",
        str(args.input_size),
        "--patch-size",
        str(args.patch_size),
    ]
    eval_command = [
        sys.executable,
        "-u",
        str(REPO_ROOT / "scripts" / "run_m3_formal_eval.py"),
        "--manifest",
        str(manifest_path),
        "--predictions",
        str(export_output),
        "--output-dir",
        str(eval_dir),
        "--threshold",
        str(args.threshold),
    ]

    _write_json(seed_dir / "export_command.json", {"argv": export_command, "display": _format_command(export_command)})
    _write_json(seed_dir / "eval_command.json", {"argv": eval_command, "display": _format_command(eval_command)})

    export_started = time.perf_counter()
    export_error: str | None = None
    try:
        _run_command(export_command, log_path=export_log, cwd=REPO_ROOT, prefix=f"seed {seed:03d} export")
        stage_status["export"] = "success"
    except subprocess.CalledProcessError:
        stage_status["export"] = "failed"
        export_error = _read_tail(export_log)
    stage_durations["export"] = time.perf_counter() - export_started
    if stage_status["export"] != "success":
        finished_at = datetime.now(timezone.utc)
        metadata = _build_metadata(
            seed=seed,
            seed_index=seed_index,
            total_seeds=total_seeds,
            started_at=started_at,
            finished_at=finished_at,
            stage_status=stage_status,
            stage_durations=stage_durations,
            export_output=export_output,
            eval_dir=eval_dir,
            export_command=export_command,
            eval_command=eval_command,
            export_log=export_log,
            eval_log=eval_log,
            error=export_error,
            manifest_path=manifest_path,
        )
        _write_json(seed_dir / "metadata.json", metadata)
        return _seed_record(
            seed=seed,
            seed_index=seed_index,
            seed_dir=seed_dir,
            started_at=started_at,
            finished_at=finished_at,
            stage_status=stage_status,
            stage_durations=stage_durations,
            export_output=export_output,
            eval_dir=eval_dir,
            export_command=export_command,
            eval_command=eval_command,
            export_log=export_log,
            eval_log=eval_log,
            status="failed",
            error=export_error,
        )

    eval_started = time.perf_counter()
    eval_error: str | None = None
    try:
        _run_command(eval_command, log_path=eval_log, cwd=REPO_ROOT, prefix=f"seed {seed:03d} eval")
        stage_status["eval"] = "success"
    except subprocess.CalledProcessError:
        stage_status["eval"] = "failed"
        eval_error = _read_tail(eval_log)
    stage_durations["eval"] = time.perf_counter() - eval_started

    metrics = None
    status = "failed"
    error = export_error or eval_error
    if stage_status["export"] == "success" and stage_status["eval"] == "success":
        try:
            metrics = load_seed_metrics(eval_dir)
            status = "success"
        except Exception as artifact_error:  # pragma: no cover - defensive path for corrupted artifacts
            status = "failed"
            stage_status["eval"] = "failed"
            error = str(artifact_error)
            eval_error = error
            metrics = None
            status = "failed"
    finished_at = datetime.now(timezone.utc)
    metadata = _build_metadata(
        seed=seed,
        seed_index=seed_index,
        total_seeds=total_seeds,
        started_at=started_at,
        finished_at=finished_at,
        stage_status=stage_status,
        stage_durations=stage_durations,
        export_output=export_output,
        eval_dir=eval_dir,
        export_command=export_command,
        eval_command=eval_command,
        export_log=export_log,
        eval_log=eval_log,
        error=error if status != "success" else None,
        manifest_path=manifest_path,
    )
    _write_json(seed_dir / "metadata.json", metadata)
    return _seed_record(
        seed=seed,
        seed_index=seed_index,
        seed_dir=seed_dir,
        started_at=started_at,
        finished_at=finished_at,
        stage_status=stage_status,
        stage_durations=stage_durations,
        export_output=export_output,
        eval_dir=eval_dir,
        export_command=export_command,
        eval_command=eval_command,
        export_log=export_log,
        eval_log=eval_log,
        status=status,
        error=error,
        metrics=metrics,
    )


def _seed_record(
    *,
    seed: int,
    seed_index: int,
    seed_dir: Path,
    started_at: datetime,
    finished_at: datetime,
    stage_status: dict[str, str],
    stage_durations: dict[str, float],
    export_output: Path,
    eval_dir: Path,
    export_command: Sequence[str],
    eval_command: Sequence[str],
    export_log: Path,
    eval_log: Path,
    status: str,
    error: str | None,
    metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "seed": seed,
        "seed_index": seed_index,
        "seed_dir": str(seed_dir),
        "status": status,
        "stages": dict(stage_status),
        "stage_durations_seconds": dict(stage_durations),
        "duration_seconds": (finished_at - started_at).total_seconds(),
        "started_at_utc": started_at.isoformat().replace("+00:00", "Z"),
        "finished_at_utc": finished_at.isoformat().replace("+00:00", "Z"),
        "output_dir": str(seed_dir),
        "export_output": str(export_output),
        "eval_dir": str(eval_dir),
        "export_log": str(export_log),
        "eval_log": str(eval_log),
        "export_command": _format_command(export_command),
        "eval_command": _format_command(eval_command),
        "metrics": metrics,
        "error": error,
    }


def _build_metadata(
    *,
    seed: int,
    seed_index: int,
    total_seeds: int,
    started_at: datetime,
    finished_at: datetime,
    stage_status: dict[str, str],
    stage_durations: dict[str, float],
    export_output: Path,
    eval_dir: Path,
    export_command: Sequence[str],
    eval_command: Sequence[str],
    export_log: Path,
    eval_log: Path,
    error: str | None,
    manifest_path: Path,
) -> dict[str, Any]:
    return {
        "seed": seed,
        "seed_index": seed_index,
        "total_seeds": total_seeds,
        "status": "failed" if error else "success",
        "stages": dict(stage_status),
        "stage_durations_seconds": dict(stage_durations),
        "started_at_utc": started_at.isoformat().replace("+00:00", "Z"),
        "finished_at_utc": finished_at.isoformat().replace("+00:00", "Z"),
        "duration_seconds": (finished_at - started_at).total_seconds(),
        "git_commit": _git_commit(short=False),
        "manifest_path": str(manifest_path),
        "export": {
            "output_path": str(export_output),
            "command": list(export_command),
            "command_display": _format_command(export_command),
            "log_path": str(export_log),
        },
        "eval": {
            "output_dir": str(eval_dir),
            "command": list(eval_command),
            "command_display": _format_command(eval_command),
            "log_path": str(eval_log),
        },
        "error": error,
    }


def _build_manifest_payload(
    *,
    summary: dict[str, Any],
    args: argparse.Namespace,
    manifest_path: Path,
    baseline_eval_dir: Path,
    baseline_predictions_path: Path,
) -> dict[str, Any]:
    return {
        "run_id": summary["run_id"],
        "scope": summary.get("scope"),
        "manifest_path": str(manifest_path),
        "baseline_eval_dir": str(baseline_eval_dir),
        "baseline_predictions_path": str(baseline_predictions_path),
        "output_root": summary["output_root"],
        "requested_seeds": summary.get("requested_seeds", []),
        "command": {
            "device": args.device,
            "model_size": args.model_size,
            "input_size": args.input_size,
            "patch_size": args.patch_size,
            "batch_size": args.batch_size,
            "num_workers": args.num_workers,
            "threshold": args.threshold,
            "hf_model_repo": args.hf_model_repo,
            "local_module_config": str(Path(args.local_module_config).resolve()),
            "progress_every": args.progress_every,
        },
    }


def _validate_reference(reference: dict[str, Any], manifest_path: Path) -> None:
    if reference.get("evaluation_scope") != "restricted_pilot":
        raise ValueError(
            f"Baseline reference scope must be restricted_pilot, got {reference.get('evaluation_scope')!r}"
        )
    if reference.get("sample_count") is None:
        raise ValueError("Baseline reference is missing sample_count")
    if not Path(reference["summary_path"]).exists():
        raise ValueError(f"Baseline summary missing: {reference['summary_path']}")
    if not Path(reference["localized_summary_path"]).exists():
        raise ValueError(f"Baseline localized summary missing: {reference['localized_summary_path']}")
    if not manifest_path.exists():
        raise ValueError(f"Manifest does not exist: {manifest_path}")


def _status_from_seed_runs(seed_runs: list[dict[str, Any]]) -> dict[str, Any]:
    successful = [run for run in seed_runs if run["status"] == "success"]
    failed = [run for run in seed_runs if run["status"] != "success"]
    return {
        "total_seeds": len(seed_runs),
        "successful_seeds": len(successful),
        "failed_seeds": len(failed),
        "failed_seed_ids": [run["seed"] for run in failed],
    }


def _run_command(
    command: Sequence[str],
    *,
    log_path: Path,
    cwd: Path,
    prefix: str,
) -> None:
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as log_handle:
        process = subprocess.Popen(
            list(command),
            cwd=str(cwd),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert process.stdout is not None
        for line in process.stdout:
            log_handle.write(line)
            log_handle.flush()
            print(f"[{prefix}] {line.rstrip()}", flush=True)
        returncode = process.wait()
    if returncode != 0:
        raise subprocess.CalledProcessError(returncode, list(command))


def _make_run_id(output_root: Path) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    sha = _git_commit(short=True)
    base = f"m4_multi_seed_{timestamp}_{sha}"
    candidate = base
    suffix = 1
    while (output_root / candidate).exists():
        candidate = f"{base}_{suffix:02d}"
        suffix += 1
    return candidate


def _parse_seeds(raw: str) -> list[int]:
    seeds = []
    for chunk in raw.split(","):
        value = chunk.strip()
        if not value:
            continue
        seeds.append(int(value))
    if not seeds:
        raise ValueError("At least one seed must be provided")
    return seeds


def _git_commit(*, short: bool) -> str:
    command = ["git", "rev-parse", "--short" if short else "HEAD"]
    result = subprocess.run(
        command,
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    )
    value = result.stdout.strip()
    return value or "unknown"


def _format_command(command: Sequence[str]) -> str:
    if os.name == "nt":
        return subprocess.list2cmdline(list(command))
    return shlex.join(list(command))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _read_tail(path: Path, lines: int = 20) -> str:
    if not path.exists():
        return ""
    content = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    if not content:
        return ""
    return "\n".join(content[-lines:])


if __name__ == "__main__":
    raise SystemExit(main())
