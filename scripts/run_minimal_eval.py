from __future__ import annotations

import argparse
import sys
from pathlib import Path

from aigc_detection.eval import run_minimal_eval


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the minimal M1 evaluation pipeline on a local mirror subset."
    )
    parser.add_argument("--manifest", required=True, help="Path to the local mirror manifest (.jsonl).")
    parser.add_argument(
        "--predictions",
        required=True,
        help="Path to the per-sample prediction scores (.jsonl).",
    )
    parser.add_argument("--output-dir", required=True, help="Directory for evaluation artifacts.")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Decision threshold used for accuracy and fake_recall.",
    )
    args = parser.parse_args(argv)

    command = f"{Path(sys.executable).name} " + " ".join(sys.argv)
    artifacts = run_minimal_eval(
        manifest_path=Path(args.manifest),
        predictions_path=Path(args.predictions),
        output_dir=Path(args.output_dir),
        threshold=args.threshold,
        command=command,
    )

    print(f"Minimal evaluation artifacts written to: {artifacts.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
