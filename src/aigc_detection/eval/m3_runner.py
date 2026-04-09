from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
from PIL import Image

from aigc_detection.data import NormalizedSample, load_manifest
from aigc_detection.metrics import summarize_sample_group, validate_scores_by_sample_id

from .predictions import load_prediction_scores
from .protocol_alignment import (
    build_protocol_alignment_bundle,
    write_protocol_alignment_artifacts,
)
from .runner import EvaluationRunArtifacts, run_minimal_eval


AREA_BIN_ORDER = ("small", "medium", "large")
DEGRADATION_ORDER = ("clean", "jpeg", "resize", "blur", "crop")
LOW_SUPPORT_POSITIVE_THRESHOLD = 10
LOW_SUPPORT_SAMPLE_THRESHOLD = 20
FAILURE_FAKE_RECALL_GAP_THRESHOLD = -0.15
FAILURE_ACCURACY_GAP_THRESHOLD = -0.10
EASY_FAKE_RECALL_GAP_THRESHOLD = -0.05
EASY_ACCURACY_GAP_THRESHOLD = -0.02


@dataclass(frozen=True)
class M3EvaluationArtifacts:
    output_dir: Path
    base_artifacts: EvaluationRunArtifacts
    localized_summary_path: Path
    localized_metrics_csv_path: Path
    localized_report_path: Path
    localized_coverage_summary_path: Path
    coverage_audit_path: Path
    failure_evidence_map_path: Path
    overall_metrics_path: Path
    slice_metrics_json_path: Path
    slice_metrics_csv_path: Path
    paper_table_summary_path: Path
    protocol_alignment_audit_path: Path


class M3EvaluationError(ValueError):
    """Raised when the M3 localized-failure report cannot be computed."""


def run_m3_formal_eval(
    *,
    manifest_path: str | Path,
    predictions_path: str | Path,
    output_dir: str | Path,
    threshold: float = 0.5,
    command: str | None = None,
) -> M3EvaluationArtifacts:
    base_artifacts = run_minimal_eval(
        manifest_path=manifest_path,
        predictions_path=predictions_path,
        output_dir=output_dir,
        threshold=threshold,
        command=command,
    )

    manifest_path = Path(manifest_path).resolve()
    predictions_path = Path(predictions_path).resolve()
    output_dir = Path(output_dir).resolve()

    samples = load_manifest(manifest_path)
    scores_by_sample_id = load_prediction_scores(predictions_path)
    scores_by_sample_id = validate_scores_by_sample_id(samples, scores_by_sample_id, threshold)
    layout_audit = _load_layout_audit(manifest_path)
    summary = build_m3_localized_failure_summary(
        samples,
        scores_by_sample_id,
        threshold=threshold,
        layout_audit=layout_audit,
    )
    summary["inputs"] = {
        "manifest_path": str(manifest_path),
        "predictions_path": str(predictions_path),
        "threshold": threshold,
    }

    coverage_summary_payload = {
        "runner": summary["runner"],
        "evaluation_scope": summary["evaluation_scope"],
        "coverage": summary["coverage"],
        "metadata_fields": summary["metadata_fields"],
        "blocked_dimensions": summary["blocked_dimensions"],
    }

    localized_summary_path = output_dir / "localized_failure_summary.json"
    localized_metrics_csv_path = output_dir / "localized_failure_metrics.csv"
    localized_report_path = output_dir / "localized_failure_report.md"
    localized_coverage_summary_path = output_dir / "localized_coverage_summary.json"
    coverage_audit_path = output_dir / "coverage_audit.md"
    failure_evidence_map_path = output_dir / "failure_evidence_map.md"

    _write_json(localized_summary_path, summary)
    _write_json(localized_coverage_summary_path, coverage_summary_payload)
    _write_m3_metrics_csv(localized_metrics_csv_path, summary)
    _write_m3_markdown_report(localized_report_path, summary)
    _write_coverage_audit_markdown(coverage_audit_path, summary)
    _write_failure_evidence_map_markdown(failure_evidence_map_path, summary)
    protocol_alignment_bundle = build_protocol_alignment_bundle(
        samples,
        scores_by_sample_id,
        legacy_threshold=threshold,
        evaluation_scope=str(summary["evaluation_scope"]),
    )
    protocol_alignment_artifacts = write_protocol_alignment_artifacts(
        output_dir,
        protocol_alignment_bundle,
    )

    return M3EvaluationArtifacts(
        output_dir=output_dir,
        base_artifacts=base_artifacts,
        localized_summary_path=localized_summary_path,
        localized_metrics_csv_path=localized_metrics_csv_path,
        localized_report_path=localized_report_path,
        localized_coverage_summary_path=localized_coverage_summary_path,
        coverage_audit_path=coverage_audit_path,
        failure_evidence_map_path=failure_evidence_map_path,
        overall_metrics_path=protocol_alignment_artifacts.overall_metrics_path,
        slice_metrics_json_path=protocol_alignment_artifacts.slice_metrics_json_path,
        slice_metrics_csv_path=protocol_alignment_artifacts.slice_metrics_csv_path,
        paper_table_summary_path=protocol_alignment_artifacts.paper_table_summary_path,
        protocol_alignment_audit_path=protocol_alignment_artifacts.protocol_alignment_audit_path,
    )


