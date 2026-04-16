# M7 Closeout: Matched-Control Audit and Fairness Repair

## Milestone Info

- Milestone ID: M7
- Milestone name: Matched-Control Audit and Fairness Repair
- Status:
  - [x] complete with documented limitations
  - [ ] partially complete
  - [ ] blocked
  - [ ] handed off with risks
- Date:
- Related branch:
- Related milestone doc:
  - `docs/gitflow/milestones/m7_matched_control_audit_and_fairness_repair.md`
- Related issue set:
  - `docs/gitflow/issues/m7_matched_control_audit_and_fairness_repair/README.md`

## 1. Executive Summary

- Why M7 was needed:
  - the old trainable-stage protocol pushed both `current_local` and
    `matched_global_only_control` into a fake-biased operating point where
    `paper_real_recall_at_0_5` collapsed
  - the previous control path was not conceptually matched to the local path
    and could not support fair attribution
- What was actually completed:
  - the matched-control audit was finished and the repaired global-only control
    path was implemented
  - the real-recall protocol repair was validated on `balanced_sampler`
  - `weighted_bce` and `balanced_sampler_weighted_bce` were evaluated as
    higher-budget follow-up / ceiling-search arms
  - the run-order, contracts, briefing, and closeout docs now reflect the
    repaired-protocol contract
- Whether the repaired protocol is fair enough for final attribution:
  - yes, with documented limitations
  - the repaired protocol restores a credible operating point for comparing
    local and matched-control behavior
  - local-vs-control differences are now interpretable as a tradeoff frontier,
    not as a protocol artifact
- Biggest remaining gap:
  - the combined ceiling-search arm is still a follow-up hypothesis rather than
    a necessary prerequisite for the fairness verdict
  - if further paper-level tightening is needed, it should be treated as a
    follow-on experiment rather than a blocker for M7 closeout

## 2. What Was Completed

- [x] Fairness audit matrix
- [x] Repaired matched control
- [x] Memory audit
- [x] Required replay seeds `42/43`
- [x] Canary seed `44` tracked or explicitly deferred
- [x] Final decision note

## 3. What Was Not Completed

- [ ] Combined `balanced_sampler_weighted_bce` ceiling search as a required
  evidence gate
- [ ] GitHub milestone / issue / PR sync for the closeout state
- [ ] Optional extra-seed expansion beyond the repaired `42/43` evidence base

## 4. Key Files and Changes

### Code
- `scripts/run_m7_matched_control_audit.py`
- `src/aigc_detection/eval/m7_matched_control.py`
- `models/m5_wrapper.py`
- `scripts/run_m7_unified_training_arm.py`
- `scripts/run_m7_real_recall_protocol_repair_phase0.py`
- `scripts/run_m7_real_recall_protocol_repair_phase1_suite.py`
- `src/aigc_detection/eval/protocol_repair.py`

### Docs
- `docs/run_order/m7_matched_control_audit_and_repair.md`
- `docs/review/review_m7_matched_control_audit_and_fairness_repair.md`
- `docs/run_order/m7_real_recall_protocol_repair.md`
- `docs/run_order/m7_real_recall_protocol_repair_phase1_suite.md`
- `docs/handoff/m7_local_module_chatgpt_briefing.md`
- `docs/contracts/m7_real_recall_protocol_repair.md`
- `docs/contracts/m7_unified_training_protocol.md`

## 5. Validation Summary

### Validation Run
- import smoke:
  - `python -m py_compile scripts/run_m7_unified_training_arm.py scripts/run_m7_matched_control_audit.py scripts/run_m7_real_recall_protocol_repair_phase0.py scripts/run_m7_real_recall_protocol_repair_phase1_suite.py src/aigc_detection/eval/protocol_repair.py tests/test_m5_snapshot_epochs.py tests/test_protocol_repair.py`
