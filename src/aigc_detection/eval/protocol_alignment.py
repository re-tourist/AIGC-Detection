from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
from PIL import Image

from aigc_detection.data import NormalizedSample
from aigc_detection.metrics import (
    PAPER_STYLE_ALIGNMENT_THRESHOLD,
    summarize_sample_group,
)

GENERATOR_FAMILY_MAPPING = {
    "lama": "GAN",
    "mat": "GAN",
    "brushnet": "Diffusion",
    "powerpaint": "Diffusion",
    "sdxl": "Diffusion",
}
REPO_FROZEN_ALIGNMENT_BINS = {
    "small_lt": 0.05,
    "medium_gte": 0.05,
    "medium_lt": 0.20,
    "large_gte": 0.20,
}
PAPER_STYLE_THRESHOLD_CONTRACT_NOTE = (
    "paper_style_threshold=0.5 is a repo-frozen M6 alignment contract used to construct "
    "BR-Gen-style Recall@50 reporting. It is not claimed as a reconstruction of unpublished "
    "paper implementation details."
)
IOU_DEFERRED_REASON = (
    "IoU remains deferred because the repo does not expose a stable mask-prediction path or "
    "a frozen localization evaluation contract for paper-comparable reporting."
)
MAIN_TABLE_HEADER = (
    "| Slice | Accuracy | AUROC | F1@paper | Recall@50 | Real R@50 | IoU | Status |"
)
MAIN_TABLE_RULE = "| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |"


@dataclass(frozen=True)
class ProtocolAlignmentArtifacts:
    overall_metrics_path: Path
    slice_metrics_json_path: Path
    slice_metrics_csv_path: Path
    paper_table_summary_path: Path
    protocol_alignment_audit_path: Path


