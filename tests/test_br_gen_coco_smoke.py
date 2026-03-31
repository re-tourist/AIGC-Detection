from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from aigc_detection.data.br_gen_cf_smoke import prepare_br_gen_coco_smoke


def _write_image(path: Path, color: tuple[int, int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (8, 8), color).save(path)


class BRGenCocoSmokeTests(unittest.TestCase):
    def test_prepares_balanced_coco_smoke_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            source_root = root / "BR-Gen"
            manifest_dir = root / "rehearsal" / "manifest"
            manifest_dir.mkdir(parents=True)

            fake_coco_a = source_root / "Forged" / "BrushNet" / "Background" / "COCO" / "fake_a.png"
            fake_coco_b = source_root / "Forged" / "LaMa" / "Stuff" / "COCO" / "fake_b.png"
            fake_imagenet = (
                source_root / "Forged" / "BrushNet" / "Background" / "ImageNet" / "fake_c.png"
            )
            _write_image(fake_coco_a, (255, 0, 0))
            _write_image(fake_coco_b, (0, 255, 0))
            _write_image(fake_imagenet, (0, 0, 255))

            real_list_path = source_root / "RealImage" / "COCO" / "COCO_image_list.txt"
            real_list_path.parent.mkdir(parents=True, exist_ok=True)
            real_filenames = [
                "000000000001.jpg",
                "000000000002.jpg",
                "000000000003.jpg",
            ]
            real_list_path.write_text("\n".join(real_filenames) + "\n", encoding="utf-8")

            manifest_path = manifest_dir / "manifest.jsonl"
            manifest_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "sample_id": "sample_coco_a",
                                "task_type": "localized_edit",
                                "split": "rehearsal",
                                "image_path": os.path.relpath(fake_coco_a, manifest_dir),
                                "label": 1,
                                "mask_path": os.path.relpath(fake_coco_a, manifest_dir),
                                "generator_id": "BrushNet",
                                "source_id": "COCO",
                                "meta": {"source_drop_root": str(source_root)},
                            }
                        ),
                        json.dumps(
                            {
                                "sample_id": "sample_coco_b",
                                "task_type": "localized_edit",
                                "split": "rehearsal",
                                "image_path": os.path.relpath(fake_coco_b, manifest_dir),
                                "label": 1,
                                "mask_path": os.path.relpath(fake_coco_b, manifest_dir),
                                "generator_id": "LaMa",
                                "source_id": "COCO",
                                "meta": {"source_drop_root": str(source_root)},
                            }
                        ),
                        json.dumps(
                            {
                                "sample_id": "sample_imagenet",
                                "task_type": "localized_edit",
                                "split": "rehearsal",
                                "image_path": os.path.relpath(fake_imagenet, manifest_dir),
                                "label": 1,
                                "mask_path": os.path.relpath(fake_imagenet, manifest_dir),
                                "generator_id": "BrushNet",
                                "source_id": "ImageNet",
                                "meta": {"source_drop_root": str(source_root)},
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            download_source = root / "download_source"
            download_source.mkdir(parents=True)
            for filename, color in zip(real_filenames, [(240, 240, 240), (220, 220, 220), (200, 200, 200)]):
                _write_image(download_source / filename, color)

            output_root = root / "cf_smoke"

            def fake_download_with_fallback(
                *,
                relative_path: str,
                dest_path: Path,
                base_urls: tuple[str, ...],
                timeout_seconds: float = 20.0,
            ):
                from aigc_detection.data.coco_download import DownloadAttemptResult

                filename = Path(relative_path).name
                shutil.copy2(download_source / filename, dest_path)
                return DownloadAttemptResult(
                    status="downloaded",
                    source_url=f"{base_urls[0].rstrip('/')}/{relative_path}",
                    reason=None,
                )

            with patch(
                "aigc_detection.data.br_gen_cf_smoke.download_with_fallback",
                side_effect=fake_download_with_fallback,
            ):
                artifacts = prepare_br_gen_coco_smoke(
                    manifest_path=manifest_path,
                    source_root=source_root,
                    output_root=output_root,
                    source_dataset="COCO",
                    real_image_download_base_url="https://images.cocodataset.org/train2017",
                )

            self.assertEqual(artifacts.copied_real_count, 2)
            self.assertEqual(artifacts.copied_fake_count, 2)

            real_files = sorted((output_root / "COCO" / "real").glob("*.jpg"))
            fake_files = sorted((output_root / "COCO" / "fake").glob("*.png"))
            self.assertEqual(len(real_files), 2)
            self.assertEqual(len(fake_files), 2)
            self.assertTrue((output_root / "README.md").exists())
            self.assertTrue((output_root / "manifest.jsonl").exists())
            self.assertTrue((output_root / "selection.jsonl").exists())

            manifest = (output_root / "manifest.jsonl").read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(manifest), 4)
            self.assertTrue(any('"label": 0' in line for line in manifest))
            self.assertTrue(any('"label": 1' in line for line in manifest))

            selection = (output_root / "selection.jsonl").read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(selection), 4)
            self.assertTrue(any('"kind": "real"' in line for line in selection))
            self.assertTrue(any('"kind": "fake"' in line for line in selection))


if __name__ == "__main__":
    unittest.main()
