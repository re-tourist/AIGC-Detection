from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from aigc_detection.data import NormalizedSample
from aigc_detection.eval import build_protocol_alignment_bundle, write_protocol_alignment_artifacts


def _write_rgb_image(path: Path, color: tuple[int, int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (10, 10), color=color).save(path)


def _write_mask(path: Path, active_pixels: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("L", (10, 10), color=0)
    for index in range(active_pixels):
        x = index % 10
        y = index // 10
        image.putpixel((x, y), 255)
    image.save(path)


def _make_sample(
    *,
    root: Path,
    sample_id: str,
    label: int,
    generator_id: str | None,
    degradation: str | None,
    region_type: str,
    active_pixels: int | None,
) -> NormalizedSample:
    image_path = root / "images" / f"{sample_id}.png"
    _write_rgb_image(image_path, (12, 34, 56))
    mask_path = None
    if active_pixels is not None:
        mask_path = root / "masks" / f"{sample_id}.png"
        _write_mask(mask_path, active_pixels)
    return NormalizedSample(
        sample_id=sample_id,
        task_type="localized_edit",
        split="holdout",
        image_path=image_path,
        label=label,
        mask_path=mask_path,
        generator_id=generator_id,
        source_id="COCO",
        degradation=degradation,
        region_type=region_type,
        meta={"evaluation_scope": "restricted_pilot"},
    )


def _find_row(
    rows: list[dict[str, object]],
    *,
    dimension: str,
    slice_value: str,
) -> dict[str, object]:
    for row in rows:
        if row["dimension"] == dimension and row["slice_value"] == slice_value:
            return row
    raise AssertionError(f"Missing row for {dimension}={slice_value}")


class ProtocolAlignmentTests(unittest.TestCase):
    def test_protocol_alignment_outputs_exclusions_na_and_deferred_iou(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            samples = [
                _make_sample(
                    root=root,
                    sample_id="real_clean",
                    label=0,
                    generator_id=None,
                    degradation="clean",
                    region_type="background",
                    active_pixels=None,
                ),
                _make_sample(
                    root=root,
                    sample_id="fake_clean_diffusion",
                    label=1,
                    generator_id="BrushNet",
                    degradation="clean",
                    region_type="background",
                    active_pixels=4,
                ),
                _make_sample(
                    root=root,
                    sample_id="fake_clean_unknown",
                    label=1,
                    generator_id=None,
                    degradation="clean",
                    region_type="stuff",
                    active_pixels=10,
                ),
                _make_sample(
                    root=root,
                    sample_id="fake_clean_unsupported",
                    label=1,
                    generator_id="MysteryGen",
                    degradation="clean",
                    region_type="stuff",
                    active_pixels=25,
                ),
                _make_sample(
                    root=root,
                    sample_id="fake_jpeg_unsupported",
                    label=1,
                    generator_id="MysteryGen",
                    degradation="jpeg",
                    region_type="stuff",
                    active_pixels=10,
                ),
            ]
            scores = {
                "real_clean": 0.10,
                "fake_clean_diffusion": 0.90,
                "fake_clean_unknown": 0.80,
                "fake_clean_unsupported": 0.55,
                "fake_jpeg_unsupported": 0.55,
            }

            bundle = build_protocol_alignment_bundle(
                samples,
                scores,
                legacy_threshold=0.6,
                evaluation_scope="restricted_pilot",
            )
            artifacts = write_protocol_alignment_artifacts(root / "artifacts", bundle)

            overall_metrics = json.loads(artifacts.overall_metrics_path.read_text(encoding="utf-8"))
            slice_metrics = json.loads(artifacts.slice_metrics_json_path.read_text(encoding="utf-8"))
            audit_payload = json.loads(
                artifacts.protocol_alignment_audit_path.read_text(encoding="utf-8")
            )
            markdown = artifacts.paper_table_summary_path.read_text(encoding="utf-8")

            self.assertEqual(overall_metrics["legacy_threshold"], 0.6)
            self.assertEqual(overall_metrics["paper_style_threshold"], 0.5)
            self.assertAlmostEqual(overall_metrics["legacy_fake_recall_value"], 0.5)
            self.assertAlmostEqual(
                overall_metrics["paper_manipulated_recall_at_0_5"],
                1.0,
            )
            self.assertFalse(overall_metrics["legacy_equals_paper_manipulated_recall"])
            self.assertEqual(overall_metrics["iou"]["status"], "deferred")

            self.assertEqual(audit_payload["excluded_counts"]["unknown_generator_count"], 1)
            self.assertEqual(
                audit_payload["excluded_counts"]["unsupported_generator_count"],
                1,
            )
            self.assertEqual(
                audit_payload["excluded_counts"]["excluded_from_split_a_count"],
                2,
            )
            self.assertEqual(
                audit_payload["excluded_counts"]["excluded_generator_ids"],
                ["MysteryGen"],
            )

            rows = slice_metrics["rows"]
            gan_row = _find_row(rows, dimension="generator_family", slice_value="GAN")
            unknown_row = _find_row(rows, dimension="generator_family", slice_value="unknown")
            unsupported_row = _find_row(
                rows,
                dimension="generator_family",
                slice_value="unsupported",
            )
            jpeg_row = _find_row(rows, dimension="degradation_detail", slice_value="jpeg")
            resize_row = _find_row(rows, dimension="degradation_detail", slice_value="resize")

            self.assertEqual(gan_row["status"], "empty_slice")
            self.assertIsNone(gan_row["auroc"])
            self.assertEqual(unknown_row["status"], "excluded")
            self.assertFalse(unknown_row["included_in_paper_main_table"])
            self.assertEqual(unsupported_row["status"], "excluded")
            self.assertFalse(unsupported_row["included_in_paper_main_table"])
            self.assertEqual(jpeg_row["status"], "undefined_metric")
            self.assertIsNone(jpeg_row["auroc"])
            self.assertIsNone(jpeg_row["paper_real_recall_at_0_5"])
            self.assertIn("AUROC is undefined", " ".join(jpeg_row["notes"]))
            self.assertEqual(resize_row["status"], "empty_slice")
            self.assertIsNone(resize_row["accuracy"])

            with artifacts.slice_metrics_csv_path.open("r", encoding="utf-8", newline="") as handle:
                csv_rows = list(csv.DictReader(handle))

            csv_gan_row = _find_row(csv_rows, dimension="generator_family", slice_value="GAN")
            csv_jpeg_row = _find_row(
                csv_rows,
                dimension="degradation_detail",
                slice_value="jpeg",
            )
            self.assertEqual(csv_gan_row["auroc"], "N/A")
            self.assertEqual(csv_jpeg_row["paper_real_recall_at_0_5"], "N/A")
            self.assertEqual(csv_jpeg_row["legacy_equals_paper_manipulated_recall"], "False")

            self.assertIn("## Clean vs Degraded", markdown)
            self.assertIn("## Degradation Detail", markdown)
            self.assertIn("IoU: `N/A (deferred)`", markdown)
            self.assertNotIn("| unknown |", markdown)
            self.assertNotIn("| unsupported |", markdown)


if __name__ == "__main__":
    unittest.main()
