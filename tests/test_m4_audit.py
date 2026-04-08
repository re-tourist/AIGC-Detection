from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from aigc_detection.eval.m4_audit import (
    aggregate_seed_audit,
    load_reference_artifacts,
    load_seed_metrics,
    render_aggregate_markdown,
    render_run_status_markdown,
)


def _write_reference_artifacts(root: Path) -> Path:
    eval_dir = root / "eval"
    eval_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "evaluation_scope": "restricted_pilot",
        "inputs": {"sample_count": 100},
        "report": {
            "overall": {
                "metrics": {
                    "accuracy": 0.50,
                    "auroc": 0.70,
                    "fake_recall": 0.40,
                }
            }
        },
    }
    localized = {
        "subtlety": {"status": "blocked", "reason": "missing"},
        "by_region_type": {
            "groups": {
                "background": {
                    "sample_count": 50,
                    "support": {"low_support": False, "low_support_reasons": []},
                    "metrics": {"accuracy": 0.80, "auroc": 0.90, "fake_recall": 0.75},
                },
                "stuff": {
                    "sample_count": 50,
                    "support": {"low_support": False, "low_support_reasons": []},
                    "metrics": {"accuracy": 0.30, "auroc": 0.60, "fake_recall": 0.20},
                },
            }
        },
        "by_edit_area_ratio": {
            "groups": {
                "small": {
                    "sample_count": 10,
                    "support": {"low_support": False, "low_support_reasons": []},
                    "metrics": {"accuracy": 0.20, "auroc": 0.50, "fake_recall": 0.10},
                },
                "medium": {
                    "sample_count": 20,
                    "support": {"low_support": False, "low_support_reasons": []},
                    "metrics": {"accuracy": 0.25, "auroc": 0.55, "fake_recall": 0.15},
                },
                "large": {
                    "sample_count": 70,
                    "support": {"low_support": False, "low_support_reasons": []},
                    "metrics": {"accuracy": 0.60, "auroc": 0.85, "fake_recall": 0.60},
                },
            }
        },
    }
    (eval_dir / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
    (eval_dir / "localized_failure_summary.json").write_text(json.dumps(localized), encoding="utf-8")
    return eval_dir


class M4AuditTests(unittest.TestCase):
    def test_load_reference_and_seed_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            eval_dir = _write_reference_artifacts(Path(tmp_dir))
            reference = load_reference_artifacts(eval_dir)
            seed_metrics = load_seed_metrics(eval_dir)

            self.assertEqual(reference["evaluation_scope"], "restricted_pilot")
            self.assertEqual(reference["sample_count"], 100)
            self.assertAlmostEqual(reference["overall"]["accuracy"], 0.50)
            self.assertAlmostEqual(reference["slices"]["background"]["metrics"]["fake_recall"], 0.75)
            self.assertEqual(reference["subtlety"]["status"], "blocked")
            self.assertFalse(reference["slice_support"]["stuff"]["low_support"])
            self.assertEqual(seed_metrics["slices"]["small"]["metrics"]["fake_recall"], 0.10)

    def test_aggregate_seed_audit_and_renderers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            eval_dir = _write_reference_artifacts(root)
            reference = load_reference_artifacts(eval_dir)
            seed_runs = [
                {
                    "seed": 0,
                    "status": "success",
                    "output_dir": str(root / "seed_000"),
                    "stages": {"export": "success", "eval": "success"},
                    "duration_seconds": 10.0,
                    "metrics": {
                        "overall": {"accuracy": 0.52, "auroc": 0.71, "fake_recall": 0.41},
                        "slices": {
                            "background": {"metrics": {"fake_recall": 0.76}},
                            "stuff": {"metrics": {"fake_recall": 0.21}},
                            "small": {"metrics": {"fake_recall": 0.11}},
                            "medium": {"metrics": {"fake_recall": 0.16}},
                            "large": {"metrics": {"fake_recall": 0.61}},
                        },
                        "subtlety": {"status": "blocked"},
                    },
                },
                {
                    "seed": 1,
                    "status": "success",
                    "output_dir": str(root / "seed_001"),
                    "stages": {"export": "success", "eval": "success"},
                    "duration_seconds": 11.0,
                    "metrics": {
                        "overall": {"accuracy": 0.54, "auroc": 0.73, "fake_recall": 0.43},
                        "slices": {
                            "background": {"metrics": {"fake_recall": 0.77}},
                            "stuff": {"metrics": {"fake_recall": 0.19}},
                            "small": {"metrics": {"fake_recall": 0.12}},
                            "medium": {"metrics": {"fake_recall": 0.14}},
                            "large": {"metrics": {"fake_recall": 0.59}},
                        },
                        "subtlety": {"status": "blocked"},
                    },
                },
                {
                    "seed": 2,
                    "status": "failed",
                    "output_dir": str(root / "seed_002"),
                    "stages": {"export": "failed", "eval": "pending"},
                    "duration_seconds": 3.0,
                    "error": "boom",
                },
            ]

            summary = aggregate_seed_audit(
                run_id="run-123",
                manifest_path=root / "manifest.jsonl",
                output_root=root,
                reference=reference,
                seed_runs=seed_runs,
                baseline_eval_dir=eval_dir,
                baseline_predictions_path=root / "baseline.jsonl",
            )

            self.assertEqual(summary["status"]["successful_seeds"], 2)
            self.assertEqual(summary["status"]["failed_seed_ids"], [2])
            self.assertAlmostEqual(summary["aggregate"]["numeric_metrics"]["overall_accuracy"]["local_mean"], 0.53)
            self.assertAlmostEqual(summary["aggregate"]["numeric_metrics"]["stuff_fake_recall"]["delta_mean"], 0.0)
            self.assertEqual(summary["aggregate"]["subtlety"]["baseline"], "blocked")

            markdown = render_aggregate_markdown(summary)
            self.assertIn("M4 Multi-Seed Local Probe Audit", markdown)
            self.assertIn("overall_accuracy", markdown)
            self.assertIn("seed `2`: `failed`", markdown)

            status_md = render_run_status_markdown(summary)
            self.assertIn("Error", status_md)
            self.assertIn("boom", status_md)


if __name__ == "__main__":
    unittest.main()
