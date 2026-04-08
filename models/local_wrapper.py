from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import torch
from torch import Tensor, nn
import yaml

from .local_module import LocalEvidenceModule


class LocalModuleConfigError(ValueError):
    """Raised when the local module config file is malformed."""


@dataclass(frozen=True)
class LocalModuleConfig:
    module_type: str = "topk"
    k: int = 16


class ViTClassifier(nn.Module):
    """Community Forensics ViT wrapper with an optional local evidence probe."""

    def __init__(
        self,
        *,
        base_model: nn.Module,
        use_local_module: bool = False,
        local_module_config: LocalModuleConfig | Mapping[str, Any] | None = None,
        model_size: str | None = None,
        input_size: int | None = None,
        patch_size: int | None = None,
        freeze_backbone: bool | None = None,
        device: str | torch.device | None = None,
        dtype: torch.dtype | None = None,
    ) -> None:
        super().__init__()
        self.base_model = base_model
        self.use_local_module = bool(use_local_module)
        self.model_size = model_size
        self.input_size = input_size
        self.patch_size = patch_size
        self.freeze_backbone = freeze_backbone
        self.device = device
        self.dtype = dtype
        self.local_module_config = (
            _normalize_local_module_config(local_module_config) if self.use_local_module else LocalModuleConfig()
        )

        self.local_module: LocalEvidenceModule | None = None
        if self.use_local_module:
            self.local_module = LocalEvidenceModule(
                token_dim=self._embed_dim,
                k=self.local_module_config.k,
                module_type=self.local_module_config.module_type,
            )

    @property
    def vit(self) -> nn.Module:
        vit = getattr(self.base_model, "vit", None)
        if vit is None:
            raise LocalModuleConfigError("Base model does not expose a ViT backbone")
        return vit

    @property
    def _embed_dim(self) -> int:
        head = getattr(self.vit, "head", None)
        if head is None:
            raise LocalModuleConfigError("Base model ViT does not expose a classification head")
        in_features = getattr(head, "in_features", None)
        if not isinstance(in_features, int):
            raise LocalModuleConfigError("Base model head does not expose an integer in_features")
        return in_features

    @classmethod
    def from_pretrained(
        cls,
        pretrained_model_name_or_path: str | Path,
        *,
        model_size: str = "small",
        input_size: int = 384,
        patch_size: int = 16,
        freeze_backbone: bool = False,
        device: str | torch.device = "cpu",
        dtype: torch.dtype = torch.float32,
        use_local_module: bool = False,
        local_module_config: LocalModuleConfig | Mapping[str, Any] | None = None,
    ) -> "ViTClassifier":
        baseline_cls = _load_external_vit_classifier_class()
        base_model = baseline_cls.from_pretrained(
            pretrained_model_name_or_path,
            model_size=model_size,
            input_size=input_size,
            patch_size=patch_size,
            freeze_backbone=freeze_backbone,
            device=device,
            dtype=dtype,
        )

        normalized_local_config = (
            _normalize_local_module_config(local_module_config) if use_local_module else None
        )
        wrapper = cls(
            base_model=base_model,
            use_local_module=use_local_module,
            local_module_config=normalized_local_config,
            model_size=model_size,
            input_size=input_size,
            patch_size=patch_size,
            freeze_backbone=freeze_backbone,
            device=device,
            dtype=dtype,
        )
        return wrapper.to(device)

    def forward(self, x: Tensor) -> Tensor:
        if not self.use_local_module or self.local_module is None:
            return self.base_model(x)

        tokens = self.vit.forward_features(x)
        if tokens.ndim != 3 or tokens.size(1) < 2:
            raise LocalModuleConfigError(
                f"Expected backbone token output with shape [B, 1+N, D], got {tuple(tokens.shape)}"
            )

        f_global = tokens[:, 0, :]
        patch_tokens = tokens[:, 1:, :]
        f_local = self.local_module(patch_tokens)
        f_out = f_global + f_local
        return self.vit.head(f_out)


