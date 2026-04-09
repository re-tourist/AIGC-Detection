"""Metric computation utilities shared across the repo evaluation pipeline."""

from .core import (
    PAPER_STYLE_ALIGNMENT_THRESHOLD,
    MetricValidationError,
    build_metric_report,
    compute_auroc,
    compute_binary_f1,
    compute_negative_recall,
    compute_positive_recall,
    summarize_binary_classification,
    summarize_sample_group,
    validate_scores_by_sample_id,
)

__all__ = [
    "PAPER_STYLE_ALIGNMENT_THRESHOLD",
    "MetricValidationError",
    "build_metric_report",
    "compute_auroc",
    "compute_binary_f1",
    "compute_negative_recall",
    "compute_positive_recall",
    "summarize_binary_classification",
    "summarize_sample_group",
    "validate_scores_by_sample_id",
]
