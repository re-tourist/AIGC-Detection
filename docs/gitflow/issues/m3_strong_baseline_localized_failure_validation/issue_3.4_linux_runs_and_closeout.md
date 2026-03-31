# Issue 3.4 — Execute formal Linux run and write milestone closeout

GitHub issue:
- #21
- `https://github.com/re-tourist/AIGC-Detection/issues/21`

## Background

M3 formal evidence depends on the official BR-Gen root and baseline weights on
Linux. Local implementation and the completed restricted pilot are not
sufficient to close the milestone.

Current repo truth:

- the expanded full-COCO restricted pilot has already been executed
- formal M3 remains blocked because ImageNet / Places real negatives are still
  unavailable
- this issue should remain open on GitHub as the blocked formal closeout issue

## Suggested Branch

`codex/stage3-formal-linux-closeout`

## Goal

Run the full formal localized-failure evaluation on Linux when prerequisites are
available, then write the milestone closeout.

## Tasks

- confirm formal prerequisites for ImageNet / Places real negatives are
  available
- run the full clean and degraded formal manifest flow on Linux
- export formal predictions and produce base eval plus M3 sidecar artifacts
- archive formal artifacts and write milestone closeout after the full run
- separate clearly:
  - already run
  - implemented but not yet run
  - Linux-only steps

## Resource Boundary

- use the frozen official BR-Gen root and M3 perturbation settings
- do not treat the restricted pilot as formal benchmark evidence
- do not write closeout text that claims results not yet run

## Non-Goals

- no additional method work
- no dataset relayout
- no rerouting through an upstream paper-reproduction harness

## Deliverable

- Linux full-run artifacts
- M3 closeout doc after formal execution

## Acceptance

- formal prerequisites are explicitly satisfied before execution
- full run produces formal manifest, predictions, base eval artifacts, and M3
  sidecar artifacts
- closeout explicitly states what was actually run and what remains out of scope
