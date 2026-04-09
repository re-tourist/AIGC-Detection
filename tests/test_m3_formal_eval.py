from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from aigc_detection.data.br_gen_formal import prepare_br_gen_formal_manifests
from aigc_detection.eval import run_m3_formal_eval
from aigc_detection.data import load_manifest


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


class M3FormalEvalTests(unittest.TestCase):
    def test_run_m3_formal_eval_writes_sidecar_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            source_root = root / "BR-Gen"

            for sample_id, color in (
                ("000000000001", (12, 34, 56)),
                ("000000000002", (22, 44, 66)),
                ("000000000003", (32, 54, 76)),
            ):
                _write_rgb_image(source_root / "Real" / "COCO" / f"{sample_id}.jpg", color)

            _write_rgb_image(
                source_root / "Forged" / "BrushNet" / "Background" / "COCO" / "000000000001_background.png",
                (200, 10, 10),
            )
            _write_mask(
                source_root / "Mask" / "Background" / "COCO" / "000000000001_background.png",
                active_pixels=4,
            )
            _write_rgb_image(
                source_root / "Forged" / "LaMa" / "Stuff" / "COCO" / "000000000002_stuff.png",
                (10, 200, 10),
            )
            _write_mask(
                source_root / "Mask" / "Stuff" / "COCO" / "000000000002_stuff.png",
                active_pixels=10,
            )
            _write_rgb_image(
                source_root / "Forged" / "BrushNet" / "Background" / "COCO" / "000000000003_background.png",
                (10, 10, 200),
            )
            _write_mask(
                source_root / "Mask" / "Background" / "COCO" / "000000000003_background.png",
                active_pixels=25,
            )

            subset_root = root / "mirrored" / "br_gen" / "subsets" / "formal"
            artifacts = prepare_br_gen_formal_manifests(
                source_root,
                subset_root,
                allowed_sources=("COCO",),
            )
            samples = load_manifest(artifacts.formal_manifest_path)

            fake_base_scores = {
                "fake__brushnet__background__coco__000000000001_background": 0.40,
                "fake__lama__stuff__coco__000000000002_stuff": 0.70,
                "fake__brushnet__background__coco__000000000003_background": 0.95,
            }
            fake_degradation_offsets = {
                "clean": 0.0,
                "jpeg": -0.10,
                "resize": -0.05,
                "blur": -0.15,
                "crop": -0.20,
            }
            real_degradation_scores = {
                "clean": 0.05,
                "jpeg": 0.10,
                "resize": 0.08,
                "blur": 0.12,
                "crop": 0.15,
            }

            predictions_path = root / "predictions.jsonl"
            with predictions_path.open("w", encoding="utf-8") as handle:
                for sample in samples:
                    base_sample_id = sample.meta["base_sample_id"]
                    if sample.label == 1:
                        score = fake_base_scores[base_sample_id] + fake_degradation_offsets[sample.degradation or "clean"]
                    else:
                        score = real_degradation_scores[sample.degradation or "clean"]
                    handle.write(json.dumps({"sample_id": sample.sample_id, "score": score}) + "\n")

            output_dir = root / "outputs" / "m3"
            run_artifacts = run_m3_formal_eval(
                manifest_path=artifacts.formal_manifest_path,
                predictions_path=predictions_path,
                output_dir=output_dir,
                threshold=0.5,
                command="python scripts/run_m3_formal_eval.py --manifest formal --predictions preds",
            )

            self.assertTrue(run_artifacts.base_artifacts.summary_path.exists())
            self.assertTrue(run_artifacts.localized_summary_path.exists())
            self.assertTrue(run_artifacts.localized_metrics_csv_path.exists())
            self.assertTrue(run_artifacts.localized_report_path.exists())
            self.assertTrue(run_artifacts.localized_coverage_summary_path.exists())
            self.assertTrue(run_artifacts.coverage_audit_path.exists())
            self.assertTrue(run_artifacts.failure_evidence_map_path.exists())
            self.assertTrue(run_artifacts.overall_metrics_path.exists())
            self.assertTrue(run_artifacts.slice_metrics_json_path.exists())
            self.assertTrue(run_artifacts.slice_metrics_csv_path.exists())
            self.assertTrue(run_artifacts.paper_table_summary_path.exists())
            self.assertTrue(run_artifacts.protocol_alignment_audit_path.exists())

            summary = json.loads(run_artifacts.localized_summary_path.read_text(encoding="utf-8"))
            base_summary = json.loads(run_artifacts.base_artifacts.summary_path.read_text(encoding="utf-8"))
            overall_metrics = json.loads(run_artifacts.overall_metrics_path.read_text(encoding="utf-8"))
            slice_metrics = json.loads(run_artifacts.slice_metrics_json_path.read_text(encoding="utf-8"))
            protocol_audit = json.loads(
                run_artifacts.protocol_alignment_audit_path.read_text(encoding="utf-8")
            )
            paper_table_summary = run_artifacts.paper_table_summary_path.read_text(
                encoding="utf-8"
            )
            self.assertEqual(summary["runner"], "m3_localized_failure_eval")
            self.assertEqual(summary["evaluation_scope"], "restricted_pilot")
            self.assertEqual(base_summary["evaluation_scope"], "restricted_pilot")
            self.assertIn("by_generator_id", summary)
            self.assertIn("by_source_id", summary)
            self.assertIn("coverage", summary)
            self.assertIn("failure_evidence_map", summary)
            self.assertIn("small", summary["by_edit_area_ratio"]["groups"])
            self.assertIn("medium", summary["by_edit_area_ratio"]["groups"])
            self.assertIn("large", summary["by_edit_area_ratio"]["groups"])
            self.assertIn("background", summary["by_region_type"]["groups"])
            self.assertIn("stuff", summary["by_region_type"]["groups"])
            self.assertIn("BrushNet", summary["by_generator_id"]["groups"])
            self.assertIn("LaMa", summary["by_generator_id"]["groups"])
            self.assertIn("COCO", summary["by_source_id"]["groups"])
            self.assertEqual(summary["subtlety"]["status"], "blocked")
            self.assertIn("jpeg", summary["clean_to_degraded_delta_summary"])
            self.assertLess(
                summary["by_edit_area_ratio"]["groups"]["small"]["metrics"]["fake_recall"],
                summary["by_edit_area_ratio"]["groups"]["large"]["metrics"]["fake_recall"],
            )
            self.assertEqual(summary["worst_slice_ranking"][0]["group"], "small")
            self.assertEqual(summary["coverage"]["selection_policy"]["fake_sample_cap_applied"], False)
            self.assertIn("region_by_degradation", summary["exploratory_slices"])
            self.assertEqual(
                summary["by_edit_area_ratio"]["groups"]["small"]["diagnostic_label"],
                "inconclusive_low_support",
            )

            self.assertEqual(overall_metrics["runner"], "m6_br_gen_style_protocol_alignment")
            self.assertEqual(overall_metrics["evaluation_scope"], "restricted_pilot")
            self.assertEqual(overall_metrics["legacy_threshold"], 0.5)
            self.assertEqual(overall_metrics["paper_style_threshold"], 0.5)
            self.assertAlmostEqual(overall_metrics["legacy_fake_recall_value"], 0.6)
            self.assertAlmostEqual(
                overall_metrics["paper_manipulated_recall_at_0_5"],
                0.6,
            )
            self.assertTrue(overall_metrics["legacy_equals_paper_manipulated_recall"])
            self.assertEqual(overall_metrics["iou"]["status"], "deferred")

            rows = slice_metrics["rows"]
            self.assertTrue(
                any(
                    row["dimension"] == "generator_family"
                    and row["slice_value"] == "GAN"
                    and row["included_in_paper_main_table"]
                    for row in rows
                )
            )
            self.assertTrue(
                any(
                    row["dimension"] == "generator_family"
                    and row["slice_value"] == "Diffusion"
                    and row["included_in_paper_main_table"]
                    for row in rows
                )
            )
            self.assertTrue(
                any(
                    row["dimension"] == "degradation_detail"
                    and row["slice_value"] == "jpeg"
                    for row in rows
                )
            )
            self.assertEqual(
                protocol_audit["excluded_counts"]["excluded_from_split_a_count"],
                0,
            )
            self.assertIn("## Split A: GAN / Diffusion", paper_table_summary)
            self.assertIn("## Clean vs Degraded", paper_table_summary)
            self.assertIn("## Degradation Detail", paper_table_summary)
            self.assertIn("IoU: `N/A (deferred)`", paper_table_summary)


if __name__ == "__main__":
    unittest.main()
