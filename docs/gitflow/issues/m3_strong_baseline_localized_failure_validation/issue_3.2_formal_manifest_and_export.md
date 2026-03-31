# Issue 3.2 — Prepare formal BR-Gen manifests and perturbation-aware export

GitHub issue:
- #19
- `https://github.com/re-tourist/AIGC-Detection/issues/19`

## Background

M3 needs a formal localized manifest path built directly from the official BR-Gen
root. The existing Community Forensics export path should be reused instead of
replaced.

Current repo truth:

- the formal manifest builder is implemented
- the Community Forensics export path is perturbation-aware
- this scope is already completed locally and should be backfilled to GitHub as a
  completed issue

## Suggested Branch

`codex/stage3-strong-baseline-localized-validation`

## Goal

Write formal clean and degraded localized manifests from the official BR-Gen
root, then export repo-compatible prediction JSONL through the existing
Community Forensics inference path.

## Tasks

- audit the official BR-Gen root before manifest generation
- generate `clean_manifest.jsonl`, `formal_manifest.jsonl`, and `layout_audit.json`
- keep the formal source root external and avoid copying the full dataset into
  the repo
- make the Community Forensics export path apply fixed perturbations when
  `meta.perturbation` is present
- preserve clean-manifest behavior when no perturbation is present

## Resource Boundary

- formal BR-Gen source root must be passed explicitly
- raw `edit_area_ratio` remains forbidden
- perturbation strengths are fixed by the M3 contract

## Non-Goals

- no new baseline
- no new model training
- no degraded image export cache

## Deliverable

- formal BR-Gen manifest builder
- perturbation-aware prediction export
- focused tests for manifest prep and export behavior

## Acceptance

- clean and degraded manifests are deterministic and repo-compatible
- ambiguous or broken official layouts fail loudly
- export output remains compatible with the existing prediction JSONL loader
