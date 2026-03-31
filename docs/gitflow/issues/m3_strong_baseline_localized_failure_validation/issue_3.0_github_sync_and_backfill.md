# Issue 3.0 — Sync M3 GitHub milestone and issue set

GitHub issue:
- #17
- `https://github.com/re-tourist/AIGC-Detection/issues/17`

## Background

The repository already contains M3 milestone and issue docs, but GitHub does
not yet reflect the current M3 execution state. In particular:

- the expanded full-COCO restricted pilot is now complete
- formal M3 remains blocked
- M3 issue docs must be synchronized to GitHub without turning GitHub into the
  only source of truth

This issue exists to track the repo-admin work needed to backfill and sync the
M3 milestone and issue set.

## Suggested Branch

`codex/stage3-github-sync`

## Goal

Refresh the local M3 gitflow docs, backfill the M3 GitHub milestone and issue
set, and write issue numbers and URLs back into the repository.

## Tasks

- refresh the M3 milestone doc to match the current restricted-pilot and formal
  M3 state
- normalize the M3 issue docs to the fixed GitHub issue-body section order
- create or update the GitHub milestone `M3: Strong Baseline Localized Failure Validation`
- create GitHub issues for Issue 3.0 through Issue 3.5 from the repo docs
- set issue states to match the current source-of-truth status
- write issue numbers, URLs, and states back into the repo issue index

## Resource Boundary

- repo docs remain the source of truth
- do not mix code-path changes into this sync work
- do not overclaim formal M3 completion in GitHub metadata

## Non-Goals

- no model, data, or evaluation logic changes
- no formal M3 closeout
- no benchmark interpretation changes beyond syncing the documented state

## Deliverable

- refreshed M3 gitflow docs
- backfilled GitHub milestone and issue set
- repo issue index with GitHub issue numbers and URLs

## Acceptance

- the M3 milestone doc reflects the current real state
- GitHub issues 3.0 through 3.5 exist and map cleanly to repo docs
- completed issues are backfilled as closed
- the blocked formal-closeout issue remains open
- repo docs contain the resulting GitHub identifiers
