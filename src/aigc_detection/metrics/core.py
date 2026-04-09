from __future__ import annotations

import math
from collections import defaultdict
from typing import Any, Mapping, Sequence

from aigc_detection.data import NormalizedSample

P2_BLOCKED_DIMENSIONS = ("region_type", "subtlety", "edit_area_ratio")
PAPER_STYLE_ALIGNMENT_THRESHOLD = 0.5


class MetricValidationError(ValueError):
    """Raised when samples or scores cannot produce a valid metric report."""


def build_metric_report(
    samples: Sequence[NormalizedSample],
    scores_by_sample_id: Mapping[str, float],
    threshold: float = 0.5,
) -> dict[str, Any]:
    """Build the frozen M1 metric report with additive M6-alignment metrics."""

    normalized_scores = validate_scores_by_sample_id(samples, scores_by_sample_id, threshold)

    return {
        "overall": summarize_sample_group(
            samples,
            normalized_scores,
            legacy_threshold=threshold,
        ),
        "grouped": {
            "task_type": _build_grouped_view(
                samples=samples,
                scores_by_sample_id=normalized_scores,
                threshold=threshold,
                field_name="task_type",
                requires_explicit_metadata=False,
            ),
            "degradation": _build_grouped_view(
                samples=samples,
                scores_by_sample_id=normalized_scores,
                threshold=threshold,
                field_name="degradation",
                requires_explicit_metadata=True,
            ),
        },
        "slice_dimensions": {
            "region_type": _blocked_dimension(
                "P2 slice reporting remains outside the frozen M1 metric scope."
            ),
            "subtlety": _blocked_dimension(
                "P2 slice reporting remains outside the frozen M1 metric scope."
            ),
            "edit_area_ratio": _blocked_dimension(
                "P2 slice reporting remains outside the frozen M1 metric scope, and "
                "no derivation rule is frozen in the active contract."
            ),
        },
    }


def validate_scores_by_sample_id(
    samples: Sequence[NormalizedSample],
    scores_by_sample_id: Mapping[str, float],
    threshold: float,
) -> dict[str, float]:
    if not samples:
        raise MetricValidationError("Cannot compute metrics without normalized samples.")
    if not isinstance(scores_by_sample_id, Mapping):
        raise MetricValidationError("scores_by_sample_id must be a mapping keyed by sample_id.")
    _validate_threshold(threshold, "threshold")

    sample_ids = [sample.sample_id for sample in samples]
    duplicate_ids = sorted({sample_id for sample_id in sample_ids if sample_ids.count(sample_id) > 1})
    if duplicate_ids:
        raise MetricValidationError(
            f"Duplicate sample_id values are not allowed: {', '.join(duplicate_ids)}"
        )

    missing_ids = sorted(set(sample_ids) - set(scores_by_sample_id))
    if missing_ids:
        raise MetricValidationError(
            f"Missing prediction scores for sample_id values: {', '.join(missing_ids)}"
        )

    extra_ids = sorted(set(scores_by_sample_id) - set(sample_ids))
    if extra_ids:
        raise MetricValidationError(
            f"Prediction scores include unknown sample_id values: {', '.join(extra_ids)}"
        )

    normalized_scores: dict[str, float] = {}
    for sample_id in sample_ids:
        raw_score = scores_by_sample_id[sample_id]
        if not isinstance(raw_score, (int, float)) or isinstance(raw_score, bool):
            raise MetricValidationError(
                f"Prediction score for sample_id {sample_id!r} must be numeric."
            )
        score = float(raw_score)
        if not math.isfinite(score):
            raise MetricValidationError(
                f"Prediction score for sample_id {sample_id!r} must be finite."
            )
        normalized_scores[sample_id] = score
    return normalized_scores


def summarize_sample_group(
    samples: Sequence[NormalizedSample],
    scores_by_sample_id: Mapping[str, float],
    *,
    legacy_threshold: float,
    paper_style_threshold: float = PAPER_STYLE_ALIGNMENT_THRESHOLD,
) -> dict[str, Any]:
    labels = [sample.label for sample in samples]
    scores = [float(scores_by_sample_id[sample.sample_id]) for sample in samples]
    return summarize_binary_classification(
        labels,
        scores,
        legacy_threshold=legacy_threshold,
        paper_style_threshold=paper_style_threshold,
    )