def build_protocol_alignment_bundle(
    samples: Sequence[NormalizedSample],
    scores_by_sample_id: Mapping[str, float],
    *,
    legacy_threshold: float,
    evaluation_scope: str,
    paper_style_threshold: float = PAPER_STYLE_ALIGNMENT_THRESHOLD,
) -> dict[str, Any]:
    localized_samples = [sample for sample in samples if sample.task_type == "localized_edit"]
    clean_samples = [sample for sample in localized_samples if _normalize_degradation(sample.degradation) == "clean"]
    degraded_samples = [
        sample for sample in localized_samples if _normalize_degradation(sample.degradation) != "clean"
    ]
    clean_positive_samples = [sample for sample in clean_samples if sample.label == 1]
    clean_negative_samples = [sample for sample in clean_samples if sample.label == 0]
    positive_samples = [sample for sample in localized_samples if sample.label == 1]
    area_metadata = _build_area_metadata(positive_samples)
    family_groups, family_audit = _group_generator_family(clean_positive_samples)

    overall_row = _build_slice_row(
        "overall",
        "overall",
        summarize_sample_group(
            localized_samples,
            scores_by_sample_id,
            legacy_threshold=legacy_threshold,
            paper_style_threshold=paper_style_threshold,
        ),
        included_in_paper_main_table=True,
    )
    clean_row = _build_slice_row(
        "clean_vs_degraded",
        "clean",
        summarize_sample_group(
            clean_samples,
            scores_by_sample_id,
            legacy_threshold=legacy_threshold,
            paper_style_threshold=paper_style_threshold,
        ),
        included_in_paper_main_table=True,
    )
    degraded_row = _build_slice_row(
        "clean_vs_degraded",
        "degraded",
        summarize_sample_group(
            degraded_samples,
            scores_by_sample_id,
            legacy_threshold=legacy_threshold,
            paper_style_threshold=paper_style_threshold,
        ),
        included_in_paper_main_table=True,
        extra_notes=["Degraded is the union of all explicit non-clean degradations."],
    )

    rows: list[dict[str, Any]] = [overall_row, clean_row, degraded_row]
    rows.extend(
        _build_shared_negative_rows(
            dimension="generator_family",
            ordered_values=("GAN", "Diffusion"),
            grouped_positive_samples=family_groups["supported"],
            negative_samples=clean_negative_samples,
            scores_by_sample_id=scores_by_sample_id,
            legacy_threshold=legacy_threshold,
            paper_style_threshold=paper_style_threshold,
            extra_notes=[
                "generator_family is derived from canonicalized generator_id.",
                "This row uses the repo's clean-shared-negative slice contract and is partially aligned to the paper reporting grammar.",
            ],
        )
    )
    rows.extend(
        _build_excluded_generator_rows(
            family_audit=family_audit,
            negative_samples=clean_negative_samples,
            scores_by_sample_id=scores_by_sample_id,
            legacy_threshold=legacy_threshold,
            paper_style_threshold=paper_style_threshold,
        )
    )
    rows.extend(
        _build_shared_negative_rows(
            dimension="region_type",
            ordered_values=("background", "stuff"),
            grouped_positive_samples=_group_samples_by_field(clean_positive_samples, "region_type"),
            negative_samples=clean_negative_samples,
            scores_by_sample_id=scores_by_sample_id,
            legacy_threshold=legacy_threshold,
            paper_style_threshold=paper_style_threshold,
            extra_notes=[
                "This row uses the repo's clean-shared-negative slice contract and is partially aligned to the paper reporting grammar.",
            ],
        )
    )
    rows.extend(
        _build_shared_negative_rows(
            dimension="area_bin",
            ordered_values=("small", "medium", "large"),
            grouped_positive_samples=_group_samples_by_area_bin(clean_positive_samples, area_metadata),
            negative_samples=clean_negative_samples,
            scores_by_sample_id=scores_by_sample_id,
            legacy_threshold=legacy_threshold,
            paper_style_threshold=paper_style_threshold,
            extra_notes=[
                "area_bin uses repo_frozen_alignment_bins and aligns the paper naming grammar only.",
                "This row uses the repo's clean-shared-negative slice contract and is partially aligned to the paper reporting grammar.",
            ],
        )
    )
    rows.extend(
        _build_degradation_detail_rows(
            localized_samples=localized_samples,
            scores_by_sample_id=scores_by_sample_id,
            legacy_threshold=legacy_threshold,
            paper_style_threshold=paper_style_threshold,
        )
    )

    slice_payload = {
        "runner": "m6_br_gen_style_protocol_alignment",
        "evaluation_scope": evaluation_scope,
        "legacy_threshold": float(legacy_threshold),
        "paper_style_threshold": float(paper_style_threshold),
        "paper_style_threshold_contract_note": PAPER_STYLE_THRESHOLD_CONTRACT_NOTE,
        "rows": rows,
    }

    audit_payload = _build_audit_payload(
        evaluation_scope=evaluation_scope,
        family_audit=family_audit,
    )
    overall_payload = {
        "runner": "m6_br_gen_style_protocol_alignment",
        "evaluation_scope": evaluation_scope,
        "legacy_threshold": float(legacy_threshold),
        "paper_style_threshold": float(paper_style_threshold),
        "paper_style_threshold_contract_note": PAPER_STYLE_THRESHOLD_CONTRACT_NOTE,
        "legacy_fake_recall_value": overall_row["legacy_fake_recall_value"],
        "paper_manipulated_recall_at_0_5": overall_row["paper_manipulated_recall_at_0_5"],
        "legacy_equals_paper_manipulated_recall": overall_row[
            "legacy_equals_paper_manipulated_recall"
        ],
        "f1_at_paper_style_threshold": overall_row["f1_at_paper_style_threshold"],
        "paper_real_recall_at_0_5": overall_row["paper_real_recall_at_0_5"],
        "accuracy": overall_row["accuracy"],
        "auroc": overall_row["auroc"],
        "overall": overall_row,
        "clean": clean_row,
        "degraded": degraded_row,
        "iou": {
            "value": None,
            "status": "deferred",
            "reason": IOU_DEFERRED_REASON,
        },
    }

    return {
        "overall_metrics": overall_payload,
        "slice_metrics": slice_payload,
        "protocol_alignment_audit": audit_payload,
        "paper_table_summary_markdown": render_protocol_alignment_markdown(
            overall_metrics=overall_payload,
            slice_metrics=slice_payload,
            protocol_alignment_audit=audit_payload,
        ),
    }