def build_m3_localized_failure_summary(
    samples: Sequence[NormalizedSample],
    scores_by_sample_id: Mapping[str, float],
    *,
    threshold: float = 0.5,
    layout_audit: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    localized_samples = [sample for sample in samples if sample.task_type == "localized_edit"]
    if not localized_samples:
        raise M3EvaluationError("M3 localized-failure evaluation requires localized_edit samples.")
    if len(localized_samples) != len(samples):
        raise M3EvaluationError("M3 localized-failure evaluation does not support mixed task types.")

    clean_samples = [sample for sample in localized_samples if (sample.degradation or "clean") == "clean"]
    if not clean_samples:
        raise M3EvaluationError("M3 localized-failure evaluation requires clean localized samples.")

    clean_positive_samples = [sample for sample in clean_samples if sample.label == 1]
    clean_negative_samples = [sample for sample in clean_samples if sample.label == 0]
    if not clean_positive_samples or not clean_negative_samples:
        raise M3EvaluationError(
            "Clean localized evaluation requires both positive and negative samples."
        )

    positive_samples = [sample for sample in localized_samples if sample.label == 1]
    negative_samples = [sample for sample in localized_samples if sample.label == 0]
    negative_by_degradation = _group_by_degradation(negative_samples)
    positive_area_metadata = _build_area_metadata(positive_samples)

    raw_clean_summary = _summarize_group(clean_samples, scores_by_sample_id, threshold)
    clean_summary = _decorate_slice_summary(
        raw_clean_summary,
        reference_summary=None,
        dimension="overall_clean",
        group="overall_clean",
        scope="clean",
    )

    raw_degradation_summary = {
        degradation: _summarize_group(group_samples, scores_by_sample_id, threshold)
        for degradation, group_samples in _group_by_degradation(localized_samples).items()
    }
    degradation_summary = {
        degradation: _decorate_slice_summary(
            group_summary,
            reference_summary=raw_clean_summary if degradation != "clean" else None,
            dimension="degradation",
            group=degradation,
            scope="all_samples",
        )
        for degradation, group_summary in raw_degradation_summary.items()
    }

    region_dimension = _build_shared_negative_dimension(
        dimension="region_type",
        grouped_positive_samples=_group_samples(clean_positive_samples, field_name="region_type"),
        negative_samples=clean_negative_samples,
        scores_by_sample_id=scores_by_sample_id,
        threshold=threshold,
        reference_summary=raw_clean_summary,
        scope="clean_shared_negatives",
    )
    generator_dimension = _build_shared_negative_dimension(
        dimension="generator_id",
        grouped_positive_samples=_group_samples(clean_positive_samples, field_name="generator_id"),
        negative_samples=clean_negative_samples,
        scores_by_sample_id=scores_by_sample_id,
        threshold=threshold,
        reference_summary=raw_clean_summary,
        scope="clean_shared_negatives",
    )
    source_dimension = _build_shared_negative_dimension(
        dimension="source_id",
        grouped_positive_samples=_group_samples(clean_positive_samples, field_name="source_id"),
        negative_samples=clean_negative_samples,
        scores_by_sample_id=scores_by_sample_id,
        threshold=threshold,
        reference_summary=raw_clean_summary,
        scope="clean_shared_negatives",
    )
    area_dimension = _build_shared_negative_dimension(
        dimension="edit_area_ratio",
        grouped_positive_samples=_group_samples_by_area(clean_positive_samples, positive_area_metadata),
        negative_samples=clean_negative_samples,
        scores_by_sample_id=scores_by_sample_id,
        threshold=threshold,
        reference_summary=raw_clean_summary,
        scope="clean_shared_negatives",
    )
    area_dimension["thresholds"] = {
        "small_lt": 0.05,
        "medium_gte": 0.05,
        "medium_lt": 0.20,
        "large_gte": 0.20,
    }

    exploratory_slices = {
        "region_by_degradation": _build_pairwise_dimension(
            dimension="region_type_x_degradation",
            grouped_positive_samples=_group_samples_by_fields(
                positive_samples,
                field_names=("region_type", "degradation"),
            ),
            negative_by_group=negative_by_degradation,
            negative_group_field="degradation",
            scores_by_sample_id=scores_by_sample_id,
            threshold=threshold,
            reference_summaries=raw_degradation_summary,
            scope="same_degradation_negatives",
        ),
        "edit_area_ratio_by_degradation": _build_pairwise_dimension(
            dimension="edit_area_ratio_x_degradation",
            grouped_positive_samples=_group_samples_by_area_and_degradation(
                positive_samples,
                positive_area_metadata,
            ),
            negative_by_group=negative_by_degradation,
            negative_group_field="degradation",
            scores_by_sample_id=scores_by_sample_id,
            threshold=threshold,
            reference_summaries=raw_degradation_summary,
            scope="same_degradation_negatives",
        ),
        "generator_by_region": _build_pairwise_dimension(
            dimension="generator_id_x_region_type",
            grouped_positive_samples=_group_samples_by_fields(
                clean_positive_samples,
                field_names=("generator_id", "region_type"),
            ),
            negative_by_group={"clean": clean_negative_samples},
            negative_group_field=None,
            scores_by_sample_id=scores_by_sample_id,
            threshold=threshold,
            reference_summaries={"clean": raw_clean_summary},
            scope="clean_shared_negatives",
        ),
    }

    metadata_fields = _build_metadata_field_summary(
        localized_samples=localized_samples,
        positive_samples=positive_samples,
        clean_positive_samples=clean_positive_samples,
        positive_area_metadata=positive_area_metadata,
    )

    evaluation_scope = _infer_evaluation_scope(localized_samples)
    blocked_dimensions = {
        "subtlety": {
            "status": "blocked",
            "reason": "No explicit subtlety metadata is present in the M3 BR-Gen manifest.",
        }
    }

    sample_counts = {
        "clean_positive_count": len(clean_positive_samples),
        "clean_negative_count": len(clean_negative_samples),
        "by_degradation": {
            degradation: {
                "sample_count": len(group_samples),
                "positive_count": sum(sample.label for sample in group_samples),
                "negative_count": len(group_samples) - sum(sample.label for sample in group_samples),
            }
            for degradation, group_samples in _group_by_degradation(localized_samples).items()
        },
        "by_region_type": {group_name: len(group_samples) for group_name, group_samples in _group_samples(clean_positive_samples, field_name="region_type").items()},
        "by_generator_id": {group_name: len(group_samples) for group_name, group_samples in _group_samples(clean_positive_samples, field_name="generator_id").items()},
        "by_source_id": {group_name: len(group_samples) for group_name, group_samples in _group_samples(clean_positive_samples, field_name="source_id").items()},
        "by_edit_area_ratio": {
            group_name: len(group_samples)
            for group_name, group_samples in _group_samples_by_area(clean_positive_samples, positive_area_metadata).items()
        },
    }

    failure_evidence_map = _build_failure_evidence_map(
        degradation_summary=degradation_summary,
        generator_dimension=generator_dimension,
        region_dimension=region_dimension,
        area_dimension=area_dimension,
        source_dimension=source_dimension,
        exploratory_slices=exploratory_slices,
        blocked_dimensions=blocked_dimensions,
    )
    worst_slice_ranking = _build_worst_slice_ranking(failure_evidence_map)
    coverage = _build_coverage_summary(
        localized_samples=localized_samples,
        clean_samples=clean_samples,
        clean_positive_samples=clean_positive_samples,
        clean_negative_samples=clean_negative_samples,
        positive_area_metadata=positive_area_metadata,
        layout_audit=layout_audit,
        generator_dimension=generator_dimension,
        region_dimension=region_dimension,
        area_dimension=area_dimension,
        source_dimension=source_dimension,
        exploratory_slices=exploratory_slices,
        blocked_dimensions=blocked_dimensions,
    )

    return {
        "runner": "m3_localized_failure_eval",
        "evaluation_scope": evaluation_scope,
        "diagnostic_thresholds": {
            "low_support_positive_threshold": LOW_SUPPORT_POSITIVE_THRESHOLD,
            "low_support_sample_threshold": LOW_SUPPORT_SAMPLE_THRESHOLD,
            "failure_fake_recall_gap_threshold": FAILURE_FAKE_RECALL_GAP_THRESHOLD,
            "failure_accuracy_gap_threshold": FAILURE_ACCURACY_GAP_THRESHOLD,
            "easy_fake_recall_gap_threshold": EASY_FAKE_RECALL_GAP_THRESHOLD,
            "easy_accuracy_gap_threshold": EASY_ACCURACY_GAP_THRESHOLD,
        },
        "overall_clean": clean_summary,
        "by_degradation": degradation_summary,
        "by_region_type": region_dimension,
        "by_edit_area_ratio": area_dimension,
        "by_generator_id": generator_dimension,
        "by_source_id": source_dimension,
        "exploratory_slices": exploratory_slices,
        "metadata_fields": metadata_fields,
        "subtlety": blocked_dimensions["subtlety"],
        "blocked_dimensions": blocked_dimensions,
        "sample_counts": sample_counts,
        "coverage": coverage,
        "clean_to_degraded_delta_summary": _build_degradation_delta_summary(raw_clean_summary, raw_degradation_summary),
        "failure_evidence_map": failure_evidence_map,
        "worst_slice_ranking": worst_slice_ranking,
    }


def _build_metadata_field_summary(
    *,
    localized_samples: Sequence[NormalizedSample],
    positive_samples: Sequence[NormalizedSample],
    clean_positive_samples: Sequence[NormalizedSample],
    positive_area_metadata: Mapping[str, Mapping[str, Any]],
) -> dict[str, dict[str, Any]]:
    def _field_counts(samples: Sequence[NormalizedSample], field_name: str) -> dict[str, int]:
        explicit = sum(1 for sample in samples if getattr(sample, field_name) not in (None, ""))
        return {
            "explicit_count": explicit,
            "missing_count": len(samples) - explicit,
            "total_count": len(samples),
        }

    return {
        "source_id": {
            "status": "ok",
            "localized": _field_counts(localized_samples, "source_id"),
            "positives": _field_counts(positive_samples, "source_id"),
            "clean_positives": _field_counts(clean_positive_samples, "source_id"),
        },
        "generator_id": {
            "status": "ok",
            "localized": _field_counts(localized_samples, "generator_id"),
            "positives": _field_counts(positive_samples, "generator_id"),
            "clean_positives": _field_counts(clean_positive_samples, "generator_id"),
        },
        "region_type": {
            "status": "ok",
            "localized": _field_counts(localized_samples, "region_type"),
            "positives": _field_counts(positive_samples, "region_type"),
            "clean_positives": _field_counts(clean_positive_samples, "region_type"),
        },
        "degradation": {
            "status": "ok",
            "localized": _field_counts(localized_samples, "degradation"),
            "positives": _field_counts(positive_samples, "degradation"),
            "clean_positives": _field_counts(clean_positive_samples, "degradation"),
        },
        "subtlety": {
            "status": "blocked",
            "reason": "No explicit subtlety metadata is present in the active restricted pilot manifest.",
            "localized": _field_counts(localized_samples, "subtlety"),
            "positives": _field_counts(positive_samples, "subtlety"),
            "clean_positives": _field_counts(clean_positive_samples, "subtlety"),
        },
        "mask_path": {
            "status": "ok",
            "localized": {
                "explicit_count": sum(1 for sample in localized_samples if sample.mask_path is not None),
                "missing_count": sum(1 for sample in localized_samples if sample.mask_path is None),
                "total_count": len(localized_samples),
            },
            "positives": {
                "explicit_count": sum(1 for sample in positive_samples if sample.mask_path is not None),
                "missing_count": sum(1 for sample in positive_samples if sample.mask_path is None),
                "total_count": len(positive_samples),
            },
            "clean_positives": {
                "explicit_count": sum(1 for sample in clean_positive_samples if sample.mask_path is not None),
                "missing_count": sum(1 for sample in clean_positive_samples if sample.mask_path is None),
                "total_count": len(clean_positive_samples),
            },
        },
        "edit_area_ratio": {
            "status": "derived_from_mask",
            "available_positive_count": len(positive_area_metadata),
            "missing_positive_count": len(positive_samples) - len(positive_area_metadata),
            "clean_available_positive_count": sum(
                1 for sample in clean_positive_samples if sample.sample_id in positive_area_metadata
            ),
            "thresholds": {
                "small_lt": 0.05,
                "medium_gte": 0.05,
                "medium_lt": 0.20,
                "large_gte": 0.20,
            },
        },
    }


def _build_area_metadata(samples: Sequence[NormalizedSample]) -> dict[str, dict[str, Any]]:
    cache: dict[Path, tuple[float, str]] = {}
    metadata: dict[str, dict[str, Any]] = {}
    for sample in samples:
        if sample.mask_path is None:
            continue
        if sample.mask_path not in cache:
            ratio = _compute_edit_area_ratio(sample.mask_path)
            cache[sample.mask_path] = (ratio, _classify_area_bin(ratio))
        ratio, area_bin = cache[sample.mask_path]
        metadata[sample.sample_id] = {
            "edit_area_ratio": ratio,
            "edit_area_bin": area_bin,
        }
    return metadata


def _build_shared_negative_dimension(
    *,
    dimension: str,
    grouped_positive_samples: Mapping[str, Sequence[NormalizedSample]],
    negative_samples: Sequence[NormalizedSample],
    scores_by_sample_id: Mapping[str, float],
    threshold: float,
    reference_summary: Mapping[str, Any],
    scope: str,
) -> dict[str, Any]:
    if not grouped_positive_samples:
        return {
            "status": "blocked",
            "scope": scope,
            "reason": f"No explicit {dimension} metadata is present in the active restricted pilot subset.",
            "groups": {},
        }

    return {
        "status": "ok",
        "scope": scope,
        "groups": {
            group_name: _decorate_slice_summary(
                _summarize_group(list(group_samples) + list(negative_samples), scores_by_sample_id, threshold),
                reference_summary=reference_summary,
                dimension=dimension,
                group=group_name,
                scope=scope,
            )
            for group_name, group_samples in grouped_positive_samples.items()
        },
    }


def _build_pairwise_dimension(
    *,
    dimension: str,
    grouped_positive_samples: Mapping[str, dict[str, Any]],
    negative_by_group: Mapping[str, Sequence[NormalizedSample]],
    negative_group_field: str | None,
    scores_by_sample_id: Mapping[str, float],
    threshold: float,
    reference_summaries: Mapping[str, Mapping[str, Any]],
    scope: str,
) -> dict[str, Any]:
    if not grouped_positive_samples:
        return {
            "status": "blocked",
            "scope": scope,
            "reason": f"No supported samples are available for exploratory dimension {dimension}.",
            "groups": {},
        }

    groups: dict[str, dict[str, Any]] = {}
    for group_name, group_info in grouped_positive_samples.items():
        positive_samples = list(group_info["samples"])
        negative_group_key = "clean" if negative_group_field is None else str(group_info[negative_group_field])
        negative_samples = list(negative_by_group.get(negative_group_key, []))
        reference_summary = reference_summaries.get(negative_group_key)
        groups[group_name] = _decorate_slice_summary(
            _summarize_group(positive_samples + negative_samples, scores_by_sample_id, threshold),
            reference_summary=reference_summary,
            dimension=dimension,
            group=group_name,
            scope=scope,
        )
        groups[group_name]["metadata"] = {
            "negative_group_key": negative_group_key,
        }

    return {
        "status": "ok",
        "scope": scope,
        "groups": groups,
    }


def _decorate_slice_summary(
    summary: Mapping[str, Any],
    *,
    reference_summary: Mapping[str, Any] | None,
    dimension: str,
    group: str,
    scope: str,
) -> dict[str, Any]:
    metrics = dict(summary["metrics"])
    notes = list(summary.get("notes", []))
    support = _build_support(summary)
    decorated = {
        "status": summary["status"],
        "sample_count": summary["sample_count"],
        "positive_count": summary["positive_count"],
        "negative_count": summary["negative_count"],
        "metrics": metrics,
        "notes": notes,
        "scope": scope,
        "support": support,
        "dimension": dimension,
        "group": group,
    }

    if reference_summary is None:
        decorated["reference"] = {
            "scope": None,
            "metrics": None,
        }
        decorated["metric_gaps"] = {
            "auroc": None,
            "accuracy": None,
            "fake_recall": None,
        }
        decorated["diagnostic_label"] = "reference"
        decorated["diagnostic_notes"] = ["Reference slice for the current diagnostic view."]
        return decorated

    reference_metrics = dict(reference_summary["metrics"])
    metric_gaps = {
        metric_name: _metric_gap(metrics.get(metric_name), reference_metrics.get(metric_name))
        for metric_name in ("auroc", "accuracy", "fake_recall")
    }
    decorated["reference"] = {
        "scope": "overall_clean" if scope != "all_samples" else "clean",
        "metrics": reference_metrics,
    }
    decorated["metric_gaps"] = metric_gaps

    diagnostic_label, diagnostic_notes = _classify_slice_difficulty(
        support=support,
        metrics=metrics,
        metric_gaps=metric_gaps,
    )
    decorated["diagnostic_label"] = diagnostic_label
    decorated["diagnostic_notes"] = diagnostic_notes
    return decorated


def _build_support(summary: Mapping[str, Any]) -> dict[str, Any]:
    positive_count = int(summary["positive_count"])
    sample_count = int(summary["sample_count"])
    low_support_reasons: list[str] = []
    if positive_count < LOW_SUPPORT_POSITIVE_THRESHOLD:
        low_support_reasons.append(
            f"positive_count={positive_count} is below {LOW_SUPPORT_POSITIVE_THRESHOLD}"
        )
    if sample_count < LOW_SUPPORT_SAMPLE_THRESHOLD:
        low_support_reasons.append(
            f"sample_count={sample_count} is below {LOW_SUPPORT_SAMPLE_THRESHOLD}"
        )

    return {
        "low_support": bool(low_support_reasons),
        "low_support_reasons": low_support_reasons,
    }


def _classify_slice_difficulty(
    *,
    support: Mapping[str, Any],
    metrics: Mapping[str, Any],
    metric_gaps: Mapping[str, float | None],
) -> tuple[str, list[str]]:
    if support["low_support"]:
        return "inconclusive_low_support", list(support["low_support_reasons"])

    fake_recall = metrics.get("fake_recall")
    fake_recall_gap = metric_gaps.get("fake_recall")
    accuracy_gap = metric_gaps.get("accuracy")

    if (
        fake_recall_gap is not None
        and fake_recall_gap <= FAILURE_FAKE_RECALL_GAP_THRESHOLD
    ) or (
        accuracy_gap is not None
        and accuracy_gap <= FAILURE_ACCURACY_GAP_THRESHOLD
    ) or (
        fake_recall is not None
        and float(fake_recall) <= 0.60
    ):
        notes = []
        if fake_recall_gap is not None and fake_recall_gap <= FAILURE_FAKE_RECALL_GAP_THRESHOLD:
            notes.append(
                f"fake_recall_gap={fake_recall_gap} is below {FAILURE_FAKE_RECALL_GAP_THRESHOLD}"
            )
        if accuracy_gap is not None and accuracy_gap <= FAILURE_ACCURACY_GAP_THRESHOLD:
            notes.append(
                f"accuracy_gap={accuracy_gap} is below {FAILURE_ACCURACY_GAP_THRESHOLD}"
            )
        if fake_recall is not None and float(fake_recall) <= 0.60:
            notes.append(f"fake_recall={fake_recall} is at or below 0.60")
        return "failure_evidence", notes or ["Slice is materially weaker than the clean reference."]

    if (
        fake_recall_gap is not None
        and fake_recall_gap >= EASY_FAKE_RECALL_GAP_THRESHOLD
        and accuracy_gap is not None
        and accuracy_gap >= EASY_ACCURACY_GAP_THRESHOLD
    ):
        return "easy_regime", [
            "Slice remains close to the clean reference on fake_recall and accuracy."
        ]

    return "inconclusive", [
        "Slice is neither clearly easy nor clearly weak relative to the clean reference."
    ]


def _build_coverage_summary(
    *,
    localized_samples: Sequence[NormalizedSample],
    clean_samples: Sequence[NormalizedSample],
    clean_positive_samples: Sequence[NormalizedSample],
    clean_negative_samples: Sequence[NormalizedSample],
    positive_area_metadata: Mapping[str, Mapping[str, Any]],
    layout_audit: Mapping[str, Any] | None,
    generator_dimension: Mapping[str, Any],
    region_dimension: Mapping[str, Any],
    area_dimension: Mapping[str, Any],
    source_dimension: Mapping[str, Any],
    exploratory_slices: Mapping[str, Mapping[str, Any]],
    blocked_dimensions: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    clean_positive_base_ids = {
        str(sample.meta.get("base_sample_id", sample.sample_id))
        for sample in clean_positive_samples
    }
    clean_negative_base_ids = {
        str(sample.meta.get("base_sample_id", sample.sample_id))
        for sample in clean_negative_samples
    }
    localized_base_ids = {
        str(sample.meta.get("base_sample_id", sample.sample_id))
        for sample in localized_samples
    }

    generator_counts = {
        group_name: len(group_samples)
        for group_name, group_samples in _group_samples(clean_positive_samples, field_name="generator_id").items()
    }
    region_counts = {
        group_name: len(group_samples)
        for group_name, group_samples in _group_samples(clean_positive_samples, field_name="region_type").items()
    }
    source_counts = {
        group_name: len(group_samples)
        for group_name, group_samples in _group_samples(clean_positive_samples, field_name="source_id").items()
    }
    area_counts = {
        group_name: len(group_samples)
        for group_name, group_samples in _group_samples_by_area(clean_positive_samples, positive_area_metadata).items()
    }
    degradation_counts = {
        degradation: len(group_samples)
        for degradation, group_samples in _group_by_degradation(localized_samples).items()
    }

    expanded_assessment = {
        "generator_coverage_group_count": len(generator_counts),
        "region_coverage_group_count": len(region_counts),
        "source_coverage_group_count": len(source_counts),
        "area_bin_group_count": len(area_counts),
        "degradation_group_count": len(degradation_counts),
        "blocked_dimensions": sorted(blocked_dimensions),
        "coverage_quality": _classify_coverage_quality(
            generator_counts=generator_counts,
            region_counts=region_counts,
            source_counts=source_counts,
            area_counts=area_counts,
            blocked_dimensions=blocked_dimensions,
        ),
    }

    return {
        "selection_policy": _build_selection_policy_summary(layout_audit),
        "total_localized_records": len(localized_samples),
        "total_clean_records": len(clean_samples),
        "total_unique_base_ids": len(localized_base_ids),
        "clean_positive_count": len(clean_positive_samples),
        "clean_negative_count": len(clean_negative_samples),
        "clean_positive_unique_base_ids": len(clean_positive_base_ids),
        "clean_negative_unique_base_ids": len(clean_negative_base_ids),
        "generator_counts": generator_counts,
        "region_counts": region_counts,
        "source_counts": source_counts,
        "edit_area_ratio_counts": area_counts,
        "degradation_counts": degradation_counts,
        "available_dimensions": {
            "generator_id": generator_dimension["status"],
            "region_type": region_dimension["status"],
            "source_id": source_dimension["status"],
            "edit_area_ratio": area_dimension["status"],
            "subtlety": blocked_dimensions["subtlety"]["status"],
        },
        "exploratory_dimensions": {
            name: {
                "status": dimension["status"],
                "group_count": len(dimension.get("groups", {})),
            }
            for name, dimension in exploratory_slices.items()
        },
        "expanded_assessment": expanded_assessment,
    }


def _classify_coverage_quality(
    *,
    generator_counts: Mapping[str, int],
    region_counts: Mapping[str, int],
    source_counts: Mapping[str, int],
    area_counts: Mapping[str, int],
    blocked_dimensions: Mapping[str, Mapping[str, Any]],
) -> str:
    if len(generator_counts) <= 1 and len(region_counts) <= 1:
        return "still_narrow"
    if sum(1 for count in area_counts.values() if count > 0) <= 1:
        return "still_area_imbalanced"
    if blocked_dimensions:
        return "partially_blocked"
    return "expanded_diagnostic"


def _build_selection_policy_summary(layout_audit: Mapping[str, Any] | None) -> dict[str, Any]:
    if not layout_audit:
        return {
            "status": "missing_layout_audit",
        }

    selection = dict(layout_audit.get("selection") or {})
    counts = dict(layout_audit.get("counts") or {})
    return {
        "status": "ok",
        "evaluation_scope": layout_audit.get("evaluation_scope"),
        "allowed_sources": list(layout_audit.get("allowed_sources") or []),
        "split_name": layout_audit.get("split_name"),
        "max_fake_samples_requested": selection.get("max_fake_samples_requested"),
        "fake_sample_cap_applied": selection.get("fake_sample_cap_applied"),
        "candidate_fake_pairs_before_cap": counts.get("candidate_fake_pairs_before_cap"),
        "selected_fake_pairs_after_cap": counts.get("selected_fake_pairs_after_cap"),
        "candidate_group_counts": layout_audit.get("candidate_group_counts") or {},
        "selected_group_counts": layout_audit.get("selected_group_counts") or {},
    }


def _build_failure_evidence_map(
    *,
    degradation_summary: Mapping[str, Mapping[str, Any]],
    generator_dimension: Mapping[str, Any],
    region_dimension: Mapping[str, Any],
    area_dimension: Mapping[str, Any],
    source_dimension: Mapping[str, Any],
    exploratory_slices: Mapping[str, Mapping[str, Any]],
    blocked_dimensions: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    by_dimension = {
        "degradation": _flatten_dimension_groups(degradation_summary, include_reference=True),
        "generator_id": _flatten_dimension_wrapper(generator_dimension),
        "region_type": _flatten_dimension_wrapper(region_dimension),
        "edit_area_ratio": _flatten_dimension_wrapper(area_dimension),
        "source_id": _flatten_dimension_wrapper(source_dimension),
        "exploratory": {
            name: _flatten_dimension_wrapper(dimension)
            for name, dimension in exploratory_slices.items()
        },
    }

    return {
        "by_dimension": by_dimension,
        "blocked_dimensions": blocked_dimensions,
    }


def _flatten_dimension_wrapper(wrapper: Mapping[str, Any]) -> list[dict[str, Any]]:
    if wrapper.get("status") != "ok":
        return []
    return _flatten_dimension_groups(wrapper.get("groups", {}), include_reference=False)


def _flatten_dimension_groups(
    groups: Mapping[str, Mapping[str, Any]],
    *,
    include_reference: bool,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for group_name, group_summary in groups.items():
        if not include_reference and group_summary.get("diagnostic_label") == "reference":
            continue
        rows.append(
            {
                "group": group_name,
                "sample_count": group_summary.get("sample_count"),
                "positive_count": group_summary.get("positive_count"),
                "negative_count": group_summary.get("negative_count"),
                "auroc": group_summary.get("metrics", {}).get("auroc"),
                "accuracy": group_summary.get("metrics", {}).get("accuracy"),
                "fake_recall": group_summary.get("metrics", {}).get("fake_recall"),
                "low_support": group_summary.get("support", {}).get("low_support"),
                "low_support_reasons": group_summary.get("support", {}).get("low_support_reasons", []),
                "diagnostic_label": group_summary.get("diagnostic_label"),
                "diagnostic_notes": group_summary.get("diagnostic_notes", []),
                "scope": group_summary.get("scope"),
                "metric_gaps": group_summary.get("metric_gaps", {}),
            }
        )
    return rows


def _build_worst_slice_ranking(failure_evidence_map: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for dimension_name, dimension_rows in failure_evidence_map["by_dimension"].items():
        if dimension_name == "exploratory":
            for exploratory_name, exploratory_rows in dimension_rows.items():
                for row in exploratory_rows:
                    rows.append({"dimension": exploratory_name, **row})
            continue
        for row in dimension_rows:
            rows.append({"dimension": dimension_name, **row})

    label_rank = {
        "failure_evidence": 0,
        "inconclusive": 1,
        "inconclusive_low_support": 2,
        "easy_regime": 3,
        "reference": 4,
        None: 5,
    }
    rows.sort(
        key=lambda row: (
            label_rank.get(row.get("diagnostic_label"), 6),
            float("inf") if row.get("fake_recall") is None else row["fake_recall"],
            float("inf") if row.get("accuracy") is None else row["accuracy"],
            str(row.get("dimension")),
            str(row.get("group")),
        )
    )
    return rows


def _group_by_degradation(samples: Sequence[NormalizedSample]) -> dict[str, list[NormalizedSample]]:
    grouped: dict[str, list[NormalizedSample]] = {}
    for sample in samples:
        degradation = sample.degradation or "clean"
        grouped.setdefault(degradation, []).append(sample)

    ordered: dict[str, list[NormalizedSample]] = {}
    for degradation in DEGRADATION_ORDER:
        if degradation in grouped:
            ordered[degradation] = grouped.pop(degradation)
    for degradation in sorted(grouped):
        ordered[degradation] = grouped[degradation]
    return ordered


def _group_samples(
    samples: Sequence[NormalizedSample],
    *,
    field_name: str,
) -> dict[str, list[NormalizedSample]]:
    grouped: dict[str, list[NormalizedSample]] = {}
    for sample in samples:
        value = getattr(sample, field_name)
        if value is None or value == "":
            continue
        grouped.setdefault(str(value), []).append(sample)
    return dict(sorted(grouped.items()))


def _group_samples_by_fields(
    samples: Sequence[NormalizedSample],
    *,
    field_names: tuple[str, ...],
) -> dict[str, dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for sample in samples:
        values: list[str] = []
        skip = False
        degradation_value = "clean"
        for field_name in field_names:
            raw_value = getattr(sample, field_name)
            value = raw_value
            if field_name == "degradation":
                value = raw_value or "clean"
                degradation_value = str(value)
            if value is None or value == "":
                skip = True
                break
            values.append(str(value))
        if skip:
            continue
        group_name = " x ".join(values)
        grouped.setdefault(
            group_name,
            {
                "samples": [],
                "degradation": degradation_value,
            },
        )
        grouped[group_name]["samples"].append(sample)
    return dict(sorted(grouped.items()))


def _group_samples_by_area(
    samples: Sequence[NormalizedSample],
    area_metadata: Mapping[str, Mapping[str, Any]],
) -> dict[str, list[NormalizedSample]]:
    grouped = {name: [] for name in AREA_BIN_ORDER}
    for sample in samples:
        metadata = area_metadata.get(sample.sample_id)
        if metadata is None:
            continue
        grouped[str(metadata["edit_area_bin"])].append(sample)
    return grouped


def _group_samples_by_area_and_degradation(
    samples: Sequence[NormalizedSample],
    area_metadata: Mapping[str, Mapping[str, Any]],
) -> dict[str, dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for sample in samples:
        metadata = area_metadata.get(sample.sample_id)
        if metadata is None:
            continue
        degradation = sample.degradation or "clean"
        area_bin = str(metadata["edit_area_bin"])
        group_name = f"{area_bin} x {degradation}"
        grouped.setdefault(
            group_name,
            {
                "samples": [],
                "degradation": degradation,
            },
        )
        grouped[group_name]["samples"].append(sample)
    return dict(sorted(grouped.items()))


def _classify_area_bin(ratio: float) -> str:
    if ratio < 0.05:
        return "small"
    if ratio < 0.20:
        return "medium"
    return "large"


def _compute_edit_area_ratio(mask_path: Path) -> float:
    with Image.open(mask_path) as image:
        array = np.asarray(image)

    if array.size == 0:
        raise M3EvaluationError(f"Mask is empty: {mask_path}")

    if array.ndim == 3:
        foreground = np.any(array > 0, axis=2)
    else:
        foreground = array > 0
    return float(foreground.sum() / foreground.size)


def _summarize_group(
    samples: Sequence[NormalizedSample],
    scores_by_sample_id: Mapping[str, float],
    threshold: float,
) -> dict[str, Any]:
    return summarize_sample_group(
        samples,
        scores_by_sample_id,
        legacy_threshold=threshold,
    )


def _build_degradation_delta_summary(
    clean_summary: Mapping[str, Any],
    degradation_summary: Mapping[str, Mapping[str, Any]],
) -> dict[str, dict[str, float | None]]:
    clean_metrics = clean_summary["metrics"]
    summary: dict[str, dict[str, float | None]] = {}
    for degradation, group_summary in degradation_summary.items():
        if degradation == "clean":
            continue
        deltas: dict[str, float | None] = {}
        for metric_name, clean_value in clean_metrics.items():
            degraded_value = group_summary["metrics"].get(metric_name)
            if clean_value is None or degraded_value is None:
                deltas[metric_name] = None
                continue
            deltas[metric_name] = float(degraded_value) - float(clean_value)
        summary[degradation] = deltas
    return summary


def _metric_gap(value: float | None, reference_value: float | None) -> float | None:
    if value is None or reference_value is None:
        return None
    return float(value) - float(reference_value)


def _write_m3_metrics_csv(path: Path, summary: Mapping[str, Any]) -> None:
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
                "scope",
                "low_support",
                "diagnostic_label",
                "fake_recall_gap",
                "accuracy_gap",
                "notes",
            ],
        )
        writer.writeheader()
        writer.writerows(_flatten_m3_rows(summary))


def _flatten_m3_rows(summary: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    rows.extend(_rows_for_summary("overall_clean", "overall_clean", summary["overall_clean"], scope="clean"))

    for degradation, group_summary in summary["by_degradation"].items():
        rows.extend(_rows_for_summary("degradation", degradation, group_summary, scope="all_samples"))

    for dimension_name in ("by_generator_id", "by_region_type", "by_source_id", "by_edit_area_ratio"):
        dimension = summary[dimension_name]
        if dimension["status"] != "ok":
            rows.append(
                {
                    "dimension": dimension_name.removeprefix("by_"),
                    "group": "*blocked*",
                    "status": dimension["status"],
                    "sample_count": "",
                    "positive_count": "",
                    "negative_count": "",
                    "metric_name": "",
                    "metric_value": "",
                    "scope": dimension.get("scope", ""),
                    "low_support": "",
                    "diagnostic_label": "blocked",
                    "fake_recall_gap": "",
                    "accuracy_gap": "",
                    "notes": dimension.get("reason", ""),
                }
            )
            continue
        for group_name, group_summary in dimension["groups"].items():
            rows.extend(
                _rows_for_summary(
                    dimension_name.removeprefix("by_"),
                    group_name,
                    group_summary,
                    scope=str(group_summary.get("scope", dimension.get("scope", ""))),
                )
            )

    for exploratory_name, dimension in summary["exploratory_slices"].items():
        if dimension["status"] != "ok":
            continue
        for group_name, group_summary in dimension["groups"].items():
            rows.extend(
                _rows_for_summary(
                    exploratory_name,
                    group_name,
                    group_summary,
                    scope=str(group_summary.get("scope", dimension.get("scope", ""))),
                )
            )

    rows.append(
        {
            "dimension": "subtlety",
            "group": "*blocked*",
            "status": summary["subtlety"]["status"],
            "sample_count": "",
            "positive_count": "",
            "negative_count": "",
            "metric_name": "",
            "metric_value": "",
            "scope": "",
            "low_support": "",
            "diagnostic_label": "blocked",
            "fake_recall_gap": "",
            "accuracy_gap": "",
            "notes": summary["subtlety"]["reason"],
        }
    )
    return rows


def _rows_for_summary(
    dimension: str,
    group: str,
    group_summary: Mapping[str, Any],
    *,
    scope: str,
) -> list[dict[str, Any]]:
    notes = " | ".join(group_summary.get("notes", []) + group_summary.get("diagnostic_notes", []))
    rows: list[dict[str, Any]] = []
    for metric_name, metric_value in group_summary["metrics"].items():
        rows.append(
            {
                "dimension": dimension,
                "group": group,
                "status": group_summary["status"],
                "sample_count": group_summary["sample_count"],
                "positive_count": group_summary["positive_count"],
                "negative_count": group_summary["negative_count"],
                "metric_name": metric_name,
                "metric_value": metric_value,
                "scope": scope,
                "low_support": group_summary.get("support", {}).get("low_support"),
                "diagnostic_label": group_summary.get("diagnostic_label"),
                "fake_recall_gap": group_summary.get("metric_gaps", {}).get("fake_recall"),
                "accuracy_gap": group_summary.get("metric_gaps", {}).get("accuracy"),
                "notes": notes,
            }
        )
    return rows


def _write_m3_markdown_report(path: Path, summary: Mapping[str, Any]) -> None:
    clean_metrics = summary["overall_clean"]["metrics"]
    lines = [
        "# M3 Localized Failure Report",
        "",
        f"- Evaluation scope: `{summary['evaluation_scope']}`",
        f"- Coverage quality: `{summary['coverage']['expanded_assessment']['coverage_quality']}`",
        "",
        "## Clean Localized Reference",
        f"- AUROC: `{clean_metrics['auroc']}`",
        f"- Accuracy: `{clean_metrics['accuracy']}`",
        f"- fake_recall: `{clean_metrics['fake_recall']}`",
        "",
        "## Coverage Summary",
        f"- Total localized records: `{summary['coverage']['total_localized_records']}`",
        f"- Clean positives: `{summary['coverage']['clean_positive_count']}`",
        f"- Clean negatives: `{summary['coverage']['clean_negative_count']}`",
        f"- Generator groups: `{len(summary['coverage']['generator_counts'])}`",
        f"- Region groups: `{len(summary['coverage']['region_counts'])}`",
        f"- Source groups: `{len(summary['coverage']['source_counts'])}`",
        f"- Edit-area bins with support: `{sum(1 for count in summary['coverage']['edit_area_ratio_counts'].values() if count > 0)}`",
        "",
        "## Degradation Summary",
    ]

    for degradation, group_summary in summary["by_degradation"].items():
        metrics = group_summary["metrics"]
        lines.append(
            f"- {degradation}: AUROC={metrics['auroc']}, Accuracy={metrics['accuracy']}, "
            f"fake_recall={metrics['fake_recall']}, label={group_summary['diagnostic_label']}"
        )

    lines.extend(["", "## Core Localized Dimensions"])
    for dimension_key, heading in (
        ("by_generator_id", "generator_id"),
        ("by_region_type", "region_type"),
        ("by_source_id", "source_id"),
        ("by_edit_area_ratio", "edit_area_ratio"),
    ):
        dimension = summary[dimension_key]
        lines.append(f"- {heading}:")
        if dimension["status"] != "ok":
            lines.append(f"  - blocked: {dimension['reason']}")
            continue
        for group_name, group_summary in dimension["groups"].items():
            metrics = group_summary["metrics"]
            lines.append(
                f"  - {group_name}: positives={group_summary['positive_count']}, "
                f"AUROC={metrics['auroc']}, Accuracy={metrics['accuracy']}, "
                f"fake_recall={metrics['fake_recall']}, low_support={group_summary['support']['low_support']}, "
                f"label={group_summary['diagnostic_label']}"
            )

    lines.extend(
        [
            "",
            "## Blocked Dimensions",
            f"- subtlety: {summary['subtlety']['reason']}",
            "",
            "## Clean-to-Degraded Deltas",
        ]
    )
    for degradation, deltas in summary["clean_to_degraded_delta_summary"].items():
        lines.append(
            f"- {degradation}: AUROC delta={deltas['auroc']}, Accuracy delta={deltas['accuracy']}, "
            f"fake_recall delta={deltas['fake_recall']}"
        )

    lines.extend(["", "## Worst Slice Ranking"])
    for row in summary["worst_slice_ranking"][:10]:
        lines.append(
            f"- {row['dimension']} / {row['group']}: positives={row['positive_count']}, "
            f"fake_recall={row['fake_recall']}, accuracy={row['accuracy']}, "
            f"low_support={row['low_support']}, label={row['diagnostic_label']}"
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_coverage_audit_markdown(path: Path, summary: Mapping[str, Any]) -> None:
    coverage = summary["coverage"]
    selection = coverage["selection_policy"]
    lines = [
        "# Restricted Pilot Coverage Audit",
        "",
        f"- Evaluation scope: `{summary['evaluation_scope']}`",
        f"- Coverage quality: `{coverage['expanded_assessment']['coverage_quality']}`",
        "",
        "## Selection Policy",
        f"- Selection status: `{selection['status']}`",
        f"- Allowed sources: `{selection.get('allowed_sources')}`",
        f"- Cap requested: `{selection.get('max_fake_samples_requested')}`",
        f"- Cap applied: `{selection.get('fake_sample_cap_applied')}`",
        f"- Candidate fake pairs before cap: `{selection.get('candidate_fake_pairs_before_cap')}`",
        f"- Selected fake pairs after cap: `{selection.get('selected_fake_pairs_after_cap')}`",
        "",
        "## Current Coverage",
        f"- Total localized records: `{coverage['total_localized_records']}`",
        f"- Total clean records: `{coverage['total_clean_records']}`",
        f"- Unique base ids: `{coverage['total_unique_base_ids']}`",
        f"- Clean positive base ids: `{coverage['clean_positive_unique_base_ids']}`",
        f"- Clean negative base ids: `{coverage['clean_negative_unique_base_ids']}`",
        "",
        "## Dimension Coverage",
        f"- generator_id: `{coverage['generator_counts']}`",
        f"- region_type: `{coverage['region_counts']}`",
        f"- source_id: `{coverage['source_counts']}`",
        f"- edit_area_ratio: `{coverage['edit_area_ratio_counts']}`",
        f"- degradation: `{coverage['degradation_counts']}`",
        "",
        "## Metadata Status",
    ]

    for field_name, field_summary in summary["metadata_fields"].items():
        status = field_summary["status"]
        if status == "blocked":
            lines.append(f"- {field_name}: blocked ({field_summary['reason']})")
            continue
        if field_name == "edit_area_ratio":
            lines.append(
                f"- {field_name}: {status}, available_positive_count={field_summary['available_positive_count']}, "
                f"missing_positive_count={field_summary['missing_positive_count']}"
            )
            continue
        clean_positive = field_summary["clean_positives"]
        lines.append(
            f"- {field_name}: {status}, clean_explicit={clean_positive['explicit_count']}, "
            f"clean_missing={clean_positive['missing_count']}"
        )

    lines.extend(["", "## Exploratory Coverage"])
    for dimension_name, dimension_summary in coverage["exploratory_dimensions"].items():
        lines.append(
            f"- {dimension_name}: status={dimension_summary['status']}, group_count={dimension_summary['group_count']}"
        )

    lines.extend(
        [
            "",
            "## Assessment",
            "- Pilot success is not defined by overall metrics alone.",
            "- This audit is a coverage and diagnosability check.",
            "- Failure discovery quality depends on slice width, metadata visibility, and support counts.",
        ]
    )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_failure_evidence_map_markdown(path: Path, summary: Mapping[str, Any]) -> None:
    evidence_map = summary["failure_evidence_map"]
    lines = [
        "# Restricted Pilot Failure Evidence Map",
        "",
        f"- Evaluation scope: `{summary['evaluation_scope']}`",
        "- Diagnostic labels:",
        "  - `easy_regime`: slice remains close to the clean reference",
        "  - `failure_evidence`: slice is materially weaker than the clean reference",
        "  - `inconclusive`: slice is mixed",
        "  - `inconclusive_low_support`: slice is too small for a strong claim",
        "",
    ]

    for dimension_name, rows in evidence_map["by_dimension"].items():
        if dimension_name == "exploratory":
            lines.append("## Exploratory Dimensions")
            for exploratory_name, exploratory_rows in rows.items():
                lines.append(f"- {exploratory_name}:")
                if not exploratory_rows:
                    lines.append("  - no supported slices")
                    continue
                for row in exploratory_rows:
                    lines.append(
                        f"  - {row['group']}: positives={row['positive_count']}, AUROC={row['auroc']}, "
                        f"Accuracy={row['accuracy']}, fake_recall={row['fake_recall']}, "
                        f"low_support={row['low_support']}, label={row['diagnostic_label']}"
                    )
            lines.append("")
            continue

        lines.append(f"## {dimension_name}")
        if not rows:
            lines.append("- no supported slices")
            lines.append("")
            continue
        for row in rows:
            lines.append(
                f"- {row['group']}: positives={row['positive_count']}, AUROC={row['auroc']}, "
                f"Accuracy={row['accuracy']}, fake_recall={row['fake_recall']}, "
                f"low_support={row['low_support']}, label={row['diagnostic_label']}"
            )
        lines.append("")

    lines.append("## Blocked Dimensions")
    for dimension_name, blocked in evidence_map["blocked_dimensions"].items():
        lines.append(f"- {dimension_name}: {blocked['reason']}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _load_layout_audit(manifest_path: Path) -> dict[str, Any] | None:
    audit_path = manifest_path.parent / "layout_audit.json"
    if not audit_path.exists():
        return None
    try:
        return json.loads(audit_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _infer_evaluation_scope(samples: Sequence[NormalizedSample]) -> str:
    scopes = {
        str(sample.meta.get("evaluation_scope")).strip()
        for sample in samples
        if isinstance(sample.meta, dict) and sample.meta.get("evaluation_scope")
    }
    if not scopes:
        return "formal"
    if len(scopes) == 1:
        return scopes.pop()
    return "mixed"
