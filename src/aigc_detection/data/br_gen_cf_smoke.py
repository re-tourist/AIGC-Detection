from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from PIL import Image

from .coco_download import download_with_fallback
from .manifest import load_manifest


class BRGenCOSmokePreparationError(ValueError):
    """Raised when the BR-Gen COCO smoke fixture cannot be prepared."""


@dataclass(frozen=True)
class BRGenCOSmokeArtifacts:
    output_root: Path
    manifest_path: Path
    selection_path: Path
    copied_real_count: int
    copied_fake_count: int
    source_dataset: str


def prepare_br_gen_coco_smoke(
    *,
    manifest_path: str | Path,
    source_root: str | Path,
    output_root: str | Path,
    source_dataset: str = "COCO",
    real_image_list_path: str | Path | None = None,
    real_image_download_base_url: str = "http://images.cocodataset.org/train2017",
) -> BRGenCOSmokeArtifacts:
    manifest_path = Path(manifest_path).resolve()
    source_root = Path(source_root).resolve()
    output_root = Path(output_root).resolve()

    if real_image_list_path is None:
        real_image_list_path = source_root / "RealImage" / source_dataset / f"{source_dataset}_image_list.txt"
    else:
        real_image_list_path = Path(real_image_list_path).resolve()

    if not manifest_path.exists():
        raise BRGenCOSmokePreparationError(f"Manifest does not exist: {manifest_path}")
    if not real_image_list_path.exists():
        raise BRGenCOSmokePreparationError(
            f"Real-image list does not exist for {source_dataset}: {real_image_list_path}"
        )

    samples = load_manifest(manifest_path)
    candidate_fake_samples = [sample for sample in samples if sample.source_id == source_dataset]
    if not candidate_fake_samples:
        raise BRGenCOSmokePreparationError(
            f"No manifest samples found with source_id={source_dataset!r} in {manifest_path}"
        )

    fake_samples = [sample for sample in candidate_fake_samples if _is_valid_image(sample.image_path)]
    if not fake_samples:
        raise BRGenCOSmokePreparationError(
            f"No readable manifest samples found with source_id={source_dataset!r} in {manifest_path}"
        )

    real_names = _read_nonempty_lines(real_image_list_path)
    if len(real_names) < len(fake_samples):
        raise BRGenCOSmokePreparationError(
            f"Real-image list for {source_dataset} has only {len(real_names)} files, "
            f"but the manifest needs {len(fake_samples)} real images"
        )

    if output_root.exists():
        shutil.rmtree(output_root)

    output_generator_root = output_root / source_dataset
    real_dir = output_generator_root / "real"
    fake_dir = output_generator_root / "fake"
    real_dir.mkdir(parents=True, exist_ok=True)
    fake_dir.mkdir(parents=True, exist_ok=True)

    selection_records: list[dict[str, object]] = []
    manifest_records: list[dict[str, object]] = []

    for index, sample in enumerate(fake_samples):
        source_fake_path = sample.image_path
        if not _is_valid_image(source_fake_path):
            raise BRGenCOSmokePreparationError(
                f"Fake source image is not readable: {source_fake_path}"
            )

        dest_fake_name = f"fake__{sample.sample_id}__{source_fake_path.name}"
        dest_fake_path = fake_dir / dest_fake_name
        _copy_file(source_fake_path, dest_fake_path)
        smoke_fake_rel_path = f"{source_dataset}/fake/{dest_fake_name}"
        selection_records.append(
            {
                "kind": "fake",
                "source_dataset": source_dataset,
                "sample_id": sample.sample_id,
                "source_path": str(source_fake_path),
                "dest_path": str(dest_fake_path),
                "label": "fake",
            }
        )
        manifest_records.append(
            {
                "sample_id": smoke_fake_rel_path,
                "task_type": "localized_edit",
                "split": "smoke",
                "image_path": smoke_fake_rel_path,
                "label": 1,
                "mask_path": None,
                "generator_id": sample.generator_id,
                "source_id": source_dataset,
                "degradation": sample.degradation,
                "region_type": sample.region_type,
                "subtlety": sample.subtlety,
                "meta": {
                    "source_drop_root": str(source_root),
                    "source_manifest_sample_id": sample.sample_id,
                    "source_path": str(source_fake_path),
                    "selection_kind": "fake",
                    "smoke_kind": "temporary_coco_balanced",
                },
            }
        )

        real_name = real_names[index]
        dest_real_path = real_dir / f"real__{real_name}"
        attempt = download_with_fallback(
            relative_path=real_name,
            dest_path=dest_real_path,
            base_urls=(real_image_download_base_url,),
        )
        if attempt.status == "failed":
            raise BRGenCOSmokePreparationError(
                f"Could not download real image {real_name!r} from {real_image_download_base_url}: {attempt.reason}"
            )
        if not _is_valid_image(dest_real_path):
            raise BRGenCOSmokePreparationError(
                f"Downloaded real image is not readable: {dest_real_path}"
            )
        smoke_real_rel_path = f"{source_dataset}/real/real__{real_name}"
        selection_records.append(
            {
                "kind": "real",
                "source_dataset": source_dataset,
                "real_filename": real_name,
                "source_url": f"{real_image_download_base_url.rstrip('/')}/{real_name}",
                "dest_path": str(dest_real_path),
                "label": "real",
            }
        )
        manifest_records.append(
            {
                "sample_id": smoke_real_rel_path,
                "task_type": "localized_edit",
                "split": "smoke",
                "image_path": smoke_real_rel_path,
                "label": 0,
                "mask_path": None,
                "generator_id": None,
                "source_id": source_dataset,
                "degradation": None,
                "region_type": None,
                "subtlety": None,
                "meta": {
                    "source_drop_root": str(source_root),
                    "source_url": f"{real_image_download_base_url.rstrip('/')}/{real_name}",
                    "real_filename": real_name,
                    "selection_kind": "real",
                    "smoke_kind": "temporary_coco_balanced",
                },
            }
        )

    selection_path = output_root / "selection.jsonl"
    _write_jsonl(selection_path, selection_records)
    manifest_output_path = output_root / "manifest.jsonl"
    _write_jsonl(manifest_output_path, manifest_records)
    _write_readme(output_root, source_dataset, len(fake_samples))

    return BRGenCOSmokeArtifacts(
        output_root=output_root,
        manifest_path=manifest_output_path,
        selection_path=selection_path,
        copied_real_count=len(fake_samples),
        copied_fake_count=len(fake_samples),
        source_dataset=source_dataset,
    )


def _read_nonempty_lines(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8") as handle:
        return [line.strip() for line in handle if line.strip()]


def _copy_file(source_path: Path, dest_path: Path) -> None:
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, dest_path)


def _is_valid_image(path: Path) -> bool:
    try:
        with Image.open(path) as image:
            image.load()
    except Exception:
        return False
    return True


def _write_jsonl(path: Path, records: Iterable[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def _write_readme(output_root: Path, source_dataset: str, sample_count: int) -> None:
    readme_path = output_root / "README.md"
    readme_path.write_text(
        "\n".join(
            [
                "# Temporary BR-Gen Community Forensics smoke data",
                "",
                f"This directory is a temporary smoke fixture for {source_dataset}.",
                f"It contains {sample_count} fake BR-Gen samples and {sample_count} COCO real images.",
                "Delete this directory after validation.",
                "The temporary manifest lives at manifest.jsonl.",
                "",
                "Layout:",
                f"- {source_dataset}/real",
                f"- {source_dataset}/fake",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
