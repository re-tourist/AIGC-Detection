# Issue 6.3 - Metadata and slice reporting alignment

## Background

The repo already has `generator_id`, `region_type`, `degradation`, and
mask-derived area support in the localized pipeline, but it does not yet expose
the paper-facing slice grammar required for M6.

## Suggested Branch

`codex/stage6-slice-reporting`

## Goal

Add a normalization/reporting layer that emits paper-style slice summaries
without changing the raw manifest schema or pretending the task has become a
full localization benchmark.

## Deliverables

- `generator_family` canonicalization and mapping
- `unknown / unsupported` exclusion handling for Split A
- `repo_frozen_alignment_bins` for `small / medium / large`
- `clean / degraded` dual reporting
- always-on `jpeg / resize / blur / crop` detail rows when metadata is present
- standardized slice rows in JSON / CSV / Markdown

## Acceptance Criteria

- rows exist for `overall`, `background`, `stuff`, `GAN`, `Diffusion`,
  `small`, `medium`, `large`, `clean`, `degraded`, and degradation detail
- unknown families do not enter the Split A main table
- exclusion counts are audited
- row-level `status + notes + N/A` behavior is stable
- the localized evaluator remains image-level and diagnostic-first
