# Issue 6.2 - Metric alignment implementation

## Background

The repo already has stable legacy metrics, but paper-style reporting needs to
additive-ly expose `F1` and `Recall@50` style reads without silently changing
the old contract.

## Suggested Branch

`codex/stage6-metric-alignment`

## Goal

Implement a unified binary metric kernel that preserves legacy metrics while
adding paper-style thresholded metrics and explicit audit fields.

## Deliverables

- shared binary metric helpers
- unified slice summary helper
- additive paper-style metrics:
  - `f1_at_paper_style_threshold`
  - `paper_manipulated_recall_at_0_5`
  - `paper_real_recall_at_0_5`
- audit fields:
  - `legacy_fake_recall_value`
  - `paper_manipulated_recall_at_0_5`
  - `legacy_threshold`
  - `paper_style_threshold`
  - `legacy_equals_paper_manipulated_recall`
- robustness handling for empty and single-class slices

## Acceptance Criteria

- legacy metrics are unchanged in meaning
- new metrics are emitted by the same evaluator path
- threshold behavior is explicit
- undefined metrics produce `null / N/A`, not fake zeros
- tests cover empty slice, single-class slice, and AUROC undefined cases
