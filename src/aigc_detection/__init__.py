"""Minimal AIGC detection utilities for the M1 data/metric bootstrap."""

from .eval import (
    EvaluationRunArtifacts,
    PredictionValidationError,
    load_prediction_scores,
    run_minimal_eval,
)
from .metrics import MetricValidationError, build_metric_report

__all__ = [
    "EvaluationRunArtifacts",
    "MetricValidationError",
    "PredictionValidationError",
    "build_metric_report",
    "load_prediction_scores",
    "run_minimal_eval",
]

