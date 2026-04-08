from __future__ import annotations

import torch
from torch import Tensor, nn


class LocalEvidenceModuleError(ValueError):
    """Raised when the local evidence probe receives invalid token input."""


class LocalEvidenceModule(nn.Module):
    """Top-k local evidence probe over patch tokens."""

    def __init__(
        self,
        token_dim: int,
        *,
        k: int = 16,
        module_type: str = "topk",
    ) -> None:
        super().__init__()
        if isinstance(token_dim, bool) or not isinstance(token_dim, int) or token_dim <= 0:
            raise LocalEvidenceModuleError(
                f"token_dim must be a positive integer, got {token_dim!r}"
            )

        module_type = str(module_type).strip().lower()
        if module_type != "topk":
            raise LocalEvidenceModuleError(f"Unsupported local module type: {module_type!r}")

        if isinstance(k, bool) or not isinstance(k, int) or k <= 0:
            raise LocalEvidenceModuleError(f"k must be a positive integer, got {k!r}")

        self.token_dim = int(token_dim)
        self.k = int(k)
        self.module_type = module_type
        hidden_dim = max(self.token_dim, 1)
        self.score_mlp = nn.Sequential(
            nn.Linear(self.token_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, 1),
        )

    def forward(self, patch_tokens: Tensor) -> Tensor:
        if patch_tokens.ndim != 3:
            raise LocalEvidenceModuleError(
                f"patch_tokens must have shape [B, N, D], got {tuple(patch_tokens.shape)}"
            )
        if patch_tokens.size(1) == 0:
            raise LocalEvidenceModuleError("patch_tokens must contain at least one token")
        if patch_tokens.size(-1) != self.token_dim:
            raise LocalEvidenceModuleError(
                f"Expected token dimension {self.token_dim}, got {patch_tokens.size(-1)}"
            )

        scores = self.score_mlp(patch_tokens)
        if scores.ndim != 3 or scores.size(0) != patch_tokens.size(0) or scores.size(1) != patch_tokens.size(1) or scores.size(-1) != 1:
            raise LocalEvidenceModuleError(
                f"score_mlp must return shape [B, N, 1], got {tuple(scores.shape)}"
            )

        scores = scores.squeeze(-1)
        top_k = min(self.k, patch_tokens.size(1))
        selected_indices = torch.topk(scores, k=top_k, dim=1).indices
        expanded_indices = selected_indices.unsqueeze(-1).expand(-1, -1, patch_tokens.size(-1))
        selected_tokens = torch.gather(patch_tokens, dim=1, index=expanded_indices)
        return selected_tokens.mean(dim=1)