- CLI smoke:
  - `python scripts/run_m7_real_recall_protocol_repair_phase0.py --help`
  - `python scripts/run_m7_real_recall_protocol_repair_phase1_suite.py --help`
  - `python scripts/run_m7_unified_training_arm.py --help`
  - `python scripts/run_m7_matched_control_audit.py --help`
- targeted tests:
  - `python -m unittest discover -s tests -p "test_protocol_repair.py"`
  - `python -m unittest discover -s tests -p "test_m5_snapshot_epochs.py"`
  - `python -m unittest discover -s tests -p "test_m7_compare.py"`
  - `python -m unittest discover -s tests -p "test_m7_unified_training_arm.py"`
  - `python -m unittest discover -s tests -p "test_m7_validation_runner.py"`

### What These Checks Actually Prove
- prove:
  - the repaired protocol is wired consistently through the runner,
    comparison helper, and summary outputs
  - the docs and contracts agree on `best_blindspot`, `best_overall`, and the
    repair protocol contract
  - the stop-loss repair is not a hidden training-logic bug
- do not prove:
  - that every possible high-budget ceiling-search variant has been exhausted
  - that an external reviewer will agree with every paper-facing phrasing choice
  - that a new unseen dataset will behave identically under the repaired protocol

## 6. Risks and Known Limitations

### P0 / blocking
- risk:
  - GitHub milestone / issue / PR sync still needs to be published or confirmed
    on the remote repository before the closeout is fully reflected there

### P1 / serious but not blocking
- risk:
  - `weighted_bce` and combined `balanced_sampler_weighted_bce` are valid
    follow-up arms, but they are not required to justify the fairness verdict
  - if future paper wording needs a stricter upper bound, a follow-on sweep may
    still be useful
  - the repo retains earlier experimental branches and artifacts, so reviewers
    should follow the run-order docs rather than assuming a single linear path

### P2 / should improve later
- risk:
  - the closeout could be tightened further if a final published PR records the
    GitHub milestone closure with linked issue numbers and URLs
  - if more seeds are ever needed, they should be added as a follow-on milestone
    rather than reopening the completed repair work

## 7. Contract / Scope Notes

- [x] fully within frozen scope
- [ ] small deviation documented
- [ ] contract issue discovered
- [ ] scope drift occurred

## 8. Recommended Next Entry Point

### Recommended first task
- next step:
  - publish the GitHub milestone / issue / PR sync, then close the milestone on
    GitHub using the completed evidence chain
  - if the remote sync is blocked, the repo-local docs now contain the complete
    closeout context needed to finish it later

### Recommended first files to read
- `scripts/run_m7_matched_control_audit.py`
- `src/aigc_detection/eval/m7_matched_control.py`
- `docs/review/review_m7_matched_control_audit_and_fairness_repair.md`
- `docs/handoff/m7_local_module_chatgpt_briefing.md`
- `docs/run_order/m7_real_recall_protocol_repair.md`
- `docs/gitflow/milestones/m7_matched_control_audit_and_fairness_repair.md`

## 9. Handoff Guidance

- Do not treat legacy control as a fair control after M7.
- Keep required seeds and canary seed status separate.
- Treat `balanced_sampler` as the validated repair baseline and
  `weighted_bce` / combined strategies as higher-budget follow-up arms.
- Do not overclaim replay evidence if a future reviewer asks about
  `balanced_sampler_weighted_bce`; the current closeout does not require it.

## 10. Final Verdict

- [ ] milestone can be cleanly closed
- [x] milestone can be closed with documented limitations
- [ ] milestone should remain open pending one last validation
- [ ] milestone should not be closed because the result is not yet reliable

- Current conclusion:
  - M7 has answered its core fairness question: the original trainable-stage
    protocol caused real-side collapse for both local and control, and the
    repaired protocol restores enough calibration to make local-vs-control
    attribution fair again.
  - The remaining difference is now an interpretable tradeoff frontier:
    `current_local` retains stronger blind-spot recovery, while
    `matched_global_only_control` is slightly more stable on real-side
    calibration.
  - The milestone should be closed on GitHub after the docs / PR sync is
    published.
