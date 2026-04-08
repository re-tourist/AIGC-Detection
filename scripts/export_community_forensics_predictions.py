from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
EXTERNAL_ROOT = REPO_ROOT / "external" / "Community-Forensics"

if str(EXTERNAL_ROOT) not in sys.path:
    sys.path.insert(0, str(EXTERNAL_ROOT))
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from aigc_detection.data.manifest import load_manifest
from aigc_detection.eval.perturbations import apply_manifest_perturbation, get_manifest_perturbation


@dataclass(frozen=True)
class ExportArtifacts:
    output_path: Path
    manifest_path: Path
    sample_count: int
    device: str


@contextmanager
def _seeded_torch_rng(seed: int | None):
    if seed is None:
        yield
        return

    cpu_state = torch.random.get_rng_state()
    cuda_state = torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None
    try:
        torch.manual_seed(seed)
        yield
    finally:
        torch.random.set_rng_state(cpu_state)
        if cuda_state is not None:
            torch.cuda.set_rng_state_all(cuda_state)


class ManifestImageDataset(Dataset):
    def __init__(self, samples, transform):
        self.samples = samples
        self.transform = transform

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int):
        sample = self.samples[index]
        image = Image.open(sample.image_path).convert("RGB")
        perturbation = get_manifest_perturbation(sample.meta)
        if perturbation is not None:
            image = apply_manifest_perturbation(image, perturbation)
        tensor = self.transform(image)
        return (
            tensor,
            sample.sample_id,
            str(sample.image_path),
            int(sample.label),
            sample.task_type,
            sample.generator_id or "",
            sample.source_id or "",
            sample.degradation or "",
            json.dumps(perturbation, sort_keys=True) if perturbation is not None else "",
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run Community Forensics inference on a frozen manifest and export prediction JSONL."
    )
    parser.add_argument("--manifest", required=True, help="Path to the frozen manifest JSONL.")
    parser.add_argument("--output", required=True, help="Path to write repo-compatible prediction JSONL.")
    parser.add_argument(
        "--hf-model-repo",
        default=str(EXTERNAL_ROOT / "weights" / "commfor-model-384"),
        help="Local or Hugging Face model repository used to load Community Forensics weights.",
    )
    parser.add_argument("--model-size", default="small", choices=("small", "tiny"))
    parser.add_argument("--input-size", type=int, default=384, choices=(224, 384))
    parser.add_argument("--patch-size", type=int, default=16, choices=(16, 32))
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument(
        "--use-local-module",
        action="store_true",
        help="Enable the inference-time local evidence probe.",
    )
    parser.add_argument(
        "--local-module-config",
        default=str(REPO_ROOT / "configs" / "model" / "local_module.yaml"),
        help="YAML file containing model.local_module parameters.",
    )
    parser.add_argument(
        "--device",
        default="auto",
        choices=("auto", "cpu", "cuda"),
        help="Inference device. Auto prefers CUDA when available.",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--progress-every",
        type=int,
        default=0,
        help="Emit progress every N batches while exporting. 0 disables progress logs.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    manifest_path = Path(args.manifest).resolve()
    output_path = Path(args.output).resolve()

    samples = load_manifest(manifest_path)
    if not samples:
        raise ValueError(f"Manifest contains no samples: {manifest_path}")

    device = _resolve_device(args.device)
    transform = _build_eval_transform(args.input_size)
    dataset = ManifestImageDataset(samples, transform)
    sample_meta_by_id = {sample.sample_id: sample.meta for sample in samples}
    dataloader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        pin_memory=(device == "cuda"),
    )

    local_module_config = _load_local_module_config_if_enabled(
        enabled=args.use_local_module,
        config_path=args.local_module_config,
    )
    with _seeded_torch_rng(args.seed if args.use_local_module else None):
        model = _load_model(
            hf_model_repo=args.hf_model_repo,
            model_size=args.model_size,
            input_size=args.input_size,
            patch_size=args.patch_size,
            device=device,
            use_local_module=args.use_local_module,
            local_module_config=local_module_config,
        )
    local_module_metadata = _describe_local_module_config(local_module_config)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    records_written = 0
    total_batches = len(dataloader)
    with torch.inference_mode():
        with output_path.open("w", encoding="utf-8") as handle:
            for batch_index, batch in enumerate(dataloader, start=1):
                (
                    inputs,
                    sample_ids,
                    image_paths,
                    labels,
                    task_types,
                    generator_ids,
                    source_ids,
                    degradations,
                    perturbations,
                ) = batch
                inputs = inputs.to(device)
                logits = model(inputs).squeeze(-1)
                scores = torch.sigmoid(logits).detach().cpu().tolist()

                for sample_id, image_path, label, task_type, generator_id, source_id, degradation, perturbation_json, score in zip(
                    sample_ids,
                    image_paths,
                    labels,
                    task_types,
                    generator_ids,
                    source_ids,
                    degradations,
                    perturbations,
                    scores,
                ):
                    record = {
                        "sample_id": sample_id,
                        "score": float(score),
                        "meta": {
                            "image_path": image_path,
                            "label": int(label),
                            "task_type": task_type,
                            "generator_id": generator_id or None,
                            "source_id": source_id or None,
                            "degradation": degradation or None,
                            "model_size": args.model_size,
                            "input_size": args.input_size,
                            "patch_size": args.patch_size,
                            "device": device,
                            "hf_model_repo": args.hf_model_repo,
                            "score_semantics": "higher_is_more_likely_fake_probability",
                        },
                    }
                    if args.use_local_module:
                        record["meta"]["local_module"] = local_module_metadata
                    sample_meta = sample_meta_by_id.get(sample_id)
                    if isinstance(sample_meta, dict) and sample_meta.get("evaluation_scope"):
                        record["meta"]["evaluation_scope"] = sample_meta["evaluation_scope"]
                    if perturbation_json:
                        record["meta"]["perturbation"] = json.loads(perturbation_json)
                    handle.write(json.dumps(record, ensure_ascii=False) + "\n")
                    records_written += 1

                if args.progress_every > 0 and (
                    batch_index % args.progress_every == 0 or batch_index == total_batches
                ):
                    print(
                        f"Export progress: batch {batch_index}/{total_batches}, "
                        f"records={records_written}/{len(dataset)}",
                        flush=True,
                    )

    print(f"Manifest: {manifest_path}")
    print(f"Output: {output_path}")
    print(f"Samples: {records_written}")
    print(f"Device: {device}")
    return 0


