from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from aigc_detection.adapters.community_forensics import (
    CommunityForensicsAdapterError,
    adapt_community_forensics_predictions,
)
from aigc_detection.eval import load_prediction_scores


class CommunityForensicsAdapterTests(unittest.TestCase):
    def test_relative_path_alignment_writes_repo_prediction_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            manifest_dir = root / "rehearsal" / "manifest"
            image_dir = manifest_dir / "images"
            mask_dir = manifest_dir / "masks"
            image_dir.mkdir(parents=True)
            mask_dir.mkdir(parents=True)

            (image_dir / "fake_a.jpg").write_text("image", encoding="utf-8")
            (image_dir / "real_a.jpg").write_text("image", encoding="utf-8")
            (mask_dir / "fake_a.mask").write_text("mask", encoding="utf-8")

            manifest_path = manifest_dir / "manifest.jsonl"
            manifest_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "sample_id": "sample_fake",
                                "task_type": "localized_edit",
                                "split": "rehearsal",
                                "image_path": "images/fake_a.jpg",
                                "label": 1,
                                "mask_path": "masks/fake_a.mask",
                                "degradation": "clean",
                                "region_type": "background",
                                "subtlety": "subtle",
                            }
                        ),
                        json.dumps(
                            {
                                "sample_id": "sample_real",
                                "task_type": "full_image_fake",
                                "split": "rehearsal",
                                "image_path": "images/real_a.jpg",
                                "label": 0,
                                "degradation": "clean",
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            input_path = root / "community_forensics_predictions.jsonl"
            input_path.write_text(
                "\n".join(
                    [
                        json.dumps({"image_path": "images/fake_a.jpg", "score": 0.10}),
                        json.dumps({"image_path": "./images/real_a.jpg", "score": 0.90}),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            output_path = root / "repo_predictions.jsonl"
            artifacts = adapt_community_forensics_predictions(
                manifest_path=manifest_path,
                input_path=input_path,
                output_path=output_path,
                alignment_strategy="relative_path",
                score_transform="one_minus",
                input_path_field="image_path",
            )

            self.assertEqual(artifacts.sample_count, 2)
            scores = load_prediction_scores(output_path)
            self.assertAlmostEqual(scores["sample_fake"], 0.9)
            self.assertAlmostEqual(scores["sample_real"], 0.1)

    def test_mapping_table_alignment_is_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            manifest_dir = root / "rehearsal" / "manifest"
            image_dir = manifest_dir / "images"
            mask_dir = manifest_dir / "masks"
            image_dir.mkdir(parents=True)
            mask_dir.mkdir(parents=True)

            (image_dir / "a.jpg").write_text("image", encoding="utf-8")
            (mask_dir / "a.mask").write_text("mask", encoding="utf-8")

            manifest_path = manifest_dir / "manifest.jsonl"
            manifest_path.write_text(
                json.dumps(
                    {
                        "sample_id": "repo_sample",
                        "task_type": "localized_edit",
                        "split": "rehearsal",
                        "image_path": "images/a.jpg",
                        "label": 1,
                        "mask_path": "masks/a.mask",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            mapping_table = root / "mapping.jsonl"
            mapping_table.write_text(
                json.dumps({"source_id": "community_001", "sample_id": "repo_sample"}) + "\n",
                encoding="utf-8",
            )

            input_path = root / "predictions.jsonl"
            input_path.write_text(
                json.dumps({"source_id": "community_001", "score": 0.77}) + "\n",
                encoding="utf-8",
            )

            output_path = root / "repo_predictions.jsonl"
            adapt_community_forensics_predictions(
                manifest_path=manifest_path,
                input_path=input_path,
                output_path=output_path,
                alignment_strategy="mapping_table",
                mapping_table_path=mapping_table,
                mapping_source_id_field="source_id",
            )

            scores = load_prediction_scores(output_path)
            self.assertAlmostEqual(scores["repo_sample"], 0.77)

    def test_sample_id_alignment_rejects_heuristic_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            manifest_dir = root / "rehearsal" / "manifest"
            image_dir = manifest_dir / "images"
            image_dir.mkdir(parents=True)
            (image_dir / "a.jpg").write_text("image", encoding="utf-8")

            manifest_path = manifest_dir / "manifest.jsonl"
            manifest_path.write_text(
                json.dumps(
                    {
                        "sample_id": "repo_sample",
                        "task_type": "full_image_fake",
                        "split": "rehearsal",
                        "image_path": "images/a.jpg",
                        "label": 1,
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            input_path = root / "predictions.jsonl"
            input_path.write_text(
                json.dumps({"score": 0.5}) + "\n",
                encoding="utf-8",
            )

            with self.assertRaises(CommunityForensicsAdapterError):
                adapt_community_forensics_predictions(
                    manifest_path=manifest_path,
                    input_path=input_path,
                    output_path=root / "repo_predictions.jsonl",
                    alignment_strategy="sample_id",
                )


if __name__ == "__main__":
    unittest.main()
