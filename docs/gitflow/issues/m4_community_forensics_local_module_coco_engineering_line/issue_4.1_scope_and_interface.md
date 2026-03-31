# Issue 4.1 - Freeze M4 scope and local-module interface on the COCO engineering line

GitHub issue:
- #23
- `https://github.com/re-tourist/AIGC-Detection/issues/23`

## Background

M3 is being closed as a restricted-pilot-only engineering handoff. The next
active line is no longer formal validation; it is a COCO-only method
engineering line built on top of the Community Forensics baseline.

The M3 failure evidence already points to the current weak slices:

- `stuff`
- `small / medium` edit area

Before implementing a local module, M4 must freeze:

- the active evaluation scope
- the allowed data boundary
- the narrowest viable integration point in the current baseline path

## Suggested Branch

`codex/stage4-scope-and-interface`

## Goal

Freeze a minimal and executable M4 scope so that the local module work does not
silently drift into formal benchmark, data expansion, or metric redefinition.

## Tasks

- confirm that M4 stays inside:
  - `evaluation_scope = restricted_pilot`
  - `dataset scope = COCO-only`
- document the baseline path that M4 will build on
- identify the narrowest local-module insertion point in the Community
  Forensics code path
- define what artifacts the comparison must reuse
- define what M4 success means for an engineering-line comparison

## Resource Boundary

- allowed:
  - Community Forensics baseline reuse
  - local module integration planning
  - COCO-only restricted-pilot comparisons
- not allowed:
  - formal M3 continuation
  - ImageNet / Places negatives
  - contract changes to metric semantics

## Non-Goals

- no model-code implementation yet
- no benchmark claim drafting
- no paper-result packaging

## Deliverable

- a frozen M4 interface and scope note
- an explicit list of files and artifacts that the implementation issue must
  build on

## Acceptance

- the scope is narrow enough that the next issue can code immediately
- the active comparison boundary is explicit
- the local module insertion point is concrete, not aspirational
