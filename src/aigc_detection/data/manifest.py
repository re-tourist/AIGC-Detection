from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
from typing import Any

from .schema import (
    FORBIDDEN_RAW_FIELDS,
    OPTIONAL_RAW_FIELDS,
    REQUIRED_RAW_FIELDS,
    SUPPORTED_TASK_TYPES,
    NormalizedSample,
)


class ManifestValidationError(ValueError):
    """Raised when a raw manifest record violates the frozen M1 contract."""


def load_manifest(manifest_path: str | Path) -> list[NormalizedSample]:
    path = Path(manifest_path)
    if not path.exists():
        raise ManifestValidationError(f"Manifest file does not exist: {path}")
    if path.suffix != ".jsonl":
        raise ManifestValidationError(
            f"Manifest must be a .jsonl file, got: {path.name}"
        )

    samples: list[NormalizedSample] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ManifestValidationError(
                    f"Invalid JSON at {path}:{line_number}: {exc.msg}"
                ) from exc
            samples.append(_normalize_record(record, path.parent, line_number))

    if not samples:
        raise ManifestValidationError(f"Manifest contains no sample records: {path}")
    return samples


def _normalize_record(
    record: dict[str, Any], manifest_dir: Path, line_number: int
) -> NormalizedSample:
    _validate_record_shape(record, line_number)

    task_type = _require_string(record["task_type"], "task_type", line_number)
    if task_type not in SUPPORTED_TASK_TYPES:
        supported = ", ".join(SUPPORTED_TASK_TYPES)
        raise ManifestValidationError(
            f"Unsupported task_type at line {line_number}: {task_type!r}. "
            f"Expected one of: {supported}"
        )

    label = _coerce_label(record["label"], line_number)
    meta = record.get("meta") or {}
    if not isinstance(meta, dict):
        raise ManifestValidationError(
            f"meta must be an object at line {line_number}, got {type(meta).__name__}"
        )
    image_path = _resolve_existing_path(
        record["image_path"], manifest_dir, "image_path", line_number, meta=meta
    )
    mask_path = _resolve_optional_path(
        record.get("mask_path"), manifest_dir, "mask_path", line_number, meta=meta
    )

    return NormalizedSample(
        sample_id=_require_string(record["sample_id"], "sample_id", line_number),
        task_type=task_type,
        split=_require_string(record["split"], "split", line_number),
        image_path=image_path,
        label=label,
        mask_path=mask_path,
        generator_id=_optional_string(record.get("generator_id"), "generator_id", line_number),
        source_id=_optional_string(record.get("source_id"), "source_id", line_number),
        degradation=_optional_string(record.get("degradation"), "degradation", line_number),
        region_type=_optional_string(record.get("region_type"), "region_type", line_number),
        subtlety=_optional_string(record.get("subtlety"), "subtlety", line_number),
        meta=meta,
        derived_fields={},
    )


def _validate_record_shape(record: Any, line_number: int) -> None:
    if not isinstance(record, dict):
        raise ManifestValidationError(
            f"Each manifest record must be an object at line {line_number}"
        )

    missing_fields = [field for field in REQUIRED_RAW_FIELDS if field not in record]
    if missing_fields:
        raise ManifestValidationError(
            f"Missing required raw fields at line {line_number}: {', '.join(missing_fields)}"
        )

    for forbidden in FORBIDDEN_RAW_FIELDS:
        if forbidden in record:
            raise ManifestValidationError(
                f"Derived field {forbidden!r} must not appear as a raw manifest field "
                f"at line {line_number}"
            )

    allowed_fields = set(REQUIRED_RAW_FIELDS) | set(OPTIONAL_RAW_FIELDS)
    unknown_fields = sorted(set(record) - allowed_fields)
    if unknown_fields:
        raise ManifestValidationError(
            f"Unknown raw manifest fields at line {line_number}: {', '.join(unknown_fields)}"
        )


def _coerce_label(value: Any, line_number: int) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int) and value in (0, 1):
        return value
    raise ManifestValidationError(
        f"label must be 0/1 at line {line_number}, got {value!r}"
    )


def _require_string(value: Any, field_name: str, line_number: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ManifestValidationError(
            f"{field_name} must be a non-empty string at line {line_number}"
        )
    return value.strip()


def _optional_string(value: Any, field_name: str, line_number: int) -> str | None:
    if value is None:
        return None
    return _require_string(value, field_name, line_number)


def _resolve_existing_path(
    raw_value: Any,
    manifest_dir: Path,
    field_name: str,
    line_number: int,
    *,
    meta: dict[str, Any] | None = None,
) -> Path:
    raw_path = _require_string(raw_value, field_name, line_number)
    candidate_paths: list[Path] = []

    raw_path_obj = Path(raw_path)
    if raw_path_obj.is_absolute():
        candidate_paths.append(raw_path_obj.resolve())
    else:
        candidate_paths.append((manifest_dir / raw_path_obj).resolve())

    remapped_path = _remap_missing_path(
        raw_value=raw_path,
        raw_path=raw_path_obj,
        manifest_dir=manifest_dir,
        meta=meta,
    )
    if remapped_path is not None:
        candidate_paths.append(remapped_path)

    for path in candidate_paths:
        if path.exists():
            return path

    raise ManifestValidationError(
        f"{field_name} does not exist at line {line_number}: {candidate_paths[0]}"
    )


def _resolve_optional_path(
    raw_value: Any,
    manifest_dir: Path,
    field_name: str,
    line_number: int,
    *,
    meta: dict[str, Any] | None = None,
) -> Path | None:
    if raw_value is None:
        return None
    return _resolve_existing_path(
        raw_value,
        manifest_dir,
        field_name,
        line_number,
        meta=meta,
    )


def _remap_missing_path(
    *,
    raw_value: str,
    raw_path: Path,
    manifest_dir: Path,
    meta: dict[str, Any] | None,
) -> Path | None:
    if not isinstance(meta, dict):
        return None

    source_root_raw = meta.get("source_root")
    if not isinstance(source_root_raw, str) or not source_root_raw.strip():
        return None

    source_root_text = source_root_raw.strip()
    source_root_parts = [
        part for part in PurePosixPath(source_root_text).parts if part not in {"/", "\\"}
    ]
    layout_suffixes: list[tuple[str, ...]] = []
    for size in range(min(3, len(source_root_parts)), 0, -1):
        suffix = tuple(source_root_parts[-size:])
        if suffix not in layout_suffixes:
            layout_suffixes.append(suffix)

    try:
        if raw_value.startswith(("/", "\\")) or source_root_text.startswith(("/", "\\")):
            relative_suffix = PurePosixPath(raw_value).relative_to(PurePosixPath(source_root_text))
            relative_parts = relative_suffix.parts
        else:
            source_root = Path(source_root_text)
            relative_suffix = raw_path.relative_to(source_root)
            relative_parts = relative_suffix.parts
    except ValueError:
        return None

    for ancestor in (manifest_dir, *manifest_dir.parents):
        for layout_suffix in layout_suffixes:
            candidate_root = ancestor.joinpath(*layout_suffix)
            if not candidate_root.is_dir():
                continue
            candidate_path = candidate_root.joinpath(*relative_parts).resolve()
            if candidate_path.exists():
                return candidate_path

    return None

