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

from aigc_detection.data.br_gen_cf_smoke import prepare_br_gen_coco_smoke


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare a Community Forensics smoke fixture from BR-Gen COCO source samples."
    )
    parser.add_argument(
        "--manifest",
        default="data/mirrored/br_gen/subsets/rehearsal/manifest/manifest.jsonl",
        help="Path to the BR-Gen rehearsal manifest used for source-id selection.",
    )
    parser.add_argument(
        "--source-root",
        default="data/BR-Gen",
        help="Path to the local BR-Gen source drop.",
    )
    parser.add_argument(
        "--output-root",
        default="data/tmp/cf_smoke",
        help="Path to the Community Forensics smoke output root.",
    )
    parser.add_argument(
        "--source-dataset",
        default="COCO",
        help="Source dataset label to mirror into the smoke fixture.",
    )
    parser.add_argument(
        "--real-image-list",
        default="",
        help="Optional override for the real-image list file.",
    )
    parser.add_argument(
        "--download-base-url",
        default="http://images.cocodataset.org/train2017",
        help="Base URL used to download the real images.",
    )
    args = parser.parse_args()

    artifacts = prepare_br_gen_coco_smoke(
        manifest_path=Path(args.manifest),
        source_root=Path(args.source_root),
        output_root=Path(args.output_root),
        source_dataset=args.source_dataset,
        real_image_list_path=Path(args.real_image_list) if args.real_image_list else None,
        real_image_download_base_url=args.download_base_url,
    )

    print(f"Output root: {artifacts.output_root}")
    print(f"Manifest: {artifacts.manifest_path}")
    print(f"Selection: {artifacts.selection_path}")
    print(f"Real copied: {artifacts.copied_real_count}")
    print(f"Fake copied: {artifacts.copied_fake_count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
