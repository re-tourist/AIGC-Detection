from __future__ import annotations

import math
from collections import defaultdict
from typing import Any, Mapping, Sequence

from aigc_detection.data import NormalizedSample

P2_BLOCKED_DIMENSIONS = ("region_type", "subtlety", "edit_area_ratio")


class MetricValidationError(ValueError):
    """Raised when samples or scores cannot produce a valid M1 metric report."""


def build_metric_report(
    samples: Sequence[NormalizedSample],
    scores_by_sample_id: Mapping[str, float],
    threshold: float = 0.5,
) -> dict[str, Any]:
    """Build the frozen M1 metric report.

    M1 only requires:
    - overall P0 metrics
    - grouped by task_type
    - grouped by degradation when explicit metadata exists
    - blocked statuses for P2 slice dimensions
    """

    normalized_scores = _validate_scores(samples, scores_by_sample_id, threshold)

    return {
        "overall": _summarize_group(samples, normalized_scores, threshold),
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


def _validate_scores(
    samples: Sequence[NormalizedSample],
    scores_by_sample_id: Mapping[str, float],
    threshold: float,
) -> dict[str, float]:
    if not samples:
        raise MetricValidationError("Cannot compute metrics without normalized samples.")
    if not isinstance(scores_by_sample_id, Mapping):
        raise MetricValidationError("scores_by_sample_id must be a mapping keyed by sample_id.")
    if not isinstance(threshold, (int, float)) or isinstance(threshold, bool):
        raise MetricValidationError("threshold must be a finite numeric value.")
    if not math.isfinite(float(threshold)):
        raise MetricValidationError("threshold must be a finite numeric value.")

    sample_ids: list[str] = []
    for sample in samples:
        sample_ids.append(sample.sample_id)

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


def _summarize_group(
    samples: Sequence[NormalizedSample],
    scores_by_sample_id: Mapping[str, float],
    threshold: float,
) -> dict[str, Any]:
    labels = [sample.label for sample in samples]
    scores = [scores_by_sample_id[sample.sample_id] for sample in samples]
    positive_count = sum(labels)
    negative_count = len(labels) - positive_count
    notes: list[str] = []

    auroc = _compute_auroc(labels, scores)
    if auroc is None:
        notes.append("AUROC is undefined because both label classes are not present.")

    fake_recall = _compute_fake_recall(labels, scores, threshold)
    if fake_recall is None:
        notes.append("fake_recall is undefined because the group contains no positive labels.")

    return {
        "status": "ok",
        "sample_count": len(samples),
        "positive_count": positive_count,
        "negative_count": negative_count,
        "metrics": {
            "auroc": auroc,
            "accuracy": _compute_accuracy(labels, scores, threshold),
            "fake_recall": fake_recall,
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
            group_name: _summarize_group(group_samples, scores_by_sample_id, threshold)
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


def _compute_accuracy(labels: Sequence[int], scores: Sequence[float], threshold: float) -> float:
    predictions = [1 if score >= threshold else 0 for score in scores]
    correct = sum(1 for label, prediction in zip(labels, predictions) if label == prediction)
    return correct / len(labels)


def _compute_fake_recall(
    labels: Sequence[int], scores: Sequence[float], threshold: float
) -> float | None:
    positive_indices = [index for index, label in enumerate(labels) if label == 1]
    if not positive_indices:
        return None
    true_positives = sum(1 for index in positive_indices if scores[index] >= threshold)
    return true_positives / len(positive_indices)


def _compute_auroc(labels: Sequence[int], scores: Sequence[float]) -> float | None:
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
