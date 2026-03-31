# M4: Community Forensics Local Module on COCO Engineering Line

GitHub milestone:
- `https://github.com/re-tourist/AIGC-Detection/milestone/5`

## Status

- Planned milestone
- Entry condition is satisfied:
  - expanded full-COCO restricted pilot from M3 has completed
  - failure evidence map exists
  - Community Forensics baseline is already wired into the repo contracts
- Active engineering boundary:
  - `evaluation_scope = restricted_pilot`
  - `dataset scope = COCO-only`
- Explicitly not active:
  - formal M3 continuation
  - ImageNet / Places negatives
  - paper-ready benchmark claims

## Goal

Add a local module on top of the current Community Forensics baseline and test
whether it improves the already identified weak localized slices on the
COCO-only engineering line.

Current execution note:

- M4 is not a formal benchmark milestone
- M4 is a method-engineering milestone guided by M3 failure evidence
- the first comparison target is baseline vs baseline-plus-local-module under
  the existing restricted-pilot runner and sidecar

## In Scope

- freeze the M4 scope and evaluation boundary before coding
- decide the narrowest viable integration point for a local module in the
  Community Forensics path
- implement the local module without breaking the existing baseline export/eval
  contract
- run baseline vs local-module comparisons on the full-COCO restricted pilot
- analyze improvements or regressions on:
  - `region_type`
  - `edit_area_ratio`
  - degradation slices
  - the known weak axes from M3
- write a reviewable M4 handoff and closeout when the COCO engineering goal is
  sufficiently answered

## Out of Scope

- any attempt to revive formal M3 benchmark claims
- ImageNet / Places negatives
- contract changes to M1/M2 metric semantics
- retraining against broader generator-diverse data
- benchmark packaging for paper submission

## Entry Criteria

- M3 closeout is written and explicitly says the project is moving to M4 on the
  COCO-only engineering line
- the restricted-pilot artifacts are available:
  - `summary.json`
  - `localized_failure_summary.json`
  - `failure_evidence_map.md`
- the weak slices are explicit enough to drive method design:
  - `stuff`
  - `small / medium` edit area

## Exit Criteria

- a local module is integrated into the Community Forensics path
- the repo can run baseline and local-module variants under the same
  restricted-pilot contract
- comparison artifacts clearly show:
  - where the new module helps
  - where it does not help
  - what remains inconclusive
- the final write-up avoids any formal-benchmark overclaim

## Issue Set

- #23 Issue 4.1 - Freeze M4 scope and local-module interface on the COCO engineering line
- #24 Issue 4.2 - Integrate a local module into the Community Forensics baseline path
- #25 Issue 4.3 - Run COCO-only baseline-vs-local-module comparison and slice audit
- #26 Issue 4.4 - Write M4 review, handoff, and closeout for the engineering line
