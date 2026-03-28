from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REQUIRED_RAW_FIELDS = (
    "sample_id",
    "task_type",
    "split",
    "image_path",
    "label",
)

OPTIONAL_RAW_FIELDS = (
    "mask_path",
    "generator_id",
    "source_id",
    "degradation",
    "region_type",
    "subtlety",
    "meta",
)

FORBIDDEN_RAW_FIELDS = ("edit_area_ratio",)

SUPPORTED_TASK_TYPES = ("localized_edit", "full_image_fake")


@dataclass(frozen=True)
class NormalizedSample:
    sample_id: str
    task_type: str
    split: str
    image_path: Path
    label: int
    mask_path: Path | None = None
    generator_id: str | None = None
    source_id: str | None = None
    degradation: str | None = None
    region_type: str | None = None
    subtlety: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)
    derived_fields: dict[str, Any] = field(default_factory=dict)

    def has_explicit_metadata(self, field_name: str) -> bool:
        value = getattr(self, field_name, None)
        return value is not None and value != ""

