from __future__ import annotations

import json
import statistics
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

NUMERIC_METRICS = (
    "overall_accuracy",
    "overall_auroc",
    "overall_fake_recall",
    "background_fake_recall",
    "stuff_fake_recall",
    "small_fake_recall",
    "medium_fake_recall",
    "large_fake_recall",
)


def load_reference_artifacts(eval_dir: str | Path) -> dict[str, Any]:
    eval_dir = Path(eval_dir).resolve()
    summary = _read_json(eval_dir / "summary.json")
    localized = _read_json(eval_dir / "localized_failure_summary.json")
    extracted = _extract_metrics(summary, localized)
    return {
        "evaluation_scope": summary.get("evaluation_scope"),
        "sample_count": summary.get("inputs", {}).get("sample_count"),
        "summary_path": str(eval_dir / "summary.json"),
        "localized_summary_path": str(eval_dir / "localized_failure_summary.json"),
        "overall": extracted["overall"],
        "slices": extracted["slices"],
        "subtlety": extracted["subtlety"],
        "slice_support": _extract_slice_support(localized),
    }


def load_seed_metrics(eval_dir: str | Path) -> dict[str, Any]:
    eval_dir = Path(eval_dir).resolve()
    summary = _read_json(eval_dir / "summary.json")
    localized = _read_json(eval_dir / "localized_failure_summary.json")
    extracted = _extract_metrics(summary, localized)
    return {
        "evaluation_scope": summary.get("evaluation_scope"),
        "sample_count": summary.get("inputs", {}).get("sample_count"),
        "summary_path": str(eval_dir / "summary.json"),
        "localized_summary_path": str(eval_dir / "localized_failure_summary.json"),
        "overall": extracted["overall"],
        "slices": extracted["slices"],
        "subtlety": extracted["subtlety"],
    }


def aggregate_seed_audit(
    *,
    run_id: str,
    manifest_path: str | Path,
    output_root: str | Path,
    reference: Mapping[str, Any],
    seed_runs: Sequence[Mapping[str, Any]],
    baseline_eval_dir: str | Path,
    baseline_predictions_path: str | Path,
) -> dict[str, Any]:
    successful_runs = [run for run in seed_runs if run.get("status") == "success"]
    failed_runs = [run for run in seed_runs if run.get("status") != "success"]
    if not successful_runs:
        raise ValueError("Cannot aggregate multi-seed audit without a successful seed.")

    numeric_metrics: dict[str, Any] = {}
    for metric_name in NUMERIC_METRICS:
        baseline_value = _metric_value(reference, metric_name)
        seed_values = [_metric_value(run["metrics"], metric_name) for run in successful_runs]
        numeric_metrics[metric_name] = _summarize_numeric_series(baseline_value, seed_values)

    subtlety_values = [run["metrics"]["subtlety"]["status"] for run in successful_runs]
    subtlety_counts = dict(sorted(Counter(subtlety_values).items()))
    return {
        "run_id": run_id,
        "scope": reference.get("evaluation_scope"),
        "manifest_path": str(Path(manifest_path).resolve()),
        "output_root": str(Path(output_root).resolve()),
        "baseline": {
            "eval_dir": str(Path(baseline_eval_dir).resolve()),
            "predictions_path": str(Path(baseline_predictions_path).resolve()),
            "reference": reference,
        },
        "seed_runs": list(seed_runs),
        "status": {
            "total_seeds": len(seed_runs),
            "successful_seeds": len(successful_runs),
            "failed_seeds": len(failed_runs),
            "failed_seed_ids": [run.get("seed") for run in failed_runs],
        },
        "aggregate": {
            "numeric_metrics": numeric_metrics,
            "subtlety": {
                "baseline": reference["subtlety"]["status"],
                "local_statuses": subtlety_values,
                "local_status_counts": subtlety_counts,
                "all_same": len(subtlety_counts) == 1,
            },
        },
    }


def render_aggregate_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# M4 Multi-Seed Local Probe Audit",
        "",
        f"- Run ID: `{summary['run_id']}`",
        f"- Scope: `{summary.get('scope')}`",
        f"- Manifest: `{summary['manifest_path']}`",
        f"- Output root: `{summary['output_root']}`",
        f"- Successful seeds: `{summary['status']['successful_seeds']}` / `{summary['status']['total_seeds']}`",
        f"- Failed seeds: `{summary['status']['failed_seeds']}`",
        "",
        "## Baseline Reference",
        f"- Baseline eval dir: `{summary['baseline']['eval_dir']}`",
        f"- Baseline predictions: `{summary['baseline']['predictions_path']}`",
        f"- Baseline evaluation scope: `{summary['baseline']['reference']['evaluation_scope']}`",
        f"- Baseline sample count: `{summary['baseline']['reference']['sample_count']}`",
        "",
        "## Aggregate Metrics",
        "| Metric | Baseline | Local mean | Delta mean | Local std | Local min | Local max | Improved seeds |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for metric_name in NUMERIC_METRICS:
        metric = summary["aggregate"]["numeric_metrics"][metric_name]
        lines.append(
            "| {metric} | {baseline:.6f} | {mean:.6f} | {delta:.6f} | {std:.6f} | {minv:.6f} | {maxv:.6f} | {improved}/{total} |".format(
                metric=metric_name,
                baseline=metric["baseline"],
                mean=metric["local_mean"],
                delta=metric["delta_mean"],
                std=metric["local_std"],
                minv=metric["local_min"],
                maxv=metric["local_max"],
                improved=metric["improved_seed_count"],
                total=metric["seed_count"],
            )
        )

    subtlety = summary["aggregate"]["subtlety"]
    lines.extend(
        [
            "",
            "## Subtlety Status",
            f"- Baseline: `{subtlety['baseline']}`",
            f"- Local statuses: `{subtlety['local_statuses']}`",
            f"- Status counts: `{subtlety['local_status_counts']}`",
            f"- All same: `{subtlety['all_same']}`",
            "",
            "## Seed Outcomes",
        ]
    )
    for run in summary["seed_runs"]:
        lines.append(
            f"- seed `{run['seed']}`: `{run['status']}`"
            + (f" ({run.get('error')})" if run.get("error") else "")
        )
    return "\n".join(lines) + "\n"