def load_local_module_config(config_path: str | Path) -> LocalModuleConfig:
    path = Path(config_path).expanduser().resolve()
    if not path.exists():
        raise LocalModuleConfigError(f"Local module config does not exist: {path}")
    if path.suffix.lower() not in {".yaml", ".yml"}:
        raise LocalModuleConfigError(f"Local module config must be YAML, got: {path.name}")

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise LocalModuleConfigError("Local module config must be a mapping at the document root")

    unknown_top_level = sorted(set(raw) - {"model"})
    if unknown_top_level:
        raise LocalModuleConfigError(
            f"Unknown top-level keys in local module config: {', '.join(unknown_top_level)}"
        )

    model_cfg = raw.get("model")
    if not isinstance(model_cfg, dict):
        raise LocalModuleConfigError("Local module config must contain a 'model' mapping")
    if "use_local_module" in model_cfg:
        raise LocalModuleConfigError(
            "Activation must be controlled by the CLI flag only; remove model.use_local_module from YAML"
        )

    unknown_model_keys = sorted(set(model_cfg) - {"local_module"})
    if unknown_model_keys:
        raise LocalModuleConfigError(
            f"Unknown keys in model mapping: {', '.join(unknown_model_keys)}"
        )

    local_cfg = model_cfg.get("local_module")
    if not isinstance(local_cfg, dict):
        raise LocalModuleConfigError("Local module config must contain model.local_module")

    unknown_local_keys = sorted(set(local_cfg) - {"type", "k"})
    if unknown_local_keys:
        raise LocalModuleConfigError(
            f"Unknown keys in model.local_module: {', '.join(unknown_local_keys)}"
        )

    module_type = local_cfg.get("type")
    if not isinstance(module_type, str) or not module_type.strip():
        raise LocalModuleConfigError("model.local_module.type must be a non-empty string")
    module_type = module_type.strip().lower()
    if module_type != "topk":
        raise LocalModuleConfigError(f"Unsupported local module type: {module_type!r}")

    k = local_cfg.get("k")
    if isinstance(k, bool) or not isinstance(k, int):
        raise LocalModuleConfigError("model.local_module.k must be an integer")
    if k <= 0:
        raise LocalModuleConfigError("model.local_module.k must be positive")

    return LocalModuleConfig(module_type=module_type, k=k)


def _normalize_local_module_config(
    local_module_config: LocalModuleConfig | Mapping[str, Any] | None,
) -> LocalModuleConfig:
    if local_module_config is None:
        return LocalModuleConfig()
    if isinstance(local_module_config, LocalModuleConfig):
        return local_module_config
    if isinstance(local_module_config, Mapping):
        unknown_keys = sorted(set(local_module_config) - {"type", "module_type", "k"})
        if unknown_keys:
            raise LocalModuleConfigError(
                f"Unknown keys in local module config: {', '.join(unknown_keys)}"
            )
        module_type = local_module_config.get(
            "type", local_module_config.get("module_type", "topk")
        )
        k = local_module_config.get("k", 16)
        if not isinstance(module_type, str) or not module_type.strip():
            raise LocalModuleConfigError("local module type must be a non-empty string")
        module_type = module_type.strip().lower()
        if module_type != "topk":
            raise LocalModuleConfigError(f"Unsupported local module type: {module_type!r}")
        if isinstance(k, bool) or not isinstance(k, int):
            raise LocalModuleConfigError("local module k must be an integer")
        if k <= 0:
            raise LocalModuleConfigError("local module k must be positive")
        return LocalModuleConfig(module_type=module_type, k=k)
    raise LocalModuleConfigError(
        f"Unsupported local module config type: {type(local_module_config).__name__}"
    )


@lru_cache(maxsize=1)
def _load_external_vit_classifier_class() -> type[nn.Module]:
    repo_root = Path(__file__).resolve().parents[1]
    external_models_path = repo_root / "external" / "Community-Forensics" / "models.py"
    if not external_models_path.exists():
        raise ModuleNotFoundError(
            f"Expected Community Forensics models at {external_models_path}"
        )

    module_name = "_community_forensics_external_models"
    spec = importlib.util.spec_from_file_location(module_name, external_models_path)
    if spec is None or spec.loader is None:
        raise ModuleNotFoundError(
            f"Could not load Community Forensics models from {external_models_path}"
        )

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    try:
        return module.ViTClassifier
    except AttributeError as error:
        raise ModuleNotFoundError(
            f"Community Forensics models file does not export ViTClassifier: {external_models_path}"
        ) from error