def write_protocol_alignment_artifacts(
    output_dir: str | Path,
    bundle: Mapping[str, Any],
) -> ProtocolAlignmentArtifacts:
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    overall_metrics_path = output_dir / "overall_metrics.json"
    slice_metrics_json_path = output_dir / "slice_metrics.json"
    slice_metrics_csv_path = output_dir / "slice_metrics.csv"
    paper_table_summary_path = output_dir / "paper_table_summary.md"
    protocol_alignment_audit_path = output_dir / "protocol_alignment_audit.json"

    _write_json(overall_metrics_path, bundle["overall_metrics"])
    _write_json(slice_metrics_json_path, bundle["slice_metrics"])
    _write_slice_metrics_csv(slice_metrics_csv_path, bundle["slice_metrics"]["rows"])
    paper_table_summary_path.write_text(bundle["paper_table_summary_markdown"], encoding="utf-8")
    _write_json(protocol_alignment_audit_path, bundle["protocol_alignment_audit"])

    return ProtocolAlignmentArtifacts(
        overall_metrics_path=overall_metrics_path,
        slice_metrics_json_path=slice_metrics_json_path,
        slice_metrics_csv_path=slice_metrics_csv_path,
        paper_table_summary_path=paper_table_summary_path,
        protocol_alignment_audit_path=protocol_alignment_audit_path,
    )


def render_protocol_alignment_markdown(
    *,
    overall_metrics: Mapping[str, Any],
    slice_metrics: Mapping[str, Any],
    protocol_alignment_audit: Mapping[str, Any],
) -> str:
    rows = list(slice_metrics["rows"])
    lines = [
        "# M6 BR-Gen-style Evaluation Protocol Alignment Summary",
        "",
        "- Current readout is image-level localized sensitivity reporting.",
        "- Current evidence comes from the restricted pilot diagnostic pipeline.",
        "- This is not a full localization benchmark.",
        f"- Evaluation scope: `{overall_metrics['evaluation_scope']}`",
        f"- Legacy threshold: `{overall_metrics['legacy_threshold']}`",
        f"- Paper-style threshold: `{overall_metrics['paper_style_threshold']}`",
        "",
        "## Overall Summary",
        MAIN_TABLE_HEADER,
        MAIN_TABLE_RULE,
        _format_table_row(overall_metrics["overall"]),
        "",
        "## Clean vs Degraded",
        MAIN_TABLE_HEADER,
        MAIN_TABLE_RULE,
        _format_table_row(overall_metrics["clean"]),
        _format_table_row(overall_metrics["degraded"]),
        "",
        "## Split A: GAN / Diffusion",
        MAIN_TABLE_HEADER,
        MAIN_TABLE_RULE,
    ]
    for row in _main_table_rows(rows, dimension="generator_family"):
        lines.append(_format_table_row(row))

    lines.extend(
        [
            "",
            "## Split B: Background / Stuff",
            MAIN_TABLE_HEADER,
            MAIN_TABLE_RULE,
        ]
    )
    for row in _main_table_rows(rows, dimension="region_type"):
        lines.append(_format_table_row(row))

    lines.extend(
        [
            "",
            "## Area Bins",
            MAIN_TABLE_HEADER,
            MAIN_TABLE_RULE,
        ]
    )
    for row in _main_table_rows(rows, dimension="area_bin"):
        lines.append(_format_table_row(row))

    lines.extend(
        [
            "",
            "## Degradation Detail",
            MAIN_TABLE_HEADER,
            MAIN_TABLE_RULE,
        ]
    )
    for row in _detail_rows(rows, dimension="degradation_detail"):
        lines.append(_format_table_row(row))

    lines.extend(
        [
            "",
            "## Alignment and Deferred Notes",
            f"- IoU: `N/A (deferred)` because {IOU_DEFERRED_REASON}",
            f"- Threshold contract: {protocol_alignment_audit['paper_style_threshold_contract_note']}",
            f"- repo_frozen_alignment_bins: `{protocol_alignment_audit['repo_frozen_alignment_bins']}`",
            f"- Excluded Split A counts: `{protocol_alignment_audit['excluded_counts']}`",
        ]
    )
    for item in protocol_alignment_audit["partially_aligned"]:
        lines.append(f"- Partially aligned: {item}")
    for item in protocol_alignment_audit["deferred"]:
        lines.append(f"- Deferred: {item['item']} ({item['reason']})")
    return "\n".join(lines) + "\n"


