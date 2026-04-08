# Issue 4.2 - Integrate a local module into the Community Forensics baseline path

GitHub issue:
- #24
- `https://github.com/re-tourist/AIGC-Detection/issues/24`

## Background

The baseline path already runs end to end on the COCO-only restricted pilot.
M4 now needs a local module added on top of that path without breaking the
existing export, prediction, and evaluation contracts.

## Suggested Branch

`codex/stage4-local-module-integration`

## Goal

Implement the smallest viable local module on top of the Community Forensics
baseline so that it can be compared fairly against the current baseline under
the same restricted-pilot contract.

## Tasks

- integrate the local module at the frozen insertion point
- keep the baseline path available as an unchanged comparison arm
- make the export path selectable between:
  - baseline
  - baseline plus local module
- preserve manifest, prediction JSONL, and runner compatibility
- add focused validation for the new path

## Resource Boundary

- allowed:
  - code changes in the Community Forensics integration path
  - minimal config or script changes needed for side-by-side comparison
- not allowed:
  - evaluation contract changes
  - new dataset scope
  - unrelated refactors

## Non-Goals

- no generator-diverse retraining
- no formal benchmark work
- no paper-facing result claims

## Deliverable

- a runnable baseline-plus-local-module export path
- focused validation proving the path is wired correctly

## Acceptance

- both comparison arms run under the same restricted-pilot contract
- the local module path does not break existing baseline execution
- the diff stays reviewable and scoped