def _resolve_device(device_mode: str) -> str:
    if device_mode != "auto":
        return device_mode
    return "cuda" if torch.cuda.is_available() else "cpu"


def _build_eval_transform(input_size: int):
    resize_size = 440 if input_size == 384 else 256
    norm_mean = [0.485, 0.456, 0.406]
    norm_std = [0.229, 0.224, 0.225]
    return transforms.Compose(
        [
            transforms.Resize(resize_size),
            transforms.CenterCrop(input_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=norm_mean, std=norm_std),
        ]
    )


def _load_model(
    *,
    hf_model_repo: str,
    model_size: str,
    input_size: int,
    patch_size: int,
    device: str,
    use_local_module: bool = False,
    local_module_config: Any | None = None,
):
    try:
        from models import ViTClassifier
    except ModuleNotFoundError as error:
        missing_name = error.name or "<unknown>"
        raise ModuleNotFoundError(
            "Community Forensics baseline dependencies are missing. "
            f"Could not import {missing_name!r}. "
            "Install the repo environment first, for example: "
            "`pip install -r requirements.txt`."
        ) from error

    try:
        model = ViTClassifier.from_pretrained(
            hf_model_repo,
            model_size=model_size,
            input_size=input_size,
            patch_size=patch_size,
            freeze_backbone=False,
            device=device,
            dtype=torch.float32,
            use_local_module=use_local_module,
            local_module_config=local_module_config,
        ).to(device)
        model.eval()
        return model
    except Exception:
        if device == "cpu":
            raise
        fallback_device = "cpu"
        model = ViTClassifier.from_pretrained(
            hf_model_repo,
            model_size=model_size,
            input_size=input_size,
            patch_size=patch_size,
            freeze_backbone=False,
            device=fallback_device,
            dtype=torch.float32,
            use_local_module=use_local_module,
            local_module_config=local_module_config,
        ).to(fallback_device)
        model.eval()
        return model


def _load_local_module_config_if_enabled(*, enabled: bool, config_path: str):
    if not enabled:
        return None
    from models import load_local_module_config

    return load_local_module_config(config_path)


def _describe_local_module_config(local_module_config: Any) -> dict[str, Any]:
    if local_module_config is None:
        return {}
    module_type = getattr(local_module_config, "module_type", None)
    k = getattr(local_module_config, "k", None)
    if module_type is None and isinstance(local_module_config, dict):
        module_type = local_module_config.get("type", local_module_config.get("module_type"))
        k = local_module_config.get("k")
    return {
        "type": module_type,
        "k": k,
    }


if __name__ == "__main__":
    raise SystemExit(main())