def summarize_binary_classification(
    labels: Sequence[int],
    scores: Sequence[float],
    *,
    legacy_threshold: float,
    paper_style_threshold: float = PAPER_STYLE_ALIGNMENT_THRESHOLD,
) -> dict[str, Any]:
    _validate_threshold(legacy_threshold, "legacy_threshold")
    _validate_threshold(paper_style_threshold, "paper_style_threshold")
    if len(labels) != len(scores):
        raise MetricValidationError(
            "labels and scores must have the same length for binary metric computation."
        )

    if not labels:
        return {
            "status": "empty_slice",
            "sample_count": 0,
            "positive_count": 0,
            "negative_count": 0,
            "metrics": {
                "auroc": None,
                "accuracy": None,
                "fake_recall": None,
            },
            "paper_metrics": {
                "f1_at_paper_style_threshold": None,
                "paper_manipulated_recall_at_0_5": None,
                "paper_real_recall_at_0_5": None,
            },
            "metric_audit": {
                "legacy_fake_recall_value": None,
                "paper_manipulated_recall_at_0_5": None,
                "legacy_threshold": float(legacy_threshold),
                "paper_style_threshold": float(paper_style_threshold),
                "legacy_equals_paper_manipulated_recall": None,
                "undefined_metric_names": [
                    "auroc",
                    "accuracy",
                    "fake_recall",
                    "f1_at_paper_style_threshold",
                    "paper_manipulated_recall_at_0_5",
                    "paper_real_recall_at_0_5",
                ],
            },
            "notes": ["The group contains no samples."],
        }

    normalized_labels: list[int] = []
    normalized_scores: list[float] = []
    for index, label in enumerate(labels):
        if label not in (0, 1):
            raise MetricValidationError(f"labels[{index}] must be 0/1, got {label!r}")
        normalized_labels.append(int(label))

    for index, score in enumerate(scores):
        if not isinstance(score, (int, float)) or isinstance(score, bool):
            raise MetricValidationError(f"scores[{index}] must be numeric, got {score!r}")
        normalized_score = float(score)
        if not math.isfinite(normalized_score):
            raise MetricValidationError(f"scores[{index}] must be finite, got {score!r}")
        normalized_scores.append(normalized_score)

    positive_count = sum(normalized_labels)
    negative_count = len(normalized_labels) - positive_count
    notes: list[str] = []
    undefined_metric_names: list[str] = []

    auroc = compute_auroc(normalized_labels, normalized_scores)
    if auroc is None:
        notes.append("AUROC is undefined because both label classes are not present.")
        undefined_metric_names.append("auroc")

    accuracy = compute_accuracy(normalized_labels, normalized_scores, legacy_threshold)
    legacy_fake_recall = compute_positive_recall(
        normalized_labels,
        normalized_scores,
        legacy_threshold,
    )
    if legacy_fake_recall is None:
        notes.append("fake_recall is undefined because the group contains no positive labels.")
        undefined_metric_names.append("fake_recall")

    paper_manipulated_recall = compute_positive_recall(
        normalized_labels,
        normalized_scores,
        paper_style_threshold,
    )
    if paper_manipulated_recall is None:
        notes.append(
            "paper_manipulated_recall_at_0_5 is undefined because the group contains no positive labels."
        )
        undefined_metric_names.append("paper_manipulated_recall_at_0_5")

    paper_real_recall = compute_negative_recall(
        normalized_labels,
        normalized_scores,
        paper_style_threshold,
    )
    if paper_real_recall is None:
        notes.append(
            "paper_real_recall_at_0_5 is undefined because the group contains no negative labels."
        )
        undefined_metric_names.append("paper_real_recall_at_0_5")

    f1_at_paper_style_threshold = compute_binary_f1(
        normalized_labels,
        normalized_scores,
        paper_style_threshold,
    )
    if f1_at_paper_style_threshold is None:
        notes.append(
            "f1_at_paper_style_threshold is undefined because both label classes are not present."
        )
        undefined_metric_names.append("f1_at_paper_style_threshold")

    legacy_equals_paper = None
    if legacy_fake_recall is not None and paper_manipulated_recall is not None:
        legacy_equals_paper = math.isclose(
            float(legacy_fake_recall),
            float(paper_manipulated_recall),
            rel_tol=0.0,
            abs_tol=1e-12,
        )

    return {
        "status": "ok",
        "sample_count": len(normalized_labels),
        "positive_count": positive_count,
        "negative_count": negative_count,
        "metrics": {
            "auroc": auroc,
            "accuracy": accuracy,
            "fake_recall": legacy_fake_recall,
        },
        "paper_metrics": {
            "f1_at_paper_style_threshold": f1_at_paper_style_threshold,
            "paper_manipulated_recall_at_0_5": paper_manipulated_recall,
            "paper_real_recall_at_0_5": paper_real_recall,
        },
        "metric_audit": {
            "legacy_fake_recall_value": legacy_fake_recall,
            "paper_manipulated_recall_at_0_5": paper_manipulated_recall,
            "legacy_threshold": float(legacy_threshold),
            "paper_style_threshold": float(paper_style_threshold),
            "legacy_equals_paper_manipulated_recall": legacy_equals_paper,
            "undefined_metric_names": undefined_metric_names,
        },
        "notes": notes,
    }


