from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


class BRGenPreparationError(ValueError):
    """Raised when the local BR-Gen source drop cannot support rehearsal prep."""


@dataclass(frozen=True)
class BRGenRehearsalArtifacts:
    manifest_path: Path
    predictions_path: Path
    sample_count: int
    skipped_missing_mask_count: int


def prepare_br_gen_rehearsal(
    source_root: str | Path,
    output_root: str | Path,
    dummy_score: float = 0.99,
) -> BRGenRehearsalArtifacts:
    source_root = Path(source_root).resolve()
    output_root = Path(output_root).resolve()

    forged_root = source_root / "Forged"
    mask_root = source_root / "Mask"

    if not forged_root.exists():
        raise BRGenPreparationError(f"Missing Forged directory: {forged_root}")
    if not mask_root.exists():
        raise BRGenPreparationError(f"Missing Mask directory: {mask_root}")

    manifest_dir = output_root / "manifest"
    predictions_dir = output_root / "predictions"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    predictions_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = manifest_dir / "manifest.jsonl"
    predictions_path = predictions_dir / "dummy_predictions.jsonl"

    records: list[dict[str, object]] = []
    prediction_records: list[dict[str, object]] = []
    skipped_missing_mask_count = 0

    for forged_path in sorted(forged_root.glob("*/*/*/*.png")):
        relative_parts = forged_path.relative_to(forged_root).parts
        if len(relative_parts) != 4:
            continue

        generator_id, region_name, source_id, filename = relative_parts
        mask_path = mask_root / region_name / source_id / filename
        if not mask_path.exists():
            skipped_missing_mask_count += 1
            continue

        sample_id = "__".join(
            (
                _normalize_token(generator_id),
                _normalize_token(region_name),
                _normalize_token(source_id),
                _normalize_token(Path(filename).stem),
            )
        )

        record = {
            "sample_id": sample_id,
            "task_type": "localized_edit",
            "split": "rehearsal",
            "image_path": _relative_path(forged_path, manifest_dir),
            "label": 1,
            "mask_path": _relative_path(mask_path, manifest_dir),
            "generator_id": generator_id,
            "source_id": source_id,
            "region_type": region_name.lower(),
            "meta": {
                "source_drop_root": str(source_root),
                "source_dataset": "BR-Gen",
                "rehearsal_kind": "positive_only_source_drop",
            },
        }
        prediction_record = {
            "sample_id": sample_id,
            "score": dummy_score,
            "meta": {
                "source": "dummy_rehearsal_score",
            },
        }

        records.append(record)
        prediction_records.append(prediction_record)

    if not records:
        raise BRGenPreparationError(
            "No BR-Gen rehearsal records were generated. Check the source drop layout and masks."
        )

    _write_jsonl(manifest_path, records)
    _write_jsonl(predictions_path, prediction_records)

    return BRGenRehearsalArtifacts(
        manifest_path=manifest_path,
        predictions_path=predictions_path,
        sample_count=len(records),
        skipped_missing_mask_count=skipped_missing_mask_count,
    )


def _normalize_token(value: str) -> str:
    return value.strip().replace(" ", "_").replace("-", "_").lower()


def _relative_path(target_path: Path, anchor_dir: Path) -> str:
    return os.path.relpath(
        Path(target_path).resolve(),
        start=Path(anchor_dir).resolve(),
    ).replace("\\", "/")


def _write_jsonl(path: Path, records: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