def render_run_status_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# M4 Multi-Seed Run Status",
        "",
        f"- Run ID: `{summary['run_id']}`",
        f"- Scope: `{summary.get('scope')}`",
        f"- Manifest: `{summary['manifest_path']}`",
        f"- Output root: `{summary['output_root']}`",
        "",
        "## Seed Table",
        "| Seed | Status | Export | Eval | Duration (s) | Error | Output dir |",
        "| --- | --- | --- | --- | ---: | --- | --- |",
    ]
    for run in summary["seed_runs"]:
        stages = run.get("stages", {})
        lines.append(
            "| {seed} | {status} | {export} | {eval_status} | {duration:.2f} | {error} | `{output_dir}` |".format(
                seed=run["seed"],
                status=run["status"],
                export=stages.get("export", "-"),
                eval_status=stages.get("eval", "-"),
                duration=float(run.get("duration_seconds", 0.0) or 0.0),
                error=(run.get("error") or "-").replace("\n", " "),
                output_dir=run["output_dir"],
            )
        )

    lines.extend(
        [
            "",
            "## Aggregate",
            f"- Successful seeds: `{summary['status']['successful_seeds']}`",
            f"- Failed seeds: `{summary['status']['failed_seeds']}`",
            f"- Failed seed IDs: `{summary['status']['failed_seed_ids']}`",
        ]
    )
    return "\n".join(lines) + "\n"


def _extract_metrics(summary: Mapping[str, Any], localized: Mapping[str, Any]) -> dict[str, Any]:
    overall = dict(summary.get("report", {}).get("overall", {}).get("metrics", {}))
    return {
        "overall": overall,
        "slices": {
            "background": dict(localized["by_region_type"]["groups"]["background"]),
            "stuff": dict(localized["by_region_type"]["groups"]["stuff"]),
            "small": dict(localized["by_edit_area_ratio"]["groups"]["small"]),
            "medium": dict(localized["by_edit_area_ratio"]["groups"]["medium"]),
            "large": dict(localized["by_edit_area_ratio"]["groups"]["large"]),
        },
        "subtlety": dict(localized.get("subtlety", {})),
    }


def _extract_slice_support(localized: Mapping[str, Any]) -> dict[str, Any]:
    def _support(group: Mapping[str, Any]) -> dict[str, Any]:
        support = dict(group.get("support", {}))
        return {
            "sample_count": group.get("sample_count"),
            "low_support": support.get("low_support"),
            "low_support_reasons": support.get("low_support_reasons", []),
        }

    return {
        "background": _support(localized["by_region_type"]["groups"]["background"]),
        "stuff": _support(localized["by_region_type"]["groups"]["stuff"]),
        "small": _support(localized["by_edit_area_ratio"]["groups"]["small"]),
        "medium": _support(localized["by_edit_area_ratio"]["groups"]["medium"]),
        "large": _support(localized["by_edit_area_ratio"]["groups"]["large"]),
        "subtlety": dict(localized.get("subtlety", {})),
    }


def _metric_value(metrics: Mapping[str, Any], metric_name: str) -> float | str:
    if metric_name.startswith("overall_"):
        return float(metrics["overall"][metric_name.removeprefix("overall_")])
    if metric_name.endswith("_fake_recall"):
        slice_name = metric_name.removesuffix("_fake_recall")
        return float(metrics["slices"][slice_name]["metrics"]["fake_recall"])
    raise KeyError(f"Unsupported metric name: {metric_name}")


def _summarize_numeric_series(baseline: float, values: Sequence[float]) -> dict[str, Any]:
    local_values = [float(value) for value in values]
    if not local_values:
        raise ValueError("Cannot summarize an empty metric series.")
    improved = sum(1 for value in local_values if value > baseline)
    worsened = sum(1 for value in local_values if value < baseline)
    unchanged = len(local_values) - improved - worsened
    local_mean = statistics.fmean(local_values)
    local_std = statistics.stdev(local_values) if len(local_values) > 1 else 0.0
    return {
        "baseline": float(baseline),
        "local_values": local_values,
        "local_mean": local_mean,
        "delta_mean": local_mean - baseline,
        "local_std": local_std,
        "local_min": min(local_values),
        "local_max": max(local_values),
        "seed_count": len(local_values),
        "improved_seed_count": improved,
        "worsened_seed_count": worsened,
        "unchanged_seed_count": unchanged,
        "improved_fraction": improved / len(local_values),
    }


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing audit artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))
