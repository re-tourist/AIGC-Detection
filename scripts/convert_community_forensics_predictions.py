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

from aigc_detection.adapters.community_forensics import (
    adapt_community_forensics_predictions,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert Community Forensics predictions into the repo prediction JSONL contract."
    )
    parser.add_argument("--manifest", required=True, help="Path to the BR-Gen rehearsal manifest.")
    parser.add_argument("--input", required=True, help="Community Forensics prediction JSONL.")
    parser.add_argument("--output", required=True, help="Output prediction JSONL path.")
    parser.add_argument(
        "--alignment-strategy",
        choices=("sample_id", "relative_path", "mapping_table"),
        default="sample_id",
        help="Frozen sample alignment strategy.",
    )
    parser.add_argument(
        "--mapping-table",
        default=None,
        help="Explicit source_id -> sample_id mapping JSONL for mapping_table alignment.",
    )
    parser.add_argument(
        "--score-transform",
        choices=("identity", "sigmoid", "one_minus", "negate"),
        default="identity",
        help="Frozen score conversion rule that ensures higher means more likely fake.",
    )
    parser.add_argument(
        "--input-sample-id-field",
        default="sample_id",
        help="Source field used when alignment-strategy is sample_id.",
    )
    parser.add_argument(
        "--input-path-field",
        default="image_path",
        help="Source field used when alignment-strategy is relative_path.",
    )
    parser.add_argument(
        "--mapping-source-id-field",
        default="source_id",
        help="Source field used when alignment-strategy is mapping_table.",
    )
    parser.add_argument(
        "--score-field",
        default="score",
        help="Source field containing the Community Forensics score.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    artifacts = adapt_community_forensics_predictions(
        manifest_path=Path(args.manifest),
        input_path=Path(args.input),
        output_path=Path(args.output),
        alignment_strategy=args.alignment_strategy,
        mapping_table_path=Path(args.mapping_table) if args.mapping_table else None,
        score_transform=args.score_transform,
        input_sample_id_field=args.input_sample_id_field,
        input_path_field=args.input_path_field,
        mapping_source_id_field=args.mapping_source_id_field,
        score_field=args.score_field,
    )
    print(f"Output: {artifacts.output_path}")
    print(f"Samples: {artifacts.sample_count}")
    print(f"Alignment: {artifacts.alignment_strategy}")
    print(f"Score transform: {artifacts.score_transform}")


if __name__ == "__main__":
    main()