def _build_grouped_view(
    samples: Sequence[NormalizedSample],
    scores_by_sample_id: Mapping[str, float],
    threshold: float,
    field_name: str,
    requires_explicit_metadata: bool,
) -> dict[str, Any]:
    grouped_samples: dict[str, list[NormalizedSample]] = defaultdict(list)
    excluded_sample_count = 0

    for sample in samples:
        if requires_explicit_metadata and not sample.has_explicit_metadata(field_name):
            excluded_sample_count += 1
            continue
        group_value = getattr(sample, field_name)
        if group_value is None:
            excluded_sample_count += 1
            continue
        grouped_samples[str(group_value)].append(sample)

    if not grouped_samples:
        if requires_explicit_metadata:
            return {
                "status": "blocked",
                "reason": (
                    f"Explicit {field_name} metadata is absent from all normalized samples."
                ),
                "groups": {},
                "included_sample_count": 0,
                "excluded_sample_count": excluded_sample_count,
            }
        raise MetricValidationError(
            f"Unable to build grouped view for required field {field_name!r}."
        )

    notes: list[str] = []
    if excluded_sample_count:
        notes.append(
            f"{excluded_sample_count} samples were excluded because {field_name} metadata "
            "was not explicit."
        )

    return {
        "status": "ok",
        "groups": {
            group_name: summarize_sample_group(
                group_samples,
                scores_by_sample_id,
                legacy_threshold=threshold,
            )
            for group_name, group_samples in sorted(grouped_samples.items())
        },
        "included_sample_count": sum(len(group) for group in grouped_samples.values()),
        "excluded_sample_count": excluded_sample_count,
        "notes": notes,
    }


def _blocked_dimension(reason: str) -> dict[str, str]:
    return {
        "status": "blocked",
        "reason": reason,
    }


def compute_accuracy(labels: Sequence[int], scores: Sequence[float], threshold: float) -> float:
    predictions = [1 if score >= threshold else 0 for score in scores]
    correct = sum(1 for label, prediction in zip(labels, predictions) if label == prediction)
    return correct / len(labels)


def compute_positive_recall(
    labels: Sequence[int], scores: Sequence[float], threshold: float
) -> float | None:
    positive_indices = [index for index, label in enumerate(labels) if label == 1]
    if not positive_indices:
        return None
    true_positives = sum(1 for index in positive_indices if scores[index] >= threshold)
    return true_positives / len(positive_indices)


def compute_negative_recall(
    labels: Sequence[int], scores: Sequence[float], threshold: float
) -> float | None:
    negative_indices = [index for index, label in enumerate(labels) if label == 0]
    if not negative_indices:
        return None
    true_negatives = sum(1 for index in negative_indices if scores[index] < threshold)
    return true_negatives / len(negative_indices)


def compute_binary_f1(
    labels: Sequence[int], scores: Sequence[float], threshold: float
) -> float | None:
    positive_count = sum(labels)
    negative_count = len(labels) - positive_count
    if positive_count == 0 or negative_count == 0:
        return None

    predictions = [1 if score >= threshold else 0 for score in scores]
    true_positives = sum(
        1 for label, prediction in zip(labels, predictions) if label == 1 and prediction == 1
    )
    false_positives = sum(
        1 for label, prediction in zip(labels, predictions) if label == 0 and prediction == 1
    )
    false_negatives = sum(
        1 for label, prediction in zip(labels, predictions) if label == 1 and prediction == 0
    )

    precision_denominator = true_positives + false_positives
    recall_denominator = true_positives + false_negatives
    precision = true_positives / precision_denominator if precision_denominator else 0.0
    recall = true_positives / recall_denominator if recall_denominator else 0.0
    if precision == 0.0 and recall == 0.0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def compute_auroc(labels: Sequence[int], scores: Sequence[float]) -> float | None:
    positive_count = sum(labels)
    negative_count = len(labels) - positive_count
    if positive_count == 0 or negative_count == 0:
        return None

    sorted_pairs = sorted(zip(scores, labels), key=lambda pair: pair[0])
    rank_sum_for_positive = 0.0
    index = 0

    while index < len(sorted_pairs):
        tie_end = index + 1
        while tie_end < len(sorted_pairs) and sorted_pairs[tie_end][0] == sorted_pairs[index][0]:
            tie_end += 1

        average_rank = (index + 1 + tie_end) / 2
        positive_in_tie = sum(label for _, label in sorted_pairs[index:tie_end])
        rank_sum_for_positive += positive_in_tie * average_rank
        index = tie_end

    mann_whitney_u = rank_sum_for_positive - (positive_count * (positive_count + 1) / 2)
    return mann_whitney_u / (positive_count * negative_count)


def _validate_threshold(value: float, field_name: str) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise MetricValidationError(f"{field_name} must be a finite numeric value.")
    if not math.isfinite(float(value)):
        raise MetricValidationError(f"{field_name} must be a finite numeric value.")
