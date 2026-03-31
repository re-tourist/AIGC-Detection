# milestone_closeout

## Milestone Info

- Milestone ID: `m1_data_metric_pipeline_bootstrap`
- Milestone name: `M1: Data and Metric Pipeline Bootstrap`
- Status:
  - [x] complete
  - [ ] partially complete
  - [ ] blocked
  - [ ] handed off with risks
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
- a real BR-Gen source-drop rehearsal path that can generate an operational manifest and run the existing runner on local mirrored data

The repository is now ready to enter M2 from an implementation standpoint. The real-data rehearsal gap has been closed on the current local BR-Gen source drop. The main remaining caveat is that this source drop contains localized forged positives plus masks and image catalogs, so the rehearsal is an ingestion/path validation step rather than a benchmark-quality evaluation.

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

- [x] Real BR-Gen source-drop rehearsal was executed on local data
  - Files:
    - `src/aigc_detection/data/br_gen.py`
    - `scripts/prepare_br_gen_rehearsal.py`
    - `docs/data/DATA_LAYOUT.md`
  - Validation:
    - generated an operational rehearsal manifest plus dummy predictions from `data/BR-Gen`
    - ran the existing minimal evaluation runner on the generated manifest
  - Result:
    - yes

---

## 3. What Was Not Completed

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

- `src/aigc_detection/data/br_gen.py`
  - Role:
    - turns a direct `data/BR-Gen` source drop into an operational rehearsal manifest and dummy predictions
  - M1 responsibility:
    - bridges real local data into the frozen manifest contract without forcing manual reorganization

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

- `scripts/prepare_br_gen_rehearsal.py`
  - Role:
    - prepares rehearsal manifest and dummy predictions from the current BR-Gen source drop
  - Reusability:
    - yes, for direct source-drop ingestion during M2 preparation

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
- BR-Gen rehearsal preparation:
  - `$env:PYTHONPATH='src'; python scripts\\prepare_br_gen_rehearsal.py --source-root data\\BR-Gen --output-root data\\mirrored\\br_gen\\subsets\\rehearsal`
- BR-Gen rehearsal run:
  - `$env:PYTHONPATH='src'; python scripts\\run_minimal_eval.py --manifest data\\mirrored\\br_gen\\subsets\\rehearsal\\manifest\\manifest.jsonl --predictions data\\mirrored\\br_gen\\subsets\\rehearsal\\predictions\\dummy_predictions.jsonl --output-dir outputs\\stage1_br_gen_rehearsal`
  - rehearsal preparation produced `27` usable samples and skipped `29` forged files without matching masks

### What These Checks Actually Prove

- Proved:
  - M1 code paths work end to end on repo-tracked smoke fixtures
  - grouped reporting does not silently invent slice metadata
  - minimal artifacts are reproducible and traceable to manifest/prediction inputs
  - the current local `data/BR-Gen` source drop can be bridged into the frozen M1 manifest contract and consumed by the existing runner
- Not proved:
  - Community Forensics outputs may still need an adapter
  - no formal localized-failure validation result exists yet

### Missing or Weak Validation

- Missing validation 1:
  - rehearse using baseline-like prediction exports rather than only the repo fixture file
- Missing validation 2:
  - replay once more after the BR-Gen source drop includes real-image binaries if future M2 work needs negative-path rehearsal on the same dataset tree

---

## 6. Risks and Known Limitations

### P0 / blocking

- none

### P1 / serious but not blocking

- none

### P2 / should improve later

- AUROC / Accuracy / fake_recall are enough for M1, but later stages may need adapter code if baseline outputs are not already JSONL keyed by `sample_id`
- repo smoke fixtures are intentionally tiny and perfectly separable; they should never be treated as evidence for research claims
- the current BR-Gen source drop is positive-only for rehearsal purposes, so the real-data run validates ingestion and artifact paths rather than full positive/negative benchmark behavior

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

- begin `M2` by adapting Community Forensics outputs into the existing prediction JSONL format and replaying them through the current runner

### Recommended first files to read

- `docs/handoff/milestone_closeout_stage1_data_metric_bootstrap.md`
- `docs/contracts/contract_freeze_stage1_data_metric_bootstrap.md`
- `src/aigc_detection/eval/runner.py`
- `scripts/run_minimal_eval.py`

### Recommended first checks

- run Community Forensics predictions through the existing runner without changing the M1 contract
- confirm whether the next BR-Gen copy includes real-image binaries or remains a positive-only localized source drop
- confirm which localized slice metadata is explicitly present before expanding grouped reporting
- place the real rehearsal subset under the repo-side mirrored layout documented in `docs/data/DATA_LAYOUT.md`

### Recommended decision to make before coding

- decide what adapter layer is needed if Community Forensics emits predictions in a different format
- decide whether future BR-Gen copies should land directly under `data/mirrored/br_gen/subsets/rehearsal/` or continue to arrive as source drops under `data/BR-Gen`

---

## 9. Handoff Guidance

- Do not reinterpret repo smoke fixtures as experiment data.
- Do not widen M1 contracts just because a baseline emits a different prediction format; add an adapter in M2 instead.
- Do not unblock `edit_area_ratio` bins until a derivation rule is explicitly frozen.
- The first M2 step should be a real-data rehearsal, not immediate model integration.

---

## 10. Final Verdict

- [x] milestone can be cleanly closed
- [ ] milestone can be closed with documented limitations
- [ ] milestone should remain open pending one last validation
- [ ] milestone should not be closed because the result is not yet reliable

Final conclusion:
- M1 code, docs, and real-data rehearsal path are complete enough to close the milestone and enter M2.
