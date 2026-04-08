# contract_freeze

## Contract Title

- Contract ID: `contract_stage3_strong_baseline_localized_failure_validation_20260329`
- Related stage / milestone: `M3: Strong Baseline Localized Failure Validation`
- Status:
  - [ ] proposed
  - [x] frozen
  - [ ] revised
  - [ ] retired
- Owner:
  - human research owner
  - codex M3 execution
- Last updated: `2026-03-29`
- Restricted pilot status:
  - approved for implementation
- Formal M3 status:
  - blocked pending ImageNet / Places real negatives

## 1. Purpose

This contract freeze locks the active M3 boundary.

Its purpose is to prevent:
- silent fallback from the official Linux BR-Gen root to ad hoc local paths
- hidden changes to the frozen M1 data and metric semantics
- expansion from formal validation into reproduction, retraining, or future-stage work
- heuristic invention of localized slice metadata that the dataset does not explicitly provide

M3 exists to validate a strong baseline under the current repository contract, not to redesign that contract.

---

## 2. What This Contract Covers

Current contract scope:
- official BR-Gen raw-layout audit rules
- formal clean and degraded manifest preparation
- perturbation-aware prediction export through the existing Community Forensics path
- localized-failure sidecar reporting layered on top of the minimal runner
- COCO-only restricted pilot path that preserves the frozen metric contract

---

## 3. Frozen Objectives

The following goals are fixed for M3:

- Objective 1:
  - prepare formal BR-Gen localized manifests from the official external source root without copying the full dataset into the repository
- Objective 2:
  - export repo-compatible prediction JSONL for clean and degraded localized samples through the existing baseline path
- Objective 3:
  - produce localized-failure evidence with the existing metrics trio plus M3 sidecar slice reporting
- Objective 4:
  - enable a COCO-only restricted pilot for pipeline validation without unblocking formal M3

These objectives must not be reinterpreted during normal implementation work.

---

## 4. Frozen Inputs / Outputs

### Inputs
- Input A:
  - source:
    - external Linux BR-Gen root
  - expected form:
    - explicit path provided at runtime
  - meaning:
    - source of formal raw real, fake, and mask files
- Input B:
  - source:
    - existing Community Forensics baseline weights and export script
  - expected form:
    - repo-compatible prediction export path
  - meaning:
    - strong baseline inference entry point for M3
- Input C:
  - source:
    - frozen M1 loader, metrics, and minimal runner
  - expected form:
    - existing manifest and prediction JSONL contract
  - meaning:
    - base evaluation substrate that M3 must reuse

### Outputs
- Output A:
  - location / API / artifact:
    - `clean_manifest.jsonl`, `formal_manifest.jsonl`, `layout_audit.json`
  - expected form:
    - manifest files under `data/mirrored/br_gen/subsets/.../manifest/`
  - meaning:
    - formal localized sample definitions derived from the official raw layout
- Output B:
  - location / API / artifact:
    - repo-compatible prediction JSONL
  - expected form:
    - one score record per manifest sample
  - meaning:
    - baseline scores consumable by the existing runner
- Output C:
  - location / API / artifact:
    - minimal runner artifacts plus M3 sidecar report
  - expected form:
    - `summary.json`, `metrics.csv`, `smoke_report.md`, `config_snapshot.json`, `localized_failure_summary.json`, `localized_failure_metrics.csv`, `localized_failure_report.md`
  - meaning:
    - traceable evaluation outputs for localized-failure validation

---

## 5. Frozen Interfaces

Frozen interfaces:
- Interface 1:
  - the official BR-Gen root must be passed explicitly to `scripts/prepare_br_gen_m3_formal.py`
  - no implicit fallback to `data/BR-Gen` is allowed for formal M3 work
- Interface 2:
  - raw fake layout must be interpreted as `Forged/<generator>/<region>/<source>/<file>`
  - mask root may be `Mask` or `Masked`
  - real root may be `Real`, `RealImage`, or `real`
- Interface 3:
  - `edit_area_ratio` remains a derived quantity only
  - it must not be accepted as a raw manifest field
- Interface 4:
  - `subtlety` remains blocked unless explicit metadata exists
  - M3 must not infer it heuristically
