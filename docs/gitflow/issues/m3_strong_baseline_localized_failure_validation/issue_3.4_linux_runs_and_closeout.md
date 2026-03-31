# Issue 3.4 - Formal Linux run and formal closeout path (deferred)

GitHub issue:
- #21
- `https://github.com/re-tourist/AIGC-Detection/issues/21`

## Background

M3 formal evidence depends on the official BR-Gen root and baseline weights on
Linux. Local implementation and the completed restricted pilot are not
sufficient to establish a formal benchmark claim.

Current repo truth:

- the expanded full-COCO restricted pilot has already been executed
- formal M3 remains unavailable because ImageNet / Places real negatives are
  still unavailable
- the project is now moving to M4 on the COCO-only engineering line
- this issue should be closed as deferred rather than left open as the active
  next step

## Suggested Branch

`codex/stage3-formal-linux-closeout`

## Goal

Record the deferred formal path cleanly so that M3 can close with documented
limitations and M4 can start from the restricted-pilot evidence base.

## Tasks

- record that the expanded `COCO-only restricted_pilot` is the last executed
  M3 evidence line
- document why the formal BR-Gen line is not being pursued before M4
- separate clearly:
  - already run restricted-pilot work
  - implemented but intentionally unrun formal work
  - the next active line, which is M4 on COCO-only engineering scope
- close the GitHub issue as deferred rather than leaving it ambiguous

## Resource Boundary

- do not relabel restricted-pilot results as formal benchmark evidence
- do not write closeout text that claims the formal line was run
- do not keep the formal path open as if it were the next required action

## Non-Goals

- no additional method work
- no forced formal run without restored prerequisites
- no benchmark overclaim

## Deliverable

- M3 closeout doc with explicit deferred-formal wording
- a clean handoff into M4 on the COCO-only engineering line

## Acceptance

- the repo docs explicitly state that formal M3 was not executed
- restricted-pilot artifacts remain the only executed evidence base
- the formal path is closed as deferred, not left in an ambiguous open state
