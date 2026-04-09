from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from aigc_detection.eval.m3_runner import run_m3_formal_eval


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the M3 localized-failure sidecar report on top of the current minimal runner."
    )
    parser.add_argument("--manifest", required=True, help="Path to the M3 formal manifest JSONL.")
    parser.add_argument(
        "--predictions",
        required=True,
        help="Path to repo-compatible prediction JSONL for the same manifest.",
    )
    parser.add_argument("--output-dir", required=True, help="Directory for M3 evaluation artifacts.")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Decision threshold used for accuracy and fake_recall.",
    )
    args = parser.parse_args(argv)

    command = f"{Path(sys.executable).name} " + " ".join(sys.argv)
    artifacts = run_m3_formal_eval(
        manifest_path=Path(args.manifest),
        predictions_path=Path(args.predictions),
        output_dir=Path(args.output_dir),
        threshold=args.threshold,
        command=command,
    )

    print(f"Minimal evaluation artifacts written to: {artifacts.base_artifacts.output_dir}")
    print(f"Localized failure summary: {artifacts.localized_summary_path}")
    print(f"Localized failure metrics: {artifacts.localized_metrics_csv_path}")
    print(f"Localized failure report: {artifacts.localized_report_path}")
    print(f"Localized coverage summary: {artifacts.localized_coverage_summary_path}")
    print(f"Coverage audit: {artifacts.coverage_audit_path}")
    print(f"Failure evidence map: {artifacts.failure_evidence_map_path}")
    print(f"Overall protocol-alignment metrics: {artifacts.overall_metrics_path}")
    print(f"Slice protocol-alignment metrics JSON: {artifacts.slice_metrics_json_path}")
    print(f"Slice protocol-alignment metrics CSV: {artifacts.slice_metrics_csv_path}")
    print(f"Paper-style summary: {artifacts.paper_table_summary_path}")
    print(f"Protocol-alignment audit: {artifacts.protocol_alignment_audit_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
