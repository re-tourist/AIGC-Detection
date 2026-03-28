# milestone_closeout

## Milestone Info

- Milestone ID: `m1_data_metric_pipeline_bootstrap`
- Milestone name: `M1: Data and Metric Pipeline Bootstrap`
- Status:
  - [ ] complete
  - [ ] partially complete
  - [ ] blocked
  - [x] handed off with risks
- Date: `2026-03-28`
- Related stage / branch:
  - `codex/stage1-data-metric-bootstrap`
- Related plan doc:
  - `docs/plan/plan_stage1_data_metric_bootstrap.md`
- Related issue doc:
  - `docs/plan/issue_stage1_data_metric_bootstrap.md`

---

## 1. Executive Summary

M1 was intended to build only the minimum data and metric substrate needed before Community Forensics integration and the later localized-failure validation experiment.

This milestone now has:
- frozen M1 docs and contracts
- a manifest-driven loader with normalized sample objects
- a minimal metric core
- a minimal evaluation runner that writes JSON / CSV / Markdown / config snapshot artifacts

The repository is ready to enter M2 from an implementation standpoint, but not yet from real-data readiness. The largest remaining gap is that the runner has only been replayed on repo-tracked smoke fixtures, not on the user's actual mirrored subset from the Linux server.

---

## 2. What Was Completed

- [x] Active M1 contract / plan / issue docs were frozen and synced
  - Files:
    - `docs/ai/PROJECT_CONTEXT.md`
    - `docs/plan/plan_stage1_data_metric_bootstrap.md`
    - `docs/plan/issue_stage1_data_metric_bootstrap.md`
    - `docs/contracts/contract_freeze_stage1_data_metric_bootstrap.md`
  - Validation:
    - manual cross-read of linked docs and file references
  - Result:
    - yes

- [x] Local mirror manifest loader and normalized sample objects were implemented
  - Files:
    - `src/aigc_detection/data/schema.py`
    - `src/aigc_detection/data/manifest.py`
    - `tests/test_manifest_loader.py`
  - Validation:
    - loader unit tests on repo-tracked local-mirror fixtures
  - Result:
    - yes for smoke scope

- [x] Minimal metric core was implemented
  - Files:
    - `src/aigc_detection/metrics/core.py`
    - `tests/test_metric_core.py`
  - Validation:
    - metric unit tests covering overall metrics, grouped views, and blocked slice dimensions
  - Result:
    - yes

- [x] Minimal evaluation runner and artifact save path were implemented
  - Files:
    - `src/aigc_detection/eval/predictions.py`
    - `src/aigc_detection/eval/runner.py`
    - `scripts/run_minimal_eval.py`
    - `tests/test_minimal_eval_runner.py`
  - Validation:
    - end-to-end smoke run on repo fixtures producing `summary.json`, `metrics.csv`, `smoke_report.md`, and `config_snapshot.json`
  - Result:
    - yes for local smoke scope

---

## 3. What Was Not Completed

- [x] Real mirrored-subset replay using the user's Linux dataset handoff
  - Why not completed:
    - the actual local mirror pack has not been copied into the workspace yet
  - Type:
    - external data dependency / handoff gap
  - Should it enter the next milestone:
    - yes; make it the first practical check before M2 baseline integration work

- [x] P2 slice reporting by `region_type`, `subtlety`, and `edit_area_ratio`
  - Why not completed:
    - intentionally blocked by the frozen M1 contract
  - Type:
    - explicit scope boundary, not implementation slippage
  - Should it enter the next milestone:
    - only if a later contract freeze explicitly enables it

---

## 4. Key Files and Changes

### Code

- `src/aigc_detection/data/manifest.py`
  - Role:
    - validates manifest JSONL records against the frozen M1 schema
  - M1 responsibility:
    - turns local-mirror records into normalized samples

- `src/aigc_detection/metrics/core.py`
  - Role:
    - computes P0 metrics and supported P1 grouped views
  - M1 responsibility:
    - provides the metric substrate for later baseline evaluation

- `src/aigc_detection/eval/runner.py`
  - Role:
    - wires manifest loading, prediction loading, metric reporting, and artifact writing
  - M1 responsibility:
    - provides the minimal end-to-end smoke execution path

### Docs

- `docs/contracts/contract_freeze_stage1_data_metric_bootstrap.md`
  - Role:
    - source of truth for schema, metric priority, artifact contract, and stop rules
  - Synced with implementation:
    - yes

- `docs/review/review_stage1_data_metric_bootstrap.md`
  - Role:
    - records the final M1 self-review
  - Synced with implementation:
    - yes

