# contract_freeze

## Contract Title

- Contract ID: `contract_stage1_data_metric_bootstrap_20260328`
- Related stage / milestone: `M1: Data and Metric Pipeline Bootstrap`
- Status:
  - [ ] proposed
  - [x] frozen
  - [ ] revised
  - [ ] retired
- Owner:
  - human research owner
  - codex M1 execution
- Last updated: `2026-03-28`

## 1. Purpose

This contract freeze locks the active M1 boundary.

Its purpose is to prevent:
- loader implementation drifting into baseline integration
- metric logic inventing metadata semantics
- runner implementation expanding into a full execution harness
- hidden redefinition of required / optional / derived fields

M1 only builds the minimum data and metric substrate needed for later validation.

---

## 2. What This Contract Covers

Current contract scope:
- manifest schema for local mirror data
- normalized sample object contract
- metric priority and grouped-reporting boundary
- minimal artifact output contract
- explicit stop rules

---

## 3. Frozen Objectives

The following goals are fixed for M1:

- Objective 1:
  - localized samples can be loaded into normalized sample objects
- Objective 2:
  - overall metrics can run on a small mirrored sample set
- Objective 3:
  - minimal outputs can be written to disk and traced back to manifest/prediction/config inputs

These objectives must not be reinterpreted during normal implementation work.

---

## 4. Frozen Inputs / Outputs

### Inputs
- Input A:
  - source:
    - local mirror manifest
  - expected form:
    - manifest-driven sample records with explicit raw fields only
  - meaning:
    - primary input to loader validation
- Input B:
  - source:
    - local mirrored sample files
  - expected form:
    - local subset copied from Linux server with representative samples
  - meaning:
    - smoke-only substrate for loader and runner validation
- Input C:
  - source:
    - prediction input file
  - expected form:
    - per-sample prediction scores keyed by `sample_id`
  - meaning:
    - metric input for minimal evaluation runner

### Outputs
- Output A:
  - location / API / artifact:
    - normalized sample objects in memory
  - expected form:
    - validated objects produced by loader
  - meaning:
    - canonical data representation for later M2/M3 work
- Output B:
  - location / API / artifact:
    - metrics summary artifacts
  - expected form:
    - `json`, `csv`, `md`
  - meaning:
    - minimal reproducible M1 metric outputs
- Output C:
  - location / API / artifact:
    - config / command snapshot
  - expected form:
    - machine-readable provenance
  - meaning:
    - tie outputs back to exact run settings

---

## 5. Frozen Interfaces

### Required raw fields

- `sample_id`
- `task_type`
- `split`
- `image_path`
- `label`

### Optional raw fields

- `mask_path`
- `generator_id`
- `source_id`
- `degradation`
- `region_type`
- `subtlety`
- `meta`

### Derived fields

- `edit_area_ratio`
  - not accepted as a raw manifest field
  - only allowed if a derivation rule is explicitly frozen
  - only allowed when computed from explicit `mask_path` or equivalent explicit region metadata

### Task type rule

- supported values:
  - `localized_edit`
  - `full_image_fake`
- M1 implementation priority:
  - `localized_edit` is the primary path
  - `full_image_fake` is compatibility-only

Allowed tolerance:
- internal refactor that preserves field meaning
- additional validation that preserves this contract
- extra metadata carried inside `meta` without changing frozen field semantics

Not allowed:
- adding new required raw fields without approval
- treating derived fields as raw manifest fields
- inventing implicit semantics for optional metadata

---

## 6. Metric Priority

### P0 required in M1

- `AUROC`
- `Accuracy`
- `fake_recall`

### P1 implement when supporting metadata exists

- grouped by `task_type`
- grouped by `degradation`

### P2 only when contract is explicit and metadata is explicit

- grouped by `region_type`
- grouped by `subtlety`
- grouped by `edit_area_ratio` bins

For M1:
- P2 dimensions may be reported as blocked / unsupported
- M1 must not fabricate grouped reporting for missing metadata

---

## 7. Allowed Change Window

The following changes are allowed within M1:

- loader implementation that respects the frozen schema
- metric implementation limited to P0 and supported P1 paths
- minimal runner and artifact writing
- narrow tests and fixtures
- doc sync for active M1 files

Project-specific allowed changes:
- add local smoke fixtures
- add machine-readable artifact formats

---

## 8. Explicitly Forbidden Changes

The following changes are forbidden without explicit approval:

- Community Forensics integration
- baseline training / inference implementation
- formal localized failure validation
- heuristic derivation of `subtlety` or `region_type`
- `edit_area_ratio` computation without a frozen derivation rule
- expansion into a full execution harness

---

## 9. Artifact Contract

M1 only requires the following minimal artifacts:

- summary JSON
- flat metrics CSV
- short smoke report Markdown
- command/config snapshot

M1 does not require:

- full benchmark tables
- server orchestration bundles
- training outputs

---

## 10. Stop Rules

- If localized samples cannot be loaded into normalized sample objects, stop before metric implementation.
- If normalized sample objects exist but no explicit slice metadata exists, complete overall metrics only and mark slice reporting as blocked.
- If mask files exist but the area-ratio derivation rule is not frozen, do not compute area bins.
- If the local mirror pack is absent, stop at loader validation and report the blocker.
- If implementing grouped metrics would require inventing metadata semantics, stop and report.

---

## 11. Linked Documents

- `docs/ai/PROJECT_CONTEXT.md`
- `docs/plan/plan_stage1_data_metric_bootstrap.md`
- `docs/plan/issue_stage1_data_metric_bootstrap.md`
- `docs/gitflow/MILESTONE_ROADMAP.md`
- `docs/review/code_review.md`

---

## 12. Freeze Review Notes

### Review entry
- date: `2026-03-28`
- requested by: `M1 execution`
- issue: `active M1 contract freeze before loader/metric implementation`
- proposed change: `freeze schema categories, metric priority, artifact contract, and stop rules`
- decision: `accepted and frozen`
- rationale: `M1 must stop leaving implementation choices implicit before code work begins`
