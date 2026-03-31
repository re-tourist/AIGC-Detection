# review_stage1_data_metric_bootstrap

## 1. Overall Verdict

- verdict:
  - approve

This M1 implementation stays within the frozen bootstrap scope and is acceptable to close locally with documented limitations.

---

## 2. Scope Status

- status:
  - [x] in scope
  - [ ] partly out of scope
  - [ ] clearly out of scope

Evidence:
- implementation stays limited to contract-backed docs, manifest loading, metric computation, and a minimal evaluation runner
- no baseline integration, training path, or Community Forensics code was introduced
- `localized_edit` remains the primary path and `full_image_fake` remains compatibility-only

---

## 3. Contract Status

- status:
  - [x] no contract issue found
  - [ ] possible contract issue
  - [ ] clear contract violation

Evidence:
- required / optional / derived field boundaries remain aligned with `docs/contracts/contract_freeze_stage1_data_metric_bootstrap.md`
- `edit_area_ratio` is still blocked as a derived field without a frozen derivation rule
- P2 slice dimensions are reported as blocked rather than silently inferred

---

## 4. Validation Status

- status:
  - [x] validation adequate
  - [ ] validation incomplete but acceptable
  - [ ] validation insufficient

Validation actually run:
- `$env:PYTHONPATH='src'; python -m unittest discover -s tests -p 'test_*.py' -v`
- `$env:PYTHONPATH='src'; python scripts\\run_minimal_eval.py --manifest tests\\fixtures\\local_mirror\\manifest.jsonl --predictions tests\\fixtures\\local_mirror\\predictions.jsonl --output-dir outputs\\stage1_m1_runner_smoke`
- `$env:PYTHONPATH='src'; python scripts\\prepare_br_gen_rehearsal.py --source-root data\\BR-Gen --output-root data\\mirrored\\br_gen\\subsets\\rehearsal`
- `$env:PYTHONPATH='src'; python scripts\\run_minimal_eval.py --manifest data\\mirrored\\br_gen\\subsets\\rehearsal\\manifest\\manifest.jsonl --predictions data\\mirrored\\br_gen\\subsets\\rehearsal\\predictions\\dummy_predictions.jsonl --output-dir outputs\\stage1_br_gen_rehearsal`

Interpretation:
- these checks prove the repo-tracked smoke substrate works end to end
- these checks prove compatibility with the user's current BR-Gen source drop layout on the local machine
- these checks do not prove anything about Community Forensics or the later localized-failure experiment result

---

## 5. Documentation Sync Status

- status:
  - [x] docs in sync
  - [ ] minor doc sync missing
  - [ ] significant doc sync missing

Synced areas:
- active M1 plan / contract / project context
- milestone status and issue index notes
- milestone closeout handoff

---

## 6. Semantic Risk Summary

- status:
  - [x] semantics look aligned
  - [ ] semantics uncertain
  - [ ] likely semantic mismatch

Reasoning:
- the implementation builds substrate only and does not overclaim experiment readiness
- grouped reporting only uses explicit metadata
- blocked slice dimensions remain explicit, preserving the localized-failure question rather than fabricating interpretability

---

## 7. Issue List by Severity

### P0

- none

### P1

- none

### P2

- the BR-Gen source drop used for rehearsal is positive-only and was paired with dummy predictions; it validates ingestion and artifact paths, not benchmark quality
- prediction input is intentionally minimal JSONL; if a later baseline emits a different format, add an adapter instead of widening M1 contracts implicitly

---

## 8. Recommended Next Action

- first action before M2 coding:
  - copy a real mirrored subset plus manifest metadata from the Linux server to the local workspace and rerun the minimal evaluation path
- then:
  - start `M2: Community Forensics Integration` from the existing loader / metric / runner substrate
