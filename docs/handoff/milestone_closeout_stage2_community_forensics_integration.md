# milestone_closeout

## Milestone Info

- Milestone ID: `m2_community_forensics_integration`
- Milestone name: `M2: Community Forensics Integration`
- Status:
  - [x] complete
  - [ ] partially complete
  - [ ] blocked
  - [ ] handed off with risks
- Date: `2026-03-29`
- Related stage / branch:
  - `codex/stage2-community-forensics-integration`
- Related plan doc:
  - `docs/gitflow/milestones/m2_community_forensics_integration.md`
- Related issue doc:
  - `docs/gitflow/issues/m2_community_forensics_integration/README.md`

---

## 1. Executive Summary

M2 was intended to integrate Community Forensics as a baseline candidate under the frozen M1 contract, without reproducing the paper protocol or changing the runner schema.

This milestone now has:
- explicit M2 protocol, sample-alignment, score, and failure definitions
- a Community Forensics prediction adapter for repo-compatible JSONL
- a temporary BR-Gen COCO-balanced smoke fixture generator
- a Community Forensics inference export path that emits repo-compatible `sample_id` / `score` records from the smoke manifest
- a local end-to-end smoke run through the existing M1 runner

The repo is now ready to close M2 from an integration standpoint. The remaining caveats are documented: upstream `external/Community-Forensics/eval.py` was not re-run on the final smoke fixture in this Windows environment, and the current BR-Gen source drop still does not provide a formal full comparison between `full_image_fake` and `localized_edit`.

---

## 2. What Was Completed

- [x] M2 contract docs were frozen and synced
  - Files:
    - `docs/gitflow/milestones/m2_community_forensics_integration.md`
    - `docs/gitflow/issues/m2_community_forensics_integration/issue_2.1_intake_and_contract.md`
    - `docs/gitflow/issues/m2_community_forensics_integration/issue_2.2_prediction_adapter.md`
    - `docs/gitflow/issues/m2_community_forensics_integration/issue_2.3_runner_sanity.md`
  - Validation:
    - manual cross-read of protocol, alignment, score, and failure rules

- [x] Community Forensics prediction adapter was implemented
  - Files:
    - `src/aigc_detection/adapters/community_forensics.py`
    - `scripts/convert_community_forensics_predictions.py`
    - `tests/test_community_forensics_adapter.py`
  - Validation:
    - unit tests for relative-path alignment, mapping-table alignment, heuristic rejection, and score contract

- [x] Temporary BR-Gen COCO smoke fixture generation was implemented
  - Files:
    - `src/aigc_detection/data/br_gen_cf_smoke.py`
    - `scripts/prepare_br_gen_coco_smoke.py`
    - `tests/test_br_gen_coco_smoke.py`
  - Validation:
    - generated a temporary `data/tmp/cf_smoke/manifest.jsonl`
    - filtered out one unreadable BR-Gen fake image
    - produced a balanced 15-real / 15-fake smoke set

- [x] Community Forensics inference export path was implemented
  - Files:
    - `scripts/export_community_forensics_predictions.py`
  - Validation:
    - exported repo-compatible `sample_id` / `score` predictions from the smoke manifest on CPU

- [x] Local runner replay on the smoke fixture completed
  - Files:
    - `scripts/run_minimal_eval.py`
    - `src/aigc_detection/eval/predictions.py`
    - `src/aigc_detection/metrics/core.py`
    - `scripts/run_m2_community_forensics_smoke.py`
  - Validation:
    - `run_minimal_eval.py` consumed the exported predictions
    - produced `summary.json`, `metrics.csv`, `smoke_report.md`, and `config_snapshot.json`
    - overall smoke metrics were `AUROC=1.0`, `Accuracy=0.9666666666666667`, `fake_recall=0.9333333333333333`
    - the one-shot wrapper wrote `data/tmp/cf_smoke/feedback.json`

---

## 3. What Was Not Completed

- [ ] Upstream Community Forensics `eval.py` replay on the final smoke fixture
  - Why not completed:
    - the current local Windows environment is not suitable for the upstream `torchrun` / NCCL path
  - Type:
    - environment limitation, not a contract problem
  - Should it enter the next milestone:
    - only as an optional Linux/GPU confirmation step

- [ ] Full `full_image_fake` vs `localized_edit` comparison
  - Why not completed:
    - the current mirrored rehearsal manifest remains localized-edit-only
  - Type:
    - source-drop limitation, not an implementation bug
  - Should it enter the next milestone:
    - yes, if M3 is the formal localized-failure validation stage

---

## 4. Key Files and Changes

### Code

- `src/aigc_detection/adapters/community_forensics.py`
  - Role:
    - converts Community Forensics-style outputs into the frozen repo prediction JSONL contract

- `src/aigc_detection/data/br_gen_cf_smoke.py`
  - Role:
    - prepares the temporary COCO-balanced smoke fixture and its manifest

- `scripts/export_community_forensics_predictions.py`
  - Role:
    - runs Community Forensics inference on the smoke manifest and exports repo-compatible predictions

- `scripts/run_minimal_eval.py`
  - Role:
    - replays the exported predictions through the existing M1 runner