def _build_audit_payload(
    *,
    evaluation_scope: str,
    family_audit: Mapping[str, Any],
) -> dict[str, Any]:
    excluded_counts = {
        "unknown_generator_count": family_audit["unknown_generator_count"],
        "unsupported_generator_count": family_audit["unsupported_generator_count"],
        "excluded_from_split_a_count": family_audit["excluded_from_split_a_count"],
        "excluded_generator_ids": family_audit["excluded_generator_ids"],
    }
    return {
        "runner": "m6_br_gen_style_protocol_alignment",
        "evaluation_scope": evaluation_scope,
        "fully_aligned": [
            "Legacy metrics remain additive and preserved.",
            "Paper-style F1 / Recall@50 style reporting is exported as JSON/CSV/Markdown artifacts.",
            "Split A and Split B naming grammar is aligned for reporting.",
            "clean/degraded dual reporting is exported together with degradation-detail rows.",
        ],
        "partially_aligned": [
            "generator_family is derived from canonicalized generator_id rather than stored as raw manifest metadata.",
            "area_bin uses repo_frozen_alignment_bins and aligns the paper naming grammar only.",
            "Conditioned slices use the repo's clean-shared-negative contract instead of claiming the paper's original benchmark pairing.",
            "The restricted pilot remains diagnostic evidence and is not promoted to a formal benchmark claim.",
        ],
        "deferred": [
            {
                "item": "IoU",
                "reason": IOU_DEFERRED_REASON,
            }
        ],
        "blocked_reasons": [IOU_DEFERRED_REASON],
        "excluded_counts": excluded_counts,
        "generator_family_mapping": {
            "canonicalization_rule": "lowercase(trim(raw_generator_id)).remove('-', '_', ' ')",
            "mapping": dict(GENERATOR_FAMILY_MAPPING),
            "supported_families": ["GAN", "Diffusion"],
        },
        "repo_frozen_alignment_bins": dict(REPO_FROZEN_ALIGNMENT_BINS),
        "paper_style_threshold_contract_note": PAPER_STYLE_THRESHOLD_CONTRACT_NOTE,
    }


