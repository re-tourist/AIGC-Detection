# Issue 3.5 — Expand restricted pilot evidence and failure mapping

GitHub issue:
- pending creation

## Background

The initial COCO-only restricted pilot ran end to end, but the first evidence
pass was too narrow:

- fake coverage was effectively close to `COCO-only`, `BrushNet-only`,
  `background-only`
- edit-area support was heavily concentrated in the `large` bin
- subtlety remained blocked
- overall metrics were high, but slice evidence was weak

Current repo truth:

- the active fake cap has been removed
- the expanded full-COCO restricted pilot has been executed
- wider coverage, support accounting, and failure-evidence artifacts now exist
- this scope should be backfilled to GitHub as a completed issue

## Suggested Branch

`codex/stage3-restricted-pilot-evidence-expansion`

## Goal

Expand the COCO-only restricted pilot so that it provides:

- wider slice coverage
- explicit support accounting
- a structured failure evidence map
- a clearer definition of pilot success

## Tasks

- audit and remove the active fake-sample cap in the restricted pilot path
- preserve the `restricted_pilot` and `COCO-only` boundaries
- extend the localized sidecar to report:
  - generator slices
  - region slices
  - source slices
  - edit-area slices
  - exploratory pairwise slices where support exists
- add low-support labeling and diagnostic labels
- generate new analysis artifacts:
  - `localized_coverage_summary.json`
  - `coverage_audit.md`
  - `failure_evidence_map.md`
- write an explicit restricted-pilot success-criteria document

## Resource Boundary

- allowed:
  - COCO-only restricted pilot expansion
  - stronger analysis artifacts
  - Linux reruns for the expanded restricted pilot
- not allowed:
  - ImageNet / Places negatives
  - formal M3 redefinition
  - method innovation
  - benchmark overclaim

## Non-Goals

- formal M3 closeout
- paper-ready benchmark claim
- new model training
- new localized architecture modules

## Deliverable

An expanded restricted pilot that is able to answer:

- which localized slices are covered
- which slices remain easy
- which slices show credible failure evidence
- which slices remain low-support or blocked

## Acceptance

- the active fake cap is auditable and removable
- expanded restricted pilot preserves `COCO-only` and `restricted_pilot`
- localized sidecar exposes wider slice coverage
- low-support slices are explicitly labeled
- a structured failure evidence map is generated
- pilot success criteria are written and linked