- Interface 5:
  - degraded localized variants must use only the fixed perturbations:
    - JPEG quality `85`
    - resize scale `0.90`
    - blur sigma `1.0`
    - center crop with `90%` retained area
- Interface 6:
  - the minimal runner metric contract remains:
    - `AUROC`
    - `Accuracy`
    - `fake_recall`

Allowed tolerance:
- internal refactor that preserves the frozen meaning above
- stricter validation that prevents ambiguous layout interpretation
- additional sidecar reporting that does not change M1 runner outputs

Not allowed:
- changing M1 metric meaning
- making `edit_area_ratio` a raw manifest field
- inventing `subtlety`, new region semantics, or other heuristic slices
- changing perturbation strengths without an explicit contract revision

---

## 6. Allowed Change Window

The following changes are allowed within M3:

- layout-audit and manifest-builder implementation
- perturbation-aware export changes that remain backward-compatible for clean manifests
- M3-only reporting layers on top of the current runner
- focused tests, docs, and runbooks

Project-specific allowed changes:
- add BR-Gen dataset notes and formal subset layout docs
- add Linux pilot and full-run command documentation
- add COCO-only real subset materialization and restricted-pilot source filtering

---

## 7. Explicitly Forbidden Changes

The following changes are forbidden without explicit approval:

- modifying the frozen M1 contract
- Community Forensics paper reproduction
- generator-diverse retraining
- copying the full official BR-Gen dataset into the repository
- fabricating benchmark evidence from smoke artifacts or synthetic substitutes
- treating COCO-only restricted pilot outputs as formal benchmark evidence

---

## 8. Validation Contract

The following validation expectations are frozen for this stage:

- required local checks:
  - M3-focused unit tests for formal manifest prep, perturbations, exporter wiring, and sidecar reporting
- required focused tests:
  - current repository `unittest` suite for `tests/test_*.py`
- required manual sanity checks:
  - doc cross-read for milestone, issue split, run order, and runbook
- optional broader checks:
  - Linux pilot run on a bounded formal subset before the full run

M3 cannot be called complete until Linux pilot and full runs are either executed or explicitly reported as pending.

---

## 9. Stop Conditions

If any of the following happen, stop and report:

- the official BR-Gen root is missing, ambiguous, or layout-incompatible with the frozen path rules
- fake, mask, and real files cannot be paired without guessing
- a requested change would modify M1 metric meaning or raw schema meaning
- formal validation would require inventing unavailable metadata such as `subtlety`
- Linux execution is required but unavailable

Project-specific stop conditions:
- if both `Mask` and `Masked` exist as distinct directories, stop and treat the root as ambiguous
- if real-image pairing becomes ambiguous for any fake sample, stop instead of using heuristic matching
- if ImageNet / Places real negatives remain unavailable, keep formal M3 blocked and limit execution to restricted pilot only

---

## 10. Change Control

If this contract must change, do not edit code first.

Use this process:

1. identify the exact frozen item that no longer holds
2. explain why it blocks correctness or execution
3. propose the smallest revision that would unblock M3
4. obtain human approval
5. update this contract explicitly before continuing

---

## 11. Linked Documents

Relevant docs:
- `docs/contracts/contract_freeze_stage1_data_metric_bootstrap.md`
- `docs/gitflow/milestones/m3_strong_baseline_localized_failure_validation.md`
- `docs/gitflow/issues/m3_strong_baseline_localized_failure_validation/README.md`
- `docs/handoff/m3_linux_runbook_strong_baseline_localized_failure_validation.md`
- `docs/handoff/milestone_closeout_stage2_community_forensics_integration.md`

Project-specific links:
- `docs/run_order.md`
- `data/registry/datasets/br_gen.dataset.md`

---

## 12. Freeze Review Notes

### Review entry
- date: `2026-03-29`
- requested by: `M3 execution`
- issue: `freeze the official BR-Gen root, perturbation contract, and M3-only reporting boundary`
- proposed change: `formalize manifest prep, export, and sidecar reporting without changing M1`
- decision: `accepted and frozen`
- rationale: `M3 needs a stable validation boundary before Linux pilot and full runs`
