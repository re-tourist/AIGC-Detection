from __future__ import annotations

import unittest
from dataclasses import replace
from pathlib import Path

from aigc_detection.data import load_manifest
from aigc_detection.metrics import (
    MetricValidationError,
    build_metric_report,
    summarize_binary_classification,
)


FIXTURE_MANIFEST = (
    Path(__file__).resolve().parent / "fixtures" / "local_mirror" / "manifest.jsonl"
)

FIXTURE_SCORES = {
    "loc_clean_fake": 0.91,
    "loc_clean_real": 0.11,
    "loc_jpeg_fake": 0.77,
    "loc_jpeg_real": 0.26,
    "full_clean_fake": 0.68,
    "full_clean_real": 0.08,
}


class MetricCoreTests(unittest.TestCase):
    def test_build_metric_report_returns_overall_and_grouped_metrics(self) -> None:
        samples = load_manifest(FIXTURE_MANIFEST)

        report = build_metric_report(samples, FIXTURE_SCORES)

        self.assertEqual(report["overall"]["status"], "ok")
        self.assertEqual(report["overall"]["sample_count"], 6)
        self.assertAlmostEqual(report["overall"]["metrics"]["auroc"], 1.0)
        self.assertAlmostEqual(report["overall"]["metrics"]["accuracy"], 1.0)
        self.assertAlmostEqual(report["overall"]["metrics"]["fake_recall"], 1.0)
        self.assertAlmostEqual(
            report["overall"]["paper_metrics"]["f1_at_paper_style_threshold"],
            1.0,
        )
        self.assertAlmostEqual(
            report["overall"]["paper_metrics"]["paper_manipulated_recall_at_0_5"],
            1.0,
        )
        self.assertAlmostEqual(
            report["overall"]["paper_metrics"]["paper_real_recall_at_0_5"],
            1.0,
        )
        self.assertAlmostEqual(
            report["overall"]["metric_audit"]["legacy_fake_recall_value"],
            1.0,
        )
        self.assertAlmostEqual(
            report["overall"]["metric_audit"]["paper_manipulated_recall_at_0_5"],
            1.0,
        )
        self.assertEqual(report["overall"]["metric_audit"]["legacy_threshold"], 0.5)
        self.assertEqual(report["overall"]["metric_audit"]["paper_style_threshold"], 0.5)
        self.assertTrue(
            report["overall"]["metric_audit"]["legacy_equals_paper_manipulated_recall"]
        )

        self.assertEqual(report["grouped"]["task_type"]["status"], "ok")
        self.assertIn("localized_edit", report["grouped"]["task_type"]["groups"])
        self.assertIn("full_image_fake", report["grouped"]["task_type"]["groups"])

        self.assertEqual(report["grouped"]["degradation"]["status"], "ok")
        self.assertIn("clean", report["grouped"]["degradation"]["groups"])
        self.assertIn("jpeg", report["grouped"]["degradation"]["groups"])

        self.assertEqual(report["slice_dimensions"]["region_type"]["status"], "blocked")
        self.assertEqual(report["slice_dimensions"]["subtlety"]["status"], "blocked")
        self.assertEqual(report["slice_dimensions"]["edit_area_ratio"]["status"], "blocked")

    def test_degradation_group_is_blocked_when_metadata_is_absent(self) -> None:
        samples = [replace(sample, degradation=None) for sample in load_manifest(FIXTURE_MANIFEST)]

        report = build_metric_report(samples, FIXTURE_SCORES)

        degradation_view = report["grouped"]["degradation"]
        self.assertEqual(degradation_view["status"], "blocked")
        self.assertEqual(degradation_view["included_sample_count"], 0)
        self.assertEqual(degradation_view["excluded_sample_count"], len(samples))
        self.assertEqual(degradation_view["groups"], {})

    def test_missing_prediction_scores_raise_validation_error(self) -> None:
        samples = load_manifest(FIXTURE_MANIFEST)
        incomplete_scores = dict(FIXTURE_SCORES)
        incomplete_scores.pop("loc_jpeg_real")

        with self.assertRaises(MetricValidationError):
            build_metric_report(samples, incomplete_scores)

    def test_unknown_prediction_scores_raise_validation_error(self) -> None:
        samples = load_manifest(FIXTURE_MANIFEST)
        extra_scores = dict(FIXTURE_SCORES)
        extra_scores["unknown_sample"] = 0.5

        with self.assertRaises(MetricValidationError):
            build_metric_report(samples, extra_scores)

    def test_summarize_binary_classification_marks_single_class_metrics_as_undefined(self) -> None:
        summary = summarize_binary_classification(
            [1, 1],
            [0.55, 0.90],
            legacy_threshold=0.6,
        )

        self.assertEqual(summary["status"], "ok")
        self.assertIsNone(summary["metrics"]["auroc"])
        self.assertAlmostEqual(summary["metrics"]["accuracy"], 0.5)
        self.assertAlmostEqual(summary["metrics"]["fake_recall"], 0.5)
        self.assertAlmostEqual(
            summary["paper_metrics"]["paper_manipulated_recall_at_0_5"],
            1.0,
        )
        self.assertIsNone(summary["paper_metrics"]["paper_real_recall_at_0_5"])
        self.assertIsNone(summary["paper_metrics"]["f1_at_paper_style_threshold"])
        self.assertFalse(summary["metric_audit"]["legacy_equals_paper_manipulated_recall"])
        self.assertIn("auroc", summary["metric_audit"]["undefined_metric_names"])
        self.assertIn(
            "paper_real_recall_at_0_5",
            summary["metric_audit"]["undefined_metric_names"],
        )
        self.assertIn(
            "f1_at_paper_style_threshold",
            summary["metric_audit"]["undefined_metric_names"],
        )

    def test_summarize_binary_classification_returns_empty_slice_payload(self) -> None:
        summary = summarize_binary_classification([], [], legacy_threshold=0.5)

        self.assertEqual(summary["status"], "empty_slice")
        self.assertEqual(summary["sample_count"], 0)
        self.assertIsNone(summary["metrics"]["auroc"])
        self.assertIsNone(summary["metrics"]["accuracy"])
        self.assertIsNone(summary["paper_metrics"]["f1_at_paper_style_threshold"])
        self.assertIsNone(
            summary["metric_audit"]["legacy_equals_paper_manipulated_recall"]
        )
        self.assertIn("The group contains no samples.", summary["notes"])


if __name__ == "__main__":
    unittest.main()
