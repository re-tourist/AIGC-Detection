# Issue 4.3 - Run COCO-only baseline-vs-local-module comparison and slice audit

GitHub issue:
- #25
- `https://github.com/re-tourist/AIGC-Detection/issues/25`

## Background

M3 has already established a failure evidence map on the full-COCO restricted
pilot. M4 must use that map to judge whether the local module helps on the
actual weak slices, not just whether overall score changes.

## Suggested Branch

`codex/stage4-coco-comparison-audit`

## Goal

Run a controlled COCO-only restricted-pilot comparison between the baseline and
the baseline-plus-local-module variant, then audit the slice-level outcome.

## Tasks

- generate predictions for both comparison arms
- run the existing eval and localized sidecar for both arms
- compare:
  - overall metrics
  - `region_type`
  - `edit_area_ratio`
  - degradation slices
  - the known weak slices from M3
- separate clearly:
  - actual improvement
  - neutral change
  - regression
  - inconclusive low-support observations

## Resource Boundary

- use the existing restricted-pilot manifests and sidecar
- keep the comparison inside COCO-only engineering scope
- avoid any wording that turns this into a formal benchmark claim

## Non-Goals

- no formal M3 resurrection
- no new data source integration
- no paper benchmark packaging

## Deliverable

- comparison artifacts for both arms
- a slice-level audit describing where the local module helps or fails to help

## Acceptance

- both arms are evaluated under the same contract
- slice-level conclusions are support-aware
- the report emphasizes failure axes rather than only overall score