- `docs/handoff/milestone_closeout_stage1_data_metric_bootstrap.md`
  - Role:
    - handoff for the next milestone
  - Synced with implementation:
    - yes

### Config / Scripts / Assets

- `scripts/run_minimal_eval.py`
  - Role:
    - CLI entrypoint for the minimal M1 evaluation path
  - Reusability:
    - yes, for local smoke and real mirrored-subset rehearsal

- `tests/fixtures/local_mirror/manifest.jsonl`
  - Role:
    - repo-tracked smoke fixture manifest
  - Reusability:
    - yes, but only as a smoke fixture, not as experiment evidence

- `tests/fixtures/local_mirror/predictions.jsonl`
  - Role:
    - repo-tracked smoke prediction file
  - Reusability:
    - yes, for runner verification only

---

## 5. Validation Summary

### Validation Run

- manifest / loader / metric / runner unit tests:
  - `$env:PYTHONPATH='src'; python -m unittest discover -s tests -p 'test_*.py' -v`
- CLI smoke run:
  - `$env:PYTHONPATH='src'; python scripts\\run_minimal_eval.py --manifest tests\\fixtures\\local_mirror\\manifest.jsonl --predictions tests\\fixtures\\local_mirror\\predictions.jsonl --output-dir outputs\\stage1_m1_runner_smoke`

### What These Checks Actually Prove

- Proved:
  - M1 code paths work end to end on repo-tracked smoke fixtures
  - grouped reporting does not silently invent slice metadata
  - minimal artifacts are reproducible and traceable to manifest/prediction inputs
- Not proved:
  - the user's actual mirrored subset may still differ from current manifest/path assumptions
  - Community Forensics outputs may still need an adapter
  - no formal localized-failure validation result exists yet

### Missing or Weak Validation

- Missing validation 1:
  - replay the runner on a real mirrored subset copied from the Linux server
- Missing validation 2:
  - rehearse using baseline-like prediction exports rather than only the repo fixture file

---

## 6. Risks and Known Limitations

### P0 / blocking

- none

### P1 / serious but not blocking

- the actual mirrored subset has not yet been used to validate manifest layout, path assumptions, and metadata availability

### P2 / should improve later

- AUROC / Accuracy / fake_recall are enough for M1, but later stages may need adapter code if baseline outputs are not already JSONL keyed by `sample_id`
- repo smoke fixtures are intentionally tiny and perfectly separable; they should never be treated as evidence for research claims

---

## 7. Contract / Scope Notes

- [x] fully executed inside the frozen contract
- [ ] minor deviation occurred and was documented
- [ ] contract-level issue occurred
- [ ] actual scope drift occurred
- [ ] no formal contract freeze existed

Additional notes:
- P2 slice dimensions remained blocked
- no baseline integration or method work was introduced
- generated smoke outputs remain local artifacts and are ignored by git

---

## 8. Recommended Next Entry Point

### Recommended first task

- copy a real mirrored subset plus manifest metadata from the Linux server into the local workspace and rerun the minimal M1 evaluation path

### Recommended first files to read

- `docs/handoff/milestone_closeout_stage1_data_metric_bootstrap.md`
- `docs/contracts/contract_freeze_stage1_data_metric_bootstrap.md`
- `src/aigc_detection/eval/runner.py`
- `scripts/run_minimal_eval.py`

### Recommended first checks

- run the loader against the real mirrored manifest and confirm path/schema compatibility
- run the minimal runner with a dummy or baseline-like prediction export and inspect output artifacts
- confirm which localized slice metadata is explicitly present before expanding grouped reporting

### Recommended decision to make before coding

- decide whether the real mirrored subset needs a manifest-generation helper or whether manual manifests are enough for M2
- decide what adapter layer is needed if Community Forensics emits predictions in a different format

---

## 9. Handoff Guidance

- Do not reinterpret repo smoke fixtures as experiment data.
- Do not widen M1 contracts just because a baseline emits a different prediction format; add an adapter in M2 instead.
- Do not unblock `edit_area_ratio` bins until a derivation rule is explicitly frozen.
- The first M2 step should be a real-data rehearsal, not immediate model integration.

---

## 10. Final Verdict

- [ ] milestone can be cleanly closed
- [x] milestone can be closed with documented limitations
- [ ] milestone should remain open pending one last validation
- [ ] milestone should not be closed because the result is not yet reliable

Final conclusion:
- M1 code and documentation are ready for M2 reuse, but the real mirrored-subset rehearsal still needs to happen before baseline integration starts.
