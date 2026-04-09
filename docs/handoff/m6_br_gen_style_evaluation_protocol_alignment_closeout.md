# M6 BR-Gen-style Evaluation Protocol Alignment Closeout

## Status

- Local implementation completed
- Local validation completed
- GitHub milestone `#6` has been created and closed
- Restricted pilot evidence remains diagnostic evidence
- No benchmark finalization claim is made here

## Scope Recap

M6 was intentionally scoped to calibrate the evaluation ruler before any new
method push.

It did:

- preserve legacy metrics
- add paper-style metrics and reporting artifacts
- align metadata slices and reporting grammar
- add explicit threshold and exclusion audits

It did not:

- introduce a new model
- change the task into segmentation-heavy localization
- claim IoU comparability

## Audit Summary

### Legacy metric audit

Legacy metrics were already present and remain preserved:

- `accuracy`
- `auroc`
- `fake_recall`

The repo now exports explicit difference-audit fields so legacy and paper-style
positive recall can be compared row by row.

### Metadata audit

Already available in the active restricted-pilot line:

- `region_type`
- `generator_id`
- `degradation`
- `mask_path`
- `meta.base_sample_id`
- `meta.selection_role`
- `meta.evaluation_scope`

Derived in M6:

- `generator_family`
- `area_bin`
- `degraded`

Not available as a frozen contract:

- mask-level prediction output suitable for IoU reporting

## Alignment Classification

### Fully aligned

- dual reporting of legacy and paper-style metrics
- standardized JSON / CSV / Markdown output artifacts
- Split A / Split B / area-bin reporting grammar
- clean vs degraded dual reporting plus degradation detail rows

### Partially aligned

- `generator_family` is derived from canonicalized `generator_id`
- `area_bin` uses `repo_frozen_alignment_bins`
- slice evaluation still uses the repo's shared-negative localized contract
- restricted pilot evidence remains diagnostic-first

### Deferred / blocked

- IoU is deferred because the repo has no stable repo-native mask prediction path
- IoU is deferred because the repo has no frozen localization evaluation contract for masks

## Implementation Summary

Code changes:

- shared binary metric kernel in `src/aigc_detection/metrics/core.py`
- protocol-alignment artifact writer in `src/aigc_detection/eval/protocol_alignment.py`
- additive integration into `src/aigc_detection/eval/m3_runner.py`
- public exports in `src/aigc_detection/eval/__init__.py`
- CLI visibility in `scripts/run_m3_formal_eval.py`

Docs and gitflow:

- M6 milestone doc
- M6 issue set docs
- M6 protocol contract doc
- roadmap update
- fixture-backed sample artifacts

## Validation

Local validation executed:

- module compile smoke
- full `unittest discover` run under `PYTHONPATH=src`

Current local result:

- 64 tests passed

Validation boundary:

- local validation proves code path, artifact schema, and regression safety
- local validation does not upgrade the restricted pilot into a formal benchmark claim

## Sample Output

Fixture-backed sample artifacts:

- `docs/handoff/m6_protocol_alignment_fixture/overall_metrics.json`
- `docs/handoff/m6_protocol_alignment_fixture/slice_metrics.json`
- `docs/handoff/m6_protocol_alignment_fixture/slice_metrics.csv`
- `docs/handoff/m6_protocol_alignment_fixture/paper_table_summary.md`
- `docs/handoff/m6_protocol_alignment_fixture/protocol_alignment_audit.json`

The sample output is useful for reporting layout and artifact contract checks.
It is not scientific evidence beyond that fixture scope.

## GitHub Maintenance

- GitHub milestone: https://github.com/re-tourist/AIGC-Detection/milestone/6
- PR target branch: `dev`
- PR status: pending publication from the current checkout after commit/push
