from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepare the temporary BR-Gen COCO smoke fixture, export Community Forensics scores, and run the minimal repo eval."
    )
    parser.add_argument(
        "--smoke-root",
        default="data/tmp/cf_smoke",
        help="Temporary smoke root that will be rebuilt from scratch.",
    )
    parser.add_argument(
        "--manifest",
        default="data/mirrored/br_gen/subsets/rehearsal/manifest/manifest.jsonl",
        help="BR-Gen rehearsal manifest used for source selection.",
    )
    parser.add_argument(
        "--source-root",
        default="data/BR-Gen",
        help="Local BR-Gen source drop.",
    )
    parser.add_argument(
        "--hf-model-repo",
        default="external/Community-Forensics/weights/commfor-model-384",
        help="Local or Hugging Face model repository used by Community Forensics.",
    )
    parser.add_argument("--model-size", default="small", choices=("small", "tiny"))
    parser.add_argument("--input-size", type=int, default=384, choices=(224, 384))
    parser.add_argument("--patch-size", type=int, default=16, choices=(16, 32))
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument(
        "--device",
        default="auto",
        choices=("auto", "cpu", "cuda"),
        help="Inference device for the export step.",
    )
    parser.add_argument("--threshold", type=float, default=0.5)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    smoke_root = _resolve(args.smoke_root)
    manifest_path = _resolve(args.manifest)
    source_root = _resolve(args.source_root)
    predictions_path = smoke_root / "predictions.jsonl"
    evaluation_dir = smoke_root / "eval"
    feedback_path = smoke_root / "feedback.json"

    _run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "prepare_br_gen_coco_smoke.py"),
            "--manifest",
            str(manifest_path),
            "--source-root",
            str(source_root),
            "--output-root",
            str(smoke_root),
        ]
    )

    _run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "export_community_forensics_predictions.py"),
            "--manifest",
            str(smoke_root / "manifest.jsonl"),
            "--output",
            str(predictions_path),
            "--hf-model-repo",
            args.hf_model_repo,
            "--model-size",
            args.model_size,
            "--input-size",
            str(args.input_size),
            "--patch-size",
            str(args.patch_size),
            "--batch-size",
            str(args.batch_size),
            "--device",
            args.device,
        ]
    )

    _run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "run_minimal_eval.py"),
            "--manifest",
            str(smoke_root / "manifest.jsonl"),
            "--predictions",
            str(predictions_path),
            "--output-dir",
            str(evaluation_dir),
            "--threshold",
            str(args.threshold),
        ]
    )

    summary_path = evaluation_dir / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    feedback = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "smoke_root": str(smoke_root),
        "manifest_path": str(smoke_root / "manifest.jsonl"),
        "predictions_path": str(predictions_path),
        "evaluation_dir": str(evaluation_dir),
        "summary_path": str(summary_path),
        "metrics": summary["report"]["overall"]["metrics"],
        "sample_count": summary["inputs"]["sample_count"],
        "notes": [
            "Temporary smoke fixture; delete after validation.",
            "Upstream eval.py is optional and still Linux/GPU-only in this repository.",
        ],
    }
    feedback_path.write_text(json.dumps(feedback, indent=2, sort_keys=True), encoding="utf-8")

    print(f"Feedback: {feedback_path}")
    print(f"Manifest: {feedback['manifest_path']}")
    print(f"Predictions: {feedback['predictions_path']}")
    print(f"Eval dir: {feedback['evaluation_dir']}")
    return 0


def _resolve(path: str) -> Path:
    return Path(path).resolve()


def _run(command: list[str]) -> None:
    subprocess.run(command, cwd=REPO_ROOT, check=True)


if __name__ == "__main__":
    raise SystemExit(main())
