from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from aigc_detection.eval import PredictionValidationError, load_prediction_scores, run_minimal_eval


FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "local_mirror"
FIXTURE_MANIFEST = FIXTURE_ROOT / "manifest.jsonl"
FIXTURE_PREDICTIONS = FIXTURE_ROOT / "predictions.jsonl"


class MinimalEvalRunnerTests(unittest.TestCase):
    def test_load_prediction_scores_reads_jsonl_records(self) -> None:
        scores = load_prediction_scores(FIXTURE_PREDICTIONS)

        self.assertEqual(len(scores), 6)
        self.assertAlmostEqual(scores["loc_clean_fake"], 0.91)
        self.assertAlmostEqual(scores["full_clean_real"], 0.08)

    def test_run_minimal_eval_writes_expected_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir) / "artifacts"
            artifacts = run_minimal_eval(
                manifest_path=FIXTURE_MANIFEST,
                predictions_path=FIXTURE_PREDICTIONS,
                output_dir=output_dir,
                threshold=0.5,
                command="python scripts/run_minimal_eval.py --manifest fixture --predictions fixture",
            )

            self.assertTrue(artifacts.summary_path.exists())
            self.assertTrue(artifacts.metrics_csv_path.exists())
            self.assertTrue(artifacts.smoke_report_path.exists())
            self.assertTrue(artifacts.config_snapshot_path.exists())

            summary_payload = json.loads(artifacts.summary_path.read_text(encoding="utf-8"))
            self.assertEqual(summary_payload["runner"], "m1_minimal_eval")
            self.assertEqual(summary_payload["inputs"]["sample_count"], 6)
            self.assertAlmostEqual(summary_payload["report"]["overall"]["metrics"]["accuracy"], 1.0)

            metrics_csv = artifacts.metrics_csv_path.read_text(encoding="utf-8")
            self.assertIn("dimension,group,status,sample_count,positive_count,negative_count,metric_name,metric_value,notes,reason", metrics_csv)
            self.assertIn("overall,overall,ok,6,3,3,accuracy,1.0", metrics_csv)
            self.assertIn("region_type,*blocked*,blocked", metrics_csv)

            smoke_report = artifacts.smoke_report_path.read_text(encoding="utf-8")
            self.assertIn("# M1 Minimal Evaluation Smoke Report", smoke_report)
            self.assertIn("## Blocked Slice Dimensions", smoke_report)
            self.assertIn("task_type", smoke_report)

    def test_prediction_loader_rejects_unknown_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            prediction_path = Path(tmp_dir) / "broken_predictions.jsonl"
            prediction_path.write_text(
                '{"sample_id":"sample","score":0.5,"unexpected":true}\n',
                encoding="utf-8",
            )

            with self.assertRaises(PredictionValidationError):
                load_prediction_scores(prediction_path)


if __name__ == "__main__":
    unittest.main()