### Docs

- `docs/gitflow/milestones/m2_community_forensics_integration.md`
  - Role:
    - source of truth for the frozen M2 integration contract
  - Synced with implementation:
    - yes

- `docs/gitflow/issues/m2_community_forensics_integration/issue_2.3_runner_sanity.md`
  - Role:
    - describes the smoke fixture and runner sanity check
  - Synced with implementation:
    - yes

- `docs/run_order.md`
  - Role:
    - records the smoke prep, export, runner replay, and optional upstream sanity commands
  - Synced with implementation:
    - yes

### Config / Scripts / Assets

- `data/tmp/cf_smoke/`
  - Role:
    - temporary smoke artifact root
  - Reusability:
    - yes, but only as a throwaway fixture

- `external/Community-Forensics/`
  - Role:
    - local clone of the upstream Community Forensics codebase
  - Reusability:
    - yes, for Linux/GPU confirmation and future baseline comparisons

---

## 5. Validation Summary

### Validation Run

- repository test suite:
  - `$env:PYTHONPATH='src'; python -m unittest discover -s tests -p 'test_*.py' -v`
- smoke fixture preparation:
  - `$env:PYTHONPATH='src'; python scripts\\prepare_br_gen_coco_smoke.py`
- Community Forensics export:
  - `$env:PYTHONPATH='src'; python scripts\\export_community_forensics_predictions.py --manifest data\\tmp\\cf_smoke\\manifest.jsonl --output data\\tmp\\cf_smoke\\predictions.jsonl --device cpu --batch-size 8`
- minimal runner replay:
  - `$env:PYTHONPATH='src'; python scripts\\run_minimal_eval.py --manifest data\\tmp\\cf_smoke\\manifest.jsonl --predictions data\\tmp\\cf_smoke\\predictions.jsonl --output-dir data\\tmp\\cf_smoke\\eval`

### What These Checks Actually Prove

- Proved:
  - the M2 adapter contract is internally consistent
  - the smoke fixture can be rebuilt from the BR-Gen source drop plus COCO real images
  - Community Forensics inference can produce repo-compatible predictions from the smoke manifest
  - the existing M1 runner can consume those predictions and produce the expected artifacts
  - the one-shot wrapper can rebuild the smoke fixture and emit a concrete local feedback file
- Not proved:
  - the upstream `external/Community-Forensics/eval.py` Linux/GPU path on the final smoke fixture
  - the formal `full_image_fake` vs `localized_edit` comparison

### Missing or Weak Validation

- Missing validation 1:
  - Linux/GPU replay of the upstream Community Forensics `eval.py`
- Missing validation 2:
  - a source-drop with both `full_image_fake` and `localized_edit` groups if M3 needs a direct comparison

---

## 6. Risks and Known Limitations

### P0 / blocking

- none

### P1 / serious but not blocking

- the final upstream eval path still needs a Linux/GPU environment for a direct smoke confirmation

### P2 / should improve later

- the BR-Gen smoke fixture is temporary and should be deleted after use
- one unreadable BR-Gen fake image was skipped, so the smoke set is 15 pairs instead of the original 16 COCO candidates
- the current smoke result is provisional evidence, not a final research claim

---

## 7. Contract / Scope Notes

- [x] fully executed inside the frozen contract
- [ ] minor deviation occurred and was documented
- [ ] contract-level issue occurred
- [ ] actual scope drift occurred
- [ ] no formal contract freeze existed

Additional notes:
- no M1 contract changes were made
- no generator-diverse retraining was introduced
- the temporary smoke root stays under `data/tmp/`

---

## 8. Recommended Next Entry Point

### Recommended first task

- start M3 by using the repo-side smoke evidence and then decide whether a Linux/GPU upstream confirmation is still needed

### Recommended first files to read

- `docs/gitflow/milestones/m3_strong_baseline_localized_failure_validation.md`
- `docs/handoff/milestone_closeout_stage2_community_forensics_integration.md`
- `docs/run_order.md`

### Recommended first checks

- verify whether M3 needs the upstream `eval.py` replay or only the repo runner evidence
- confirm whether the next BR-Gen source drop will include real-image binaries directly
- confirm the target comparison groups before any stronger baseline validation

### Recommended decision to make before coding

- decide whether the Linux/GPU upstream eval is required before M3
- decide whether to keep the temporary COCO smoke fixture as a reusable debug asset or delete it immediately

---

## 9. Handoff Guidance

- Do not treat the temporary smoke fixture as benchmark evidence.
- Do not widen the frozen M1 contract just to make Community Forensics fit.
- Do not infer new slice metadata from the source drop.
- The repo already has an integration path; the remaining gap is formal upstream confirmation on Linux/GPU if the next stage requires it.

---

## 10. Final Verdict

- [x] milestone can be cleanly closed
- [ ] milestone can be closed with documented limitations
- [ ] milestone should remain open pending one last validation
- [ ] milestone should not be closed because the result is not yet reliable

Final conclusion:
- M2 has enough implemented code, docs, and local smoke validation to close cleanly, with the remaining upstream Linux/GPU eval and formal full comparison explicitly documented as non-blocking limitations.
