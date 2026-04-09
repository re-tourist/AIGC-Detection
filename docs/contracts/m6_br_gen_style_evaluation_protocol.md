# M6 BR-Gen-style Evaluation Protocol

## Purpose

Define the frozen M6 evaluation/reporting contract that aligns the repo's
localized evaluation grammar with BR-Gen-style reporting where possible, while
preserving the real project boundary.

## Boundary

This contract is:

- a protocol alignment contract
- a reporting alignment contract
- a metadata normalization contract

This contract is not:

- a new model contract
- a segmentation-heavy localization benchmark contract
- a claim that the repo fully reproduces unpublished BR-Gen implementation details

## Legacy Metrics

Legacy metrics remain preserved and additive:

- `accuracy`
- `auroc`
- `fake_recall`

`fake_recall` keeps its legacy meaning: positive-class recall computed at the
legacy decision threshold.

## Paper-style Metrics

The same evaluator path now also exports:

- `f1_at_paper_style_threshold`
- `paper_manipulated_recall_at_0_5`
- `paper_real_recall_at_0_5`

### Threshold Rule

- `legacy_threshold` is whatever threshold the caller passes to the legacy eval
- `paper_style_threshold = 0.5` is a repo-frozen M6 alignment contract
- this `0.5` threshold is used to construct BR-Gen-style `Recall@50` reporting
- this does not claim exact equivalence to unpublished paper implementation details

## Difference Audit Fields

The following fields must appear in `overall_metrics.json` and slice rows:

- `legacy_fake_recall_value`
- `paper_manipulated_recall_at_0_5`
- `legacy_threshold`
- `paper_style_threshold`
- `legacy_equals_paper_manipulated_recall`

Rules:

- `legacy_equals_paper_manipulated_recall = true` only if both values are defined and numerically equal
- if either side is undefined, the field is `null`
- undefined values are `null` in JSON and `N/A` in CSV / Markdown

## Slice Grammar

### Overall

- `overall`

### Split A

Derived `generator_family`:

- canonicalization rule:
  - `lowercase(trim(raw_generator_id)).remove('-', '_', ' ')`
- mapping:
  - `LaMa`, `MAT` -> `GAN`
  - `BrushNet`, `PowerPaint`, `SDXL` -> `Diffusion`
- fallback:
  - missing / empty -> `unknown`
  - unmapped non-empty -> `unsupported`

`unknown / unsupported` do not enter the Split A main table. They must still be
counted in the audit payload.

### Split B

- `region_type = background / stuff`

### Area Bins

`area_bin` is derived from mask area ratio using `repo_frozen_alignment_bins`:

- `small < 0.05`
- `0.05 <= medium < 0.20`
- `large >= 0.20`

This aligns the paper naming grammar only. It does not claim exact equivalence
to the paper's original area contract.

### Degradation

Main reporting:

- `clean`
- `degraded`

Detail reporting:

- `clean`
- `jpeg`
- `resize`
- `blur`
- `crop`

If metadata exists, degradation detail rows are always exported to JSON / CSV.

## Artifact Contract

### `overall_metrics.json`

Contains:

- legacy metrics
- paper-style metrics
- threshold audit fields
- overall / clean / degraded rows
- IoU deferred note

### `slice_metrics.json`

Contains top-level run metadata plus stable row objects with:

- `dimension`
- `slice_value`
- `sample_count`
- `positive_count`
- `negative_count`
- `status`
- `notes`
- `legacy_fake_recall_value`
- `paper_manipulated_recall_at_0_5`
- `paper_real_recall_at_0_5`
- `f1_at_paper_style_threshold`
- `auroc`
- `accuracy`
- `legacy_threshold`
- `paper_style_threshold`
- `legacy_equals_paper_manipulated_recall`
- `included_in_paper_main_table`

Allowed status values:

- `ok`
- `empty_slice`
- `undefined_metric`
- `excluded`
- `blocked`

### `slice_metrics.csv`

Exports the same row schema in flat form. Undefined values must appear as
`N/A`, never as `0`.

### `paper_table_summary.md`

Must contain:

- overall summary
- clean vs degraded
- Split A
- Split B
- area bins
- degradation detail
- alignment / deferred notes

The markdown header must explicitly say:

- this is image-level localized sensitivity reporting
- the current evidence comes from the restricted pilot diagnostic pipeline
- this is not a full localization benchmark

### `protocol_alignment_audit.json`

Must contain:

- `fully_aligned`
- `partially_aligned`
- `deferred`
- `blocked_reasons`
- `excluded_counts`
- `generator_family_mapping`
- `repo_frozen_alignment_bins`
- `paper_style_threshold_contract_note`

## Alignment Status

### Fully aligned

- dual reporting is exported
- paper-style summary artifacts are emitted
- Split A / Split B / area-bin naming grammar is supported
- clean/degraded dual reporting exists

### Partially aligned

- `generator_family` is derived, not raw
- `area_bin` is repo-frozen naming alignment only
- conditioned slices still use the repo's shared-negative localized contract
- restricted pilot evidence remains diagnostic, not formal benchmark evidence

### Deferred

- IoU

Reason:

- the repo does not expose a stable mask prediction path
- the repo does not expose a frozen localization eval contract for mask outputs

## Sample Output Pointer

Fixture-backed example artifacts live under:

- `docs/handoff/m6_protocol_alignment_fixture/`
