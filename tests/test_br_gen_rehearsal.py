from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from aigc_detection.data import load_manifest
from aigc_detection.data.br_gen import BRGenPreparationError, prepare_br_gen_rehearsal


class BRGenRehearsalTests(unittest.TestCase):
    def test_prepare_br_gen_rehearsal_writes_manifest_and_predictions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            source_root = root / "BR-Gen"
            forged = source_root / "Forged" / "BrushNet" / "Background" / "COCO"
            mask = source_root / "Mask" / "Background" / "COCO"
            forged.mkdir(parents=True)
            mask.mkdir(parents=True)

            forged_path = forged / "000000000034_background.png"
            mask_path = mask / "000000000034_background.png"
            forged_path.write_text("forged", encoding="utf-8")
            mask_path.write_text("mask", encoding="utf-8")

            output_root = root / "mirrored" / "br_gen" / "subsets" / "rehearsal"
            artifacts = prepare_br_gen_rehearsal(source_root, output_root)

            self.assertEqual(artifacts.sample_count, 1)
            self.assertEqual(artifacts.skipped_missing_mask_count, 0)
            self.assertTrue(artifacts.manifest_path.exists())
            self.assertTrue(artifacts.predictions_path.exists())

            manifest_record = json.loads(
                artifacts.manifest_path.read_text(encoding="utf-8").strip()
            )
            self.assertEqual(manifest_record["task_type"], "localized_edit")
            self.assertEqual(manifest_record["label"], 1)
            self.assertEqual(manifest_record["generator_id"], "BrushNet")
            self.assertEqual(manifest_record["region_type"], "background")

            loaded_samples = load_manifest(artifacts.manifest_path)
            self.assertEqual(len(loaded_samples), 1)
            self.assertTrue(loaded_samples[0].image_path.exists())
            self.assertTrue(loaded_samples[0].mask_path.exists())

    def test_prepare_br_gen_rehearsal_raises_when_no_records_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            source_root = root / "BR-Gen"
            (source_root / "Forged").mkdir(parents=True)
            (source_root / "Mask").mkdir(parents=True)

            with self.assertRaises(BRGenPreparationError):
                prepare_br_gen_rehearsal(source_root, root / "out")


if __name__ == "__main__":
    unittest.main()
