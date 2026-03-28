from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from aigc_detection.data import load_manifest
from aigc_detection.metrics import build_metric_report

from .predictions import load_prediction_scores


@dataclass(frozen=True)
class EvaluationRunArtifacts:
    output_dir: Path
    summary_path: Path
    metrics_csv_path: Path
    smoke_report_path: Path
    config_snapshot_path: Path


def run_minimal_eval(
    manifest_path: str | Path,
    predictions_path: str | Path,
    output_dir: str | Path,
    threshold: float = 0.5,
    command: str | None = None,
) -> EvaluationRunArtifacts:
    manifest_path = Path(manifest_path).resolve()
    predictions_path = Path(predictions_path).resolve()
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    samples = load_manifest(manifest_path)
    scores_by_sample_id = load_prediction_scores(predictions_path)
    report = build_metric_report(samples, scores_by_sample_id, threshold=threshold)

    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    summary_payload = {
        "runner": "m1_minimal_eval",
        "generated_at_utc": generated_at,
        "inputs": {
            "manifest_path": str(manifest_path),
            "predictions_path": str(predictions_path),
            "sample_count": len(samples),
            "threshold": threshold,
        },
        "report": report,
    }
    config_snapshot = {
        "runner": "scripts/run_minimal_eval.py",
        "generated_at_utc": generated_at,
        "command": command,
        "manifest_path": str(manifest_path),
        "predictions_path": str(predictions_path),
        "output_dir": str(output_dir),
        "threshold": threshold,
    }

    summary_path = output_dir / "summary.json"
    metrics_csv_path = output_dir / "metrics.csv"
    smoke_report_path = output_dir / "smoke_report.md"
    config_snapshot_path = output_dir / "config_snapshot.json"

    _write_json(summary_path, summary_payload)
    _write_metrics_csv(metrics_csv_path, report)
    _write_markdown_report(
        smoke_report_path,
        summary_payload=summary_payload,
        config_snapshot=config_snapshot,
    )
    _write_json(config_snapshot_path, config_snapshot)

    return EvaluationRunArtifacts(
        output_dir=output_dir,
        summary_path=summary_path,
        metrics_csv_path=metrics_csv_path,
        smoke_report_path=smoke_report_path,
        config_snapshot_path=config_snapshot_path,
    )


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_metrics_csv(path: Path, report: dict[str, Any]) -> None:
    rows = _flatten_metric_rows(report)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "dimension",
                "group",
                "status",
                "sample_count",
                "positive_count",
                "negative_count",
                "metric_name",
                "metric_value",
                "notes",
                "reason",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def _flatten_metric_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    rows.extend(_rows_for_metric_summary("overall", "overall", report["overall"]))

    grouped = report["grouped"]
    for dimension_name, dimension_report in grouped.items():
        if dimension_report["status"] == "blocked":
            rows.append(
                {
                    "dimension": dimension_name,
                    "group": "*blocked*",
                    "status": "blocked",
                    "sample_count": dimension_report.get("included_sample_count", 0),
                    "positive_count": "",
                    "negative_count": "",
                    "metric_name": "",
                    "metric_value": "",
                    "notes": "",
                    "reason": dimension_report["reason"],
                }
            )
            continue

        for group_name, group_summary in dimension_report["groups"].items():
            rows.extend(_rows_for_metric_summary(dimension_name, group_name, group_summary))

    for dimension_name, status in report["slice_dimensions"].items():
        rows.append(
            {
                "dimension": dimension_name,
                "group": "*blocked*",
                "status": status["status"],
                "sample_count": "",
                "positive_count": "",
                "negative_count": "",
                "metric_name": "",
                "metric_value": "",
                "notes": "",
                "reason": status["reason"],
            }
        )

    return rows


def _rows_for_metric_summary(
    dimension_name: str, group_name: str, summary: dict[str, Any]
) -> list[dict[str, Any]]:
    notes = " | ".join(summary.get("notes", []))
    rows: list[dict[str, Any]] = []
    for metric_name, metric_value in summary["metrics"].items():
        rows.append(
            {
                "dimension": dimension_name,
                "group": group_name,
                "status": summary["status"],
                "sample_count": summary["sample_count"],
                "positive_count": summary["positive_count"],
                "negative_count": summary["negative_count"],
                "metric_name": metric_name,
                "metric_value": metric_value,
                "notes": notes,
                "reason": "",
            }
        )
    return rows


def _write_markdown_report(
    path: Path, summary_payload: dict[str, Any], config_snapshot: dict[str, Any]
) -> None:
    inputs = summary_payload["inputs"]
    report = summary_payload["report"]
    overall_metrics = report["overall"]["metrics"]

    lines = [
        "# M1 Minimal Evaluation Smoke Report",
        "",
        "## Inputs",
        f"- Manifest: `{inputs['manifest_path']}`",
        f"- Predictions: `{inputs['predictions_path']}`",
        f"- Sample count: `{inputs['sample_count']}`",
        f"- Threshold: `{inputs['threshold']}`",
        "",
        "## Overall Metrics",
        f"- AUROC: `{overall_metrics['auroc']}`",
        f"- Accuracy: `{overall_metrics['accuracy']}`",
        f"- fake_recall: `{overall_metrics['fake_recall']}`",
        "",
        "## Grouped Reporting",
        _format_grouped_dimension("task_type", report["grouped"]["task_type"]),
        _format_grouped_dimension("degradation", report["grouped"]["degradation"]),
        "",
        "## Blocked Slice Dimensions",
    ]

    for dimension_name, status in report["slice_dimensions"].items():
        lines.append(f"- {dimension_name}: {status['reason']}")

    lines.extend(
        [
            "",
            "## Provenance",
            f"- Runner: `{config_snapshot['runner']}`",
            f"- Command: `{config_snapshot['command']}`",
            f"- Generated at: `{config_snapshot['generated_at_utc']}`",
        ]
    )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _format_grouped_dimension(dimension_name: str, dimension_report: dict[str, Any]) -> str:
    if dimension_report["status"] == "blocked":
        return f"- {dimension_name}: blocked ({dimension_report['reason']})"

    group_summaries: list[str] = []
    for group_name, summary in dimension_report["groups"].items():
        metrics = summary["metrics"]
        group_summaries.append(
            f"{group_name} -> AUROC={metrics['auroc']}, Accuracy={metrics['accuracy']}, "
            f"fake_recall={metrics['fake_recall']}"
        )

    return f"- {dimension_name}: " + "; ".join(group_summaries)
