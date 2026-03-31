from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


class PredictionValidationError(ValueError):
    """Raised when a prediction input file violates the minimal M1 runner contract."""


def load_prediction_scores(predictions_path: str | Path) -> dict[str, float]:
    path = Path(predictions_path)
    if not path.exists():
        raise PredictionValidationError(f"Prediction file does not exist: {path}")
    if path.suffix != ".jsonl":
        raise PredictionValidationError(
            f"Prediction file must be a .jsonl file, got: {path.name}"
        )

    scores_by_sample_id: dict[str, float] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise PredictionValidationError(
                    f"Invalid JSON at {path}:{line_number}: {exc.msg}"
                ) from exc
            sample_id, score = _normalize_record(record, line_number)
            if sample_id in scores_by_sample_id:
                raise PredictionValidationError(
                    f"Duplicate prediction sample_id at line {line_number}: {sample_id!r}"
                )
            scores_by_sample_id[sample_id] = score

    if not scores_by_sample_id:
        raise PredictionValidationError(f"Prediction file contains no records: {path}")
    return scores_by_sample_id


def _normalize_record(record: Any, line_number: int) -> tuple[str, float]:
    if not isinstance(record, dict):
        raise PredictionValidationError(
            f"Each prediction record must be an object at line {line_number}"
        )

    allowed_fields = {"sample_id", "score", "meta"}
    unknown_fields = sorted(set(record) - allowed_fields)
    if unknown_fields:
        raise PredictionValidationError(
            f"Unknown prediction fields at line {line_number}: {', '.join(unknown_fields)}"
        )

    if "sample_id" not in record or "score" not in record:
        raise PredictionValidationError(
            f"Prediction records require sample_id and score at line {line_number}"
        )

    sample_id = record["sample_id"]
    if not isinstance(sample_id, str) or not sample_id.strip():
        raise PredictionValidationError(
            f"sample_id must be a non-empty string at line {line_number}"
        )

    score = record["score"]
    if not isinstance(score, (int, float)) or isinstance(score, bool):
        raise PredictionValidationError(
            f"score must be numeric at line {line_number}, got {score!r}"
        )
    score = float(score)
    if not math.isfinite(score):
        raise PredictionValidationError(
            f"score must be finite at line {line_number}, got {score!r}"
        )

    meta = record.get("meta")
    if meta is not None and not isinstance(meta, dict):
        raise PredictionValidationError(
            f"meta must be an object at line {line_number}, got {type(meta).__name__}"
        )

    return sample_id.strip(), score
