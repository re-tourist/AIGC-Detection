# M7: Matched-Control Audit and Fairness Repair

GitHub milestone:
- pending GitHub closeout sync; repo docs remain the source of truth

## Status

- locally complete with documented limitations
- Phase 0 diagnostics completed
- Phase 1 docs matrix completed
- repaired trainable-stage protocol validated on `current_local` and `matched_global_only_control`
- balanced sampler validated as the stop-loss repair baseline
- weighted BCE and combined sampler+loss are documented follow-up / ceiling-search arms
- ready for GitHub milestone / issue / PR sync and closeout

## Goal

Repair the local-vs-control comparison so that the verdict about local-module
value is based on a conceptually matched control and a repaired trainable-stage
protocol, not the legacy full-forward control path or the old calibration
pathology.

## In Scope

- audit `current_local` vs `current_control_legacy` forward-path differences
- audit freeze semantics, `requires_grad`, and `torch.no_grad()` behavior
- audit head path and trainable-parameter differences
- audit protocol parity: split, optimizer, scheduler, batch, preprocessing, eval
- audit memory / compute with isolated-process probes
- implement `matched_global_only_control`
- repair the trainable stage with class-imbalance-aware protocol changes
- replay seeds `42` and `43`, with `44` retained as a canary-only reference
- produce fairness audit, replay summary, closeout, and GitHub sync artifacts

## Out of Scope

- new local-module architectures
- gated fusion
- new loss / objective work beyond the documented repair protocol
- consistency / robustness branches
- benchmark expansion
- segmentation-heavy localization work

## Exit Criteria

- current mismatch dimensions are explicitly enumerated
- repaired matched global-only control is implemented and runnable
- the repaired trainable-stage protocol restores real-side calibration enough to
  make attribution fair again
- M7 runner emits fairness audit artifacts plus repaired replay artifacts
- required seeds `42/43` have replay results, with `44` explicitly tracked as a
  canary or deferred check
- closeout states whether the old control was mismatched and whether the
  repaired protocol changes the verdict

## Issue Set

- Issue 7.1 - fairness audit matrix
- Issue 7.2 - repaired matched-control implementation
- Issue 7.3 - memory audit and replay
- Issue 7.4 - review, closeout, and gitflow sync

## Deliverable Pointers

- runner:
  - `scripts/run_m7_matched_control_audit.py`
- comparison helper:
  - `src/aigc_detection/eval/m7_matched_control.py`
- repaired-protocol runner:
  - `scripts/run_m7_unified_training_arm.py`
- run-order:
  - `docs/run_order/m7_matched_control_audit_and_repair.md`
  - `docs/run_order/m7_real_recall_protocol_repair.md`
- review:
  - `docs/review/review_m7_matched_control_audit_and_fairness_repair.md`
- closeout:
  - `docs/handoff/m7_matched_control_audit_and_fairness_repair_closeout.md`
