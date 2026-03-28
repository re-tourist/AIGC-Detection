from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from aigc_detection.data import ManifestValidationError, load_manifest


FIXTURE_MANIFEST = (
    Path(__file__).resolve().parent / "fixtures" / "local_mirror" / "manifest.jsonl"
)


class ManifestLoaderTests(unittest.TestCase):
    def test_load_manifest_returns_normalized_samples(self) -> None:
        samples = load_manifest(FIXTURE_MANIFEST)
        self.assertEqual(len(samples), 6)
        self.assertEqual(samples[0].task_type, "localized_edit")
        self.assertEqual(samples[-1].task_type, "full_image_fake")
        self.assertTrue(samples[0].image_path.exists())
        self.assertEqual(samples[0].derived_fields, {})

    def test_full_image_compatibility_path_keeps_optional_fields_optional(self) -> None:
        samples = load_manifest(FIXTURE_MANIFEST)
        full_image_samples = [sample for sample in samples if sample.task_type == "full_image_fake"]
        self.assertEqual(len(full_image_samples), 2)
        self.assertIsNone(full_image_samples[0].mask_path)
        self.assertIsNone(full_image_samples[0].region_type)
        self.assertIsNone(full_image_samples[0].subtlety)

    def test_rejects_missing_required_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            image_path = tmp_path / "sample.jpg"
            image_path.write_text("placeholder", encoding="utf-8")
            manifest_path = tmp_path / "broken.jsonl"
            manifest_path.write_text(
                json.dumps(
                    {
                        "sample_id": "missing_label",
                        "task_type": "localized_edit",
                        "split": "smoke",
                        "image_path": image_path.name,
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(ManifestValidationError):
                load_manifest(manifest_path)

    def test_rejects_edit_area_ratio_as_raw_field(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            image_path = tmp_path / "sample.jpg"
            image_path.write_text("placeholder", encoding="utf-8")
            manifest_path = tmp_path / "broken.jsonl"
            manifest_path.write_text(
                json.dumps(
                    {
                        "sample_id": "derived_field_error",
                        "task_type": "localized_edit",
                        "split": "smoke",
                        "image_path": image_path.name,
                        "label": 1,
                        "edit_area_ratio": 0.3,
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(ManifestValidationError):
                load_manifest(manifest_path)


if __name__ == "__main__":
    unittest.main()