def _build_shared_negative_rows(
    *,
    dimension: str,
    ordered_values: Sequence[str],
    grouped_positive_samples: Mapping[str, Sequence[NormalizedSample]],
    negative_samples: Sequence[NormalizedSample],
    scores_by_sample_id: Mapping[str, float],
    legacy_threshold: float,
    paper_style_threshold: float,
    extra_notes: Sequence[str],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for value in ordered_values:
        positive_samples = list(grouped_positive_samples.get(value, []))
        summary = _summarize_shared_negative_slice(
            positive_samples=positive_samples,
            negative_samples=negative_samples,
            scores_by_sample_id=scores_by_sample_id,
            legacy_threshold=legacy_threshold,
            paper_style_threshold=paper_style_threshold,
            empty_reason=f"No clean positive samples are available for {dimension}={value}.",
        )
        rows.append(
            _build_slice_row(
                dimension,
                value,
                summary,
                included_in_paper_main_table=True,
                extra_notes=list(extra_notes),
            )
        )
    return rows


def _build_excluded_generator_rows(
    *,
    family_audit: Mapping[str, Any],
    negative_samples: Sequence[NormalizedSample],
    scores_by_sample_id: Mapping[str, float],
    legacy_threshold: float,
    paper_style_threshold: float,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for excluded_value in ("unknown", "unsupported"):
        positive_samples = list(family_audit["excluded_groups"].get(excluded_value, []))
        if not positive_samples:
            continue
        summary = _summarize_shared_negative_slice(
            positive_samples=positive_samples,
            negative_samples=negative_samples,
            scores_by_sample_id=scores_by_sample_id,
            legacy_threshold=legacy_threshold,
            paper_style_threshold=paper_style_threshold,
            empty_reason=f"No clean positive samples are available for generator_family={excluded_value}.",
        )
        rows.append(
            _build_slice_row(
                "generator_family",
                excluded_value,
                summary,
                included_in_paper_main_table=False,
                status_override="excluded",
                extra_notes=[
                    "Excluded from the Split A paper main table because the canonicalized generator_id does not map to a supported GAN/Diffusion family.",
                ],
            )
        )
    return rows


def _build_degradation_detail_rows(
    *,
    localized_samples: Sequence[NormalizedSample],
    scores_by_sample_id: Mapping[str, float],
    legacy_threshold: float,
    paper_style_threshold: float,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    grouped = _group_samples_by_degradation(localized_samples)
    for degradation in ("clean", "jpeg", "resize", "blur", "crop"):
        summary = summarize_sample_group(
            grouped.get(degradation, []),
            scores_by_sample_id,
            legacy_threshold=legacy_threshold,
            paper_style_threshold=paper_style_threshold,
        )
        rows.append(
            _build_slice_row(
                "degradation_detail",
                degradation,
                summary,
                included_in_paper_main_table=False,
                extra_notes=[
                    "Degradation detail rows are always exported when explicit metadata is present.",
                ],
            )
        )
    return rows


def _summarize_shared_negative_slice(
    *,
    positive_samples: Sequence[NormalizedSample],
    negative_samples: Sequence[NormalizedSample],
    scores_by_sample_id: Mapping[str, float],
    legacy_threshold: float,
    paper_style_threshold: float,
    empty_reason: str,
) -> dict[str, Any]:
    if not positive_samples:
        summary = summarize_sample_group(
            [],
            scores_by_sample_id,
            legacy_threshold=legacy_threshold,
            paper_style_threshold=paper_style_threshold,
        )
        summary["notes"] = [empty_reason]
        return summary
    return summarize_sample_group(
        [*positive_samples, *negative_samples],
        scores_by_sample_id,
        legacy_threshold=legacy_threshold,
        paper_style_threshold=paper_style_threshold,
    )


def _build_slice_row(
    dimension: str,
    slice_value: str,
    summary: Mapping[str, Any],
    *,
    included_in_paper_main_table: bool,
    status_override: str | None = None,
    extra_notes: Sequence[str] | None = None,
) -> dict[str, Any]:
    notes = _dedupe_notes([*summary.get("notes", []), *(extra_notes or [])])
    metric_audit = summary.get("metric_audit", {})
    paper_metrics = summary.get("paper_metrics", {})
    status = status_override or _derive_row_status(summary)
    return {
        "dimension": dimension,
        "slice_value": slice_value,
        "sample_count": summary.get("sample_count"),
        "positive_count": summary.get("positive_count"),
        "negative_count": summary.get("negative_count"),
        "status": status,
        "notes": notes,
        "legacy_fake_recall_value": metric_audit.get("legacy_fake_recall_value"),
        "paper_manipulated_recall_at_0_5": metric_audit.get(
            "paper_manipulated_recall_at_0_5"
        ),
        "paper_real_recall_at_0_5": paper_metrics.get("paper_real_recall_at_0_5"),
        "f1_at_paper_style_threshold": paper_metrics.get("f1_at_paper_style_threshold"),
        "auroc": summary.get("metrics", {}).get("auroc"),
        "accuracy": summary.get("metrics", {}).get("accuracy"),
        "legacy_threshold": metric_audit.get("legacy_threshold"),
        "paper_style_threshold": metric_audit.get("paper_style_threshold"),
        "legacy_equals_paper_manipulated_recall": metric_audit.get(
            "legacy_equals_paper_manipulated_recall"
        ),
        "included_in_paper_main_table": included_in_paper_main_table,
    }


def _derive_row_status(summary: Mapping[str, Any]) -> str:
    if summary.get("status") == "empty_slice":
        return "empty_slice"
    if summary.get("metric_audit", {}).get("undefined_metric_names"):
        return "undefined_metric"
    return "ok"


def _group_generator_family(
    samples: Iterable[NormalizedSample],
) -> tuple[dict[str, dict[str, list[NormalizedSample]]], dict[str, Any]]:
    supported: dict[str, list[NormalizedSample]] = {"GAN": [], "Diffusion": []}
    excluded_groups: dict[str, list[NormalizedSample]] = {"unknown": [], "unsupported": []}
    excluded_generator_ids: set[str] = set()

    for sample in samples:
        family_info = _derive_generator_family(sample.generator_id)
        family = family_info["generator_family"]
        if family in supported:
            supported[family].append(sample)
            continue
        excluded_groups[family].append(sample)
        if family_info["raw_generator_id"] is not None:
            excluded_generator_ids.add(str(family_info["raw_generator_id"]))

    return (
        {"supported": supported, "excluded": excluded_groups},
        {
            "unknown_generator_count": len(excluded_groups["unknown"]),
            "unsupported_generator_count": len(excluded_groups["unsupported"]),
            "excluded_from_split_a_count": len(excluded_groups["unknown"])
            + len(excluded_groups["unsupported"]),
            "excluded_generator_ids": sorted(excluded_generator_ids),
            "excluded_groups": excluded_groups,
        },
    )


def _group_samples_by_field(
    samples: Iterable[NormalizedSample], field_name: str
) -> dict[str, list[NormalizedSample]]:
    grouped: dict[str, list[NormalizedSample]] = {}
    for sample in samples:
        value = getattr(sample, field_name)
        if value is None:
            continue
        grouped.setdefault(str(value).strip().lower(), []).append(sample)
    return grouped


def _group_samples_by_area_bin(
    samples: Iterable[NormalizedSample],
    area_metadata: Mapping[str, Mapping[str, Any]],
) -> dict[str, list[NormalizedSample]]:
    grouped: dict[str, list[NormalizedSample]] = {"small": [], "medium": [], "large": []}
    for sample in samples:
        metadata = area_metadata.get(sample.sample_id)
        if metadata is None:
            continue
        grouped[str(metadata["area_bin"])].append(sample)
    return grouped


def _group_samples_by_degradation(
    samples: Iterable[NormalizedSample],
) -> dict[str, list[NormalizedSample]]:
    grouped: dict[str, list[NormalizedSample]] = {}
    for sample in samples:
        grouped.setdefault(_normalize_degradation(sample.degradation), []).append(sample)
    return grouped


def _derive_generator_family(raw_generator_id: str | None) -> dict[str, str | None]:
    if raw_generator_id is None or not str(raw_generator_id).strip():
        return {
            "raw_generator_id": raw_generator_id,
            "canonical_generator_id": None,
            "generator_family": "unknown",
        }
    canonical_generator_id = (
        str(raw_generator_id).strip().lower().replace("-", "").replace("_", "").replace(" ", "")
    )
    return {
        "raw_generator_id": str(raw_generator_id),
        "canonical_generator_id": canonical_generator_id,
        "generator_family": GENERATOR_FAMILY_MAPPING.get(canonical_generator_id, "unsupported"),
    }


def _build_area_metadata(samples: Iterable[NormalizedSample]) -> dict[str, dict[str, Any]]:
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
            "area_bin": area_bin,
        }
    return metadata


def _compute_edit_area_ratio(mask_path: Path) -> float:
    with Image.open(mask_path) as image:
        array = np.asarray(image)

    if array.size == 0:
        raise ValueError(f"Mask is empty: {mask_path}")
    if array.ndim == 3:
        foreground = np.any(array > 0, axis=2)
    else:
        foreground = array > 0
    return float(foreground.sum() / foreground.size)


def _classify_area_bin(ratio: float) -> str:
    if ratio < REPO_FROZEN_ALIGNMENT_BINS["small_lt"]:
        return "small"
    if ratio < REPO_FROZEN_ALIGNMENT_BINS["medium_lt"]:
        return "medium"
    return "large"


def _normalize_degradation(value: str | None) -> str:
    if value is None or not str(value).strip():
        return "clean"
    return str(value).strip().lower()


def _main_table_rows(rows: Sequence[Mapping[str, Any]], *, dimension: str) -> list[Mapping[str, Any]]:
    return [
        row
        for row in rows
        if row["dimension"] == dimension and row["included_in_paper_main_table"]
    ]


def _detail_rows(rows: Sequence[Mapping[str, Any]], *, dimension: str) -> list[Mapping[str, Any]]:
    return [row for row in rows if row["dimension"] == dimension]


def _format_table_row(row: Mapping[str, Any]) -> str:
    return (
        f"| {row['slice_value']} | {_fmt(row['accuracy'])} | {_fmt(row['auroc'])} | "
        f"{_fmt(row['f1_at_paper_style_threshold'])} | "
        f"{_fmt(row['paper_manipulated_recall_at_0_5'])} | "
        f"{_fmt(row['paper_real_recall_at_0_5'])} | N/A (deferred) | {row['status']} |"
    )


def _fmt(value: Any) -> str:
    if value is None:
        return "N/A"
    return f"{float(value):.6f}"


def _dedupe_notes(notes: Iterable[str]) -> list[str]:
    deduped: list[str] = []
    for note in notes:
        text = str(note).strip()
        if not text or text in deduped:
            continue
        deduped.append(text)
    return deduped


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_slice_metrics_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "dimension",
                "slice_value",
                "sample_count",
                "positive_count",
                "negative_count",
                "status",
                "notes",
                "legacy_fake_recall_value",
                "paper_manipulated_recall_at_0_5",
                "paper_real_recall_at_0_5",
                "f1_at_paper_style_threshold",
                "auroc",
                "accuracy",
                "legacy_threshold",
                "paper_style_threshold",
                "legacy_equals_paper_manipulated_recall",
                "included_in_paper_main_table",
            ],
        )
        writer.writeheader()
        for row in rows:
            serialized_row = {
                **row,
                "notes": " | ".join(row.get("notes", [])) or "N/A",
            }
            for key, value in list(serialized_row.items()):
                if value is None:
                    serialized_row[key] = "N/A"
            writer.writerow(
                serialized_row
            )
