# local_module_contract

## Contract Title

- Contract ID: `contract_m4_local_module_probe_coco_restricted_pilot`
- Related stage / milestone: `M4: Local Evidence Probe on COCO Restricted Pilot`
- Status:
  - [x] frozen
  - [ ] proposed
  - [ ] revised
  - [ ] retired
- Owner:
  - human research owner
  - codex M4 execution
- Last updated: `2026-04-02`

## 1. Purpose

This contract freezes the M4 probe path for the currently verified Community
Forensics ViT baseline.

The goal is narrow:
- test whether localized evidence can help the known weak slices from M3
- do not change the baseline backbone
- do not turn the probe into a new model or a training milestone

M4 is a failure-explanation and minimal-fix probe, not a benchmark claim.

---

## 2. M4 Scope Clarification

- The local evidence module is introduced as an inference-time probe path.
- No training recipe or optimization claim is included in this milestone.
- Hard top-k selection is acceptable because differentiability is out of scope.

This module is NOT a new model.
This module is a probe for localized failure.

---

## 3. What This Contract Covers

Current contract scope:
- COCO-only restricted pilot
- current verified CF-ViT baseline path
- patch-token-only local evidence scoring
- residual fusion between CLS/global and local evidence
- CLI-gated activation with YAML parameters only
- baseline export compatibility and regression protection

---

## 4. Frozen Objectives

The following goals are fixed for M4:

- Objective 1:
  - preserve the current Community Forensics baseline path unchanged when the
    probe is disabled
- Objective 2:
  - insert the local module only between token features and the unchanged head
- Objective 3:
  - measure whether the probe improves the known weak localized slices on the
    COCO restricted pilot

These objectives must not be reinterpreted during normal implementation work.

---

## 5. Frozen Inputs / Outputs

### Inputs
- Input A:
  - source:
    - `forward_features(x)` from the verified CF-ViT backbone
  - expected form:
    - `X ∈ R^{B×(1+N)×D}`
  - meaning:
    - token sequence with CLS token at index `0` and patch tokens at
      `1:`
- Input B:
  - source:
    - local evidence module parameters
  - expected form:
    - `model.local_module.type`
    - `model.local_module.k`
  - meaning:
    - probe configuration only, not activation
- Input C:
  - source:
    - CLI flag `--use-local-module`
  - expected form:
    - boolean switch
  - meaning:
    - single activation source for the probe path

### Outputs
- Output A:
  - location / API / artifact:
    - wrapper logit output
  - expected form:
    - `logit ∈ R^{B×1}`
  - meaning:
    - classification score from the unchanged head
- Output B:
  - location / API / artifact:
    - repo-compatible prediction JSONL
  - expected form:
    - same baseline schema, with optional local-module provenance in `meta`
  - meaning:
    - export path stays compatible with existing runner contracts

---

## 6. Frozen Interfaces

Frozen interfaces:
- Interface 1:
  - `LocalEvidenceModule.forward(patch_tokens)` consumes patch tokens only
  - patch tokens are `X[:, 1:, :]`
- Interface 2:
  - `f_global = X[:, 0, :]`
  - `f_local = LocalEvidenceModule(patch_tokens)`
  - `f_out = f_global + f_local`
  - no concat, no gating, no attention, no extra head
- Interface 3:
  - `--use-local-module` is the only activation switch
  - YAML must not contain `model.use_local_module`
- Interface 4:
  - YAML is parameter-only
  - allowed keys are `model.local_module.type` and `model.local_module.k`
- Interface 5:
  - baseline mode must be numerically equivalent to the original CF ViT
    classifier within tolerance
- Interface 6:
  - top-k behavior:
    - `k <= 0` -> error
    - `N == 0` -> error
    - `k > N` -> clamp to `N`
    - `N == 1` -> trivial selection

Allowed tolerance:
- internal refactor that preserves the frozen meaning above
- doc clarification without semantic change
- non-breaking validation additions

Not allowed:
- renaming or changing the frozen fusion rule
- silent semantic drift in token selection
- hidden activation control through YAML
- changing the head interface
- introducing training-only behavior

---

## 7. Allowed Change Window

The following changes are allowed within this stage:

- implementation detail improvements that do not change semantics
- focused bug fixes that restore intended behavior
- additional tests / validation
- documentation sync
- narrow refactors that preserve interfaces and outputs

Project-specific allowed changes:
- add the local module wrapper and exporter plumbing
- add config and docs for the probe path
- add slice-aware comparison notes for COCO restricted pilot analysis

---

## 8. Explicitly Forbidden Changes

The following changes must not be made during this stage without explicit
approval:

- redesigning the backbone
- adding concat, gating, attention, or a new head
- changing evaluation or metric semantics
- expanding the dataset scope beyond COCO-only restricted pilot
- introducing ImageNet / Places negatives
- turning the probe into a benchmark claim

---

## 9. Validation Contract

The following validation expectations are frozen for this stage:

- required local checks:
  - `torch.allclose` baseline equivalence test with `atol=1e-6`
  - top-k selection and clamp tests
  - empty-token and invalid-`k` error tests
  - YAML parameter-only config rejection test
  - exporter flag plumbing test
- required focused tests:
  - repository unit tests covering the new module and exporter path
- required manual sanity checks:
  - review the contract, plan, and results docs before running the COCO pilot
- optional broader checks:
  - the later COCO restricted-pilot comparison using the existing eval chain

---

## 10. Stop Conditions

If any of the following happen, stop and report:

- the baseline path no longer matches the original CF ViT behavior when the
  probe is off
- token layout is ambiguous or CLS / patch positions cannot be trusted
- the requested change needs concat, gating, attention, or a new head
- YAML is being used as an activation source
- the work would expand beyond the verified CF-ViT path

---

## 11. Change Control

If this contract must change, do not edit code first.

Use this process:

1. identify the exact frozen item that no longer holds
2. explain why it blocks correctness or execution
3. propose the smallest revision that would unblock M4
4. obtain human approval
5. update this contract explicitly before continuing

---

## 12. Linked Documents

Relevant docs:
- `docs/gitflow/milestones/m4_community_forensics_local_module_coco_engineering_line.md`
- `docs/gitflow/issues/m4_community_forensics_local_module_coco_engineering_line/issue_4.2_local_module_integration.md`
- `docs/gitflow/issues/m4_community_forensics_local_module_coco_engineering_line/issue_4.3_coco_only_comparison_and_slice_audit.md`
- `docs/plan/milestone4_local_module.md`
- `docs/exp/local_module_results.md`

## 13. Repository Workflow Note

- Full COCO restricted-pilot runs and multi-seed audits are expected to execute
  on Linux servers with the complete BR-Gen forged-image mirror.
- Local validation is limited to code paths, CLI behavior, config parsing, and
  unit tests.
- New experiment commands should be appended to `docs/run_order.md` with a
  timestamped heading and a short note; keep historical commands instead of
  overwriting them.
