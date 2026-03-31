from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from aigc_detection.data import load_manifest

AlignmentStrategy = Literal["sample_id", "relative_path", "mapping_table"]
ScoreTransform = Literal["identity", "sigmoid", "one_minus", "negate"]


class CommunityForensicsAdapterError(ValueError):
    """Raised when Community Forensics outputs cannot be adapted to the repo contract."""


@dataclass(frozen=True)
class CommunityForensicsAdapterArtifacts:
    output_path: Path
    manifest_path: Path
    input_path: Path
    sample_count: int
    alignment_strategy: AlignmentStrategy
    score_transform: ScoreTransform


def adapt_community_forensics_predictions(
    *,
    manifest_path: str | Path,
    input_path: str | Path,
    output_path: str | Path,
    alignment_strategy: AlignmentStrategy = "sample_id",
    score_transform: ScoreTransform = "identity",
    mapping_table_path: str | Path | None = None,
    input_sample_id_field: str = "sample_id",
    input_path_field: str = "image_path",
    mapping_source_id_field: str = "source_id",
    score_field: str = "score",
) -> CommunityForensicsAdapterArtifacts:
    manifest_path = Path(manifest_path).resolve()
    input_path = Path(input_path).resolve()
    output_path = Path(output_path).resolve()

    samples = load_manifest(manifest_path)
    if not samples:
        raise CommunityForensicsAdapterError(f"Manifest contains no samples: {manifest_path}")

    manifest_dir = manifest_path.parent
    relative_path_root = _detect_relative_path_root(samples, manifest_dir)
    manifest_by_sample_id = {sample.sample_id: sample for sample in samples}
    manifest_by_rel_path = {
        _normalize_relative_path(sample.image_path, anchor_root=relative_path_root): sample.sample_id
        for sample in samples
    }
    mapping_table = _load_mapping_table(mapping_table_path) if mapping_table_path else {}

    predictions_by_sample_id: dict[str, float] = {}
    input_record_count = 0
    with input_path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise CommunityForensicsAdapterError(
                    f"Invalid JSON at {input_path}:{line_number}: {exc.msg}"
                ) from exc

            if not isinstance(record, dict):
                raise CommunityForensicsAdapterError(
                    f"Each input record must be an object at line {line_number}"
                )

            source_id = _resolve_source_id(
                record=record,
                alignment_strategy=alignment_strategy,
                input_sample_id_field=input_sample_id_field,
                input_path_field=input_path_field,
                mapping_source_id_field=mapping_source_id_field,
                mapping_table=mapping_table,
                manifest_by_rel_path=manifest_by_rel_path,
                relative_path_root=relative_path_root,
                line_number=line_number,
            )
            if source_id not in manifest_by_sample_id:
                raise CommunityForensicsAdapterError(
                    f"Adapter resolved unknown manifest sample_id at line {line_number}: {source_id!r}"
                )
            if source_id in predictions_by_sample_id:
                raise CommunityForensicsAdapterError(
                    f"Duplicate resolved sample_id at line {line_number}: {source_id!r}"
                )

            raw_score = _extract_score(record, score_field=score_field, line_number=line_number)
            predictions_by_sample_id[source_id] = _transform_score(
                raw_score, score_transform=score_transform
            )
            input_record_count += 1

    missing_sample_ids = sorted(set(manifest_by_sample_id) - set(predictions_by_sample_id))
    extra_sample_ids = sorted(set(predictions_by_sample_id) - set(manifest_by_sample_id))
    if missing_sample_ids or extra_sample_ids:
        details: list[str] = []
        if missing_sample_ids:
            details.append(
                f"missing sample_ids: {', '.join(missing_sample_ids[:5])}"
            )
        if extra_sample_ids:
            details.append(f"extra sample_ids: {', '.join(extra_sample_ids[:5])}")
        raise CommunityForensicsAdapterError(
            "Adapter predictions do not align exactly with the manifest: " + "; ".join(details)
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_records = []
    for sample in samples:
        output_records.append(
            {
                "sample_id": sample.sample_id,
                "score": predictions_by_sample_id[sample.sample_id],
                "meta": {
                    "adapter": "community_forensics",
                    "alignment_strategy": alignment_strategy,
                    "score_transform": score_transform,
                    "relative_path_root": str(relative_path_root),
                    "input_record_count": input_record_count,
                    "input_path": str(input_path),
                    "manifest_path": str(manifest_path),
                },
            }
        )

    _write_jsonl(output_path, output_records)
    return CommunityForensicsAdapterArtifacts(
        output_path=output_path,
        manifest_path=manifest_path,
        input_path=input_path,
        sample_count=len(output_records),
        alignment_strategy=alignment_strategy,
        score_transform=score_transform,
    )


def _resolve_source_id(
    *,
    record: dict[str, Any],
    alignment_strategy: AlignmentStrategy,
    input_sample_id_field: str,
    input_path_field: str,
    mapping_source_id_field: str,
    mapping_table: dict[str, str],
    manifest_by_rel_path: dict[str, str],
    relative_path_root: Path,
    line_number: int,
) -> str:
    if alignment_strategy == "sample_id":
        source_id = record.get(input_sample_id_field)
        if not isinstance(source_id, str) or not source_id.strip():
            raise CommunityForensicsAdapterError(
                f"{input_sample_id_field} must be a non-empty string at line {line_number}"
            )
        return source_id.strip()

    if alignment_strategy == "relative_path":
        raw_path = record.get(input_path_field)
        if not isinstance(raw_path, str) or not raw_path.strip():
            raise CommunityForensicsAdapterError(
                f"{input_path_field} must be a non-empty string at line {line_number}"
            )
        normalized_path = _normalize_relative_path(raw_path, anchor_root=relative_path_root)
        try:
            return manifest_by_rel_path[normalized_path]
        except KeyError as exc:
            raise CommunityForensicsAdapterError(
                f"No manifest sample matched relative path {normalized_path!r} at line {line_number}"
            ) from exc

    raw_source_id = record.get(mapping_source_id_field)
    if not isinstance(raw_source_id, str) or not raw_source_id.strip():
        raise CommunityForensicsAdapterError(
            f"{mapping_source_id_field} must be a non-empty string at line {line_number}"
        )
    source_id = raw_source_id.strip()
    try:
        return mapping_table[source_id]
    except KeyError as exc:
        raise CommunityForensicsAdapterError(
            f"No explicit mapping table entry for source_id {source_id!r} at line {line_number}"
        ) from exc


def _extract_score(record: dict[str, Any], *, score_field: str, line_number: int) -> float:
    if score_field not in record:
        raise CommunityForensicsAdapterError(
            f"Missing score field {score_field!r} at line {line_number}"
        )
    raw_score = record[score_field]
    if not isinstance(raw_score, (int, float)) or isinstance(raw_score, bool):
        raise CommunityForensicsAdapterError(
            f"Score field {score_field!r} must be numeric at line {line_number}, got {raw_score!r}"
        )
    score = float(raw_score)
    if not math.isfinite(score):
        raise CommunityForensicsAdapterError(
            f"Score field {score_field!r} must be finite at line {line_number}, got {raw_score!r}"
        )
    return score


def _transform_score(score: float, *, score_transform: ScoreTransform) -> float:
    if score_transform == "identity":
        transformed = score
    elif score_transform == "sigmoid":
        transformed = 1.0 / (1.0 + math.exp(-score))
    elif score_transform == "one_minus":
        transformed = 1.0 - score
    elif score_transform == "negate":
        transformed = -score
    else:  # pragma: no cover - exhaustive guard
        raise CommunityForensicsAdapterError(f"Unsupported score transform: {score_transform}")

    if not math.isfinite(transformed):
        raise CommunityForensicsAdapterError(
            f"Score transform {score_transform!r} produced a non-finite value: {transformed!r}"
        )
    return transformed


def _load_mapping_table(mapping_table_path: str | Path) -> dict[str, str]:
    path = Path(mapping_table_path).resolve()
    if not path.exists():
        raise CommunityForensicsAdapterError(f"Mapping table does not exist: {path}")
    if path.suffix != ".jsonl":
        raise CommunityForensicsAdapterError(
            f"Mapping table must be a .jsonl file, got: {path.name}"
        )

    mapping: dict[str, str] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise CommunityForensicsAdapterError(
                    f"Invalid JSON at {path}:{line_number}: {exc.msg}"
                ) from exc
            if not isinstance(record, dict):
                raise CommunityForensicsAdapterError(
                    f"Each mapping record must be an object at line {line_number}"
                )
            source_id = record.get("source_id")
            sample_id = record.get("sample_id")
            if not isinstance(source_id, str) or not source_id.strip():
                raise CommunityForensicsAdapterError(
                    f"Mapping record requires non-empty source_id at line {line_number}"
                )
            if not isinstance(sample_id, str) or not sample_id.strip():
                raise CommunityForensicsAdapterError(
                    f"Mapping record requires non-empty sample_id at line {line_number}"
                )
            normalized_source_id = source_id.strip()
            normalized_sample_id = sample_id.strip()
            if normalized_source_id in mapping:
                raise CommunityForensicsAdapterError(
                    f"Duplicate source_id in mapping table at line {line_number}: {normalized_source_id!r}"
                )
            mapping[normalized_source_id] = normalized_sample_id

    if not mapping:
        raise CommunityForensicsAdapterError(f"Mapping table contains no records: {path}")
    return mapping


def _detect_relative_path_root(
    samples: list[Any], manifest_dir: Path
) -> Path:
    candidate_roots: list[Path] = []
    for sample in samples:
        meta = sample.meta if isinstance(sample.meta, dict) else {}
        source_root = meta.get("source_drop_root")
        if isinstance(source_root, str) and source_root.strip():
            candidate_roots.append(Path(source_root).resolve())

    if candidate_roots:
        first_root = candidate_roots[0]
        if any(root != first_root for root in candidate_roots[1:]):
            raise CommunityForensicsAdapterError(
                "Manifest samples disagree on source_drop_root"
            )
        return first_root

    return manifest_dir.resolve()


def _normalize_relative_path(raw_path: str | Path, *, anchor_root: Path | None) -> str:
    path = Path(str(raw_path).strip().replace("\\", "/"))
    if not str(path):
        raise CommunityForensicsAdapterError("Relative path must not be empty")

    if path.is_absolute():
        if anchor_root is None:
            raise CommunityForensicsAdapterError(
                f"Relative path must be relative unless an anchor root is provided: {raw_path!r}"
            )
        try:
            path = path.resolve().relative_to(anchor_root.resolve())
        except ValueError as exc:
            raise CommunityForensicsAdapterError(
                f"Absolute path {raw_path!r} is not under anchor root {anchor_root}"
            ) from exc
    else:
        while str(path).startswith("./"):
            path = Path(str(path)[2:])
        if ".." in path.parts:
            raise CommunityForensicsAdapterError(
                f"Relative path must not contain parent traversal: {raw_path!r}"
            )

    normalized = path.as_posix().lstrip("/")
    if not normalized:
        raise CommunityForensicsAdapterError("Relative path normalization produced an empty path")
    if normalized.startswith(".."):
        raise CommunityForensicsAdapterError(
            f"Relative path must not escape the anchor root: {raw_path!r}"
        )
    return normalized


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
