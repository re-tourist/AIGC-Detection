from __future__ import annotations

import argparse
from pathlib import Path

from aigc_detection.data.br_gen import prepare_br_gen_rehearsal


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare a BR-Gen rehearsal manifest and dummy predictions from a local source drop."
    )
    parser.add_argument(
        "--source-root",
        default="data/BR-Gen",
        help="Path to the local BR-Gen source drop.",
    )
    parser.add_argument(
        "--output-root",
        default="data/mirrored/br_gen/subsets/rehearsal",
        help="Path to the rehearsal subset output root.",
    )
    parser.add_argument(
        "--dummy-score",
        type=float,
        default=0.99,
        help="Dummy prediction score written for each generated sample.",
    )
    args = parser.parse_args()

    artifacts = prepare_br_gen_rehearsal(
        source_root=Path(args.source_root),
        output_root=Path(args.output_root),
        dummy_score=args.dummy_score,
    )

    print(f"Manifest: {artifacts.manifest_path}")
    print(f"Predictions: {artifacts.predictions_path}")
    print(f"Samples: {artifacts.sample_count}")
    print(f"Skipped missing masks: {artifacts.skipped_missing_mask_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
