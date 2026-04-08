# M4 Local Module Restricted Pilot Review

## Inputs

- `outputs/m4/restricted_pilot/predictions_baseline.jsonl`
- `outputs/m4/restricted_pilot/predictions_local_module.jsonl`
- `outputs/m4/restricted_pilot/eval_baseline/summary.json`
- `outputs/m4/restricted_pilot/eval_local_module/summary.json`
- `outputs/m4/restricted_pilot/eval_baseline/localized_failure_summary.json`
- `outputs/m4/restricted_pilot/eval_local_module/localized_failure_summary.json`
- `outputs/m4/restricted_pilot/eval_baseline/localized_coverage_summary.json`
- `outputs/m4/restricted_pilot/eval_local_module/localized_coverage_summary.json`

## 1. 结果可信度审计

This comparison is credible.

Reasons:
- Both prediction files contain `275000` rows.
- `sample_id` ordering is identical across baseline and local-module outputs.
- Both eval runs use the same manifest and the same `restricted_pilot` scope.
- Coverage is identical on the dimensions that matter for this milestone:
  - `region_type`
  - `edit_area_ratio`
  - `degradation`
  - `generator_id`
- `subtlety` remains blocked in both runs, which matches the frozen M4 contract.
- The local-module prediction metadata only adds `meta.local_module`; it does
  not change manifest coverage or sample selection.

Result status:
- trusted enough for milestone judgment
- not a benchmark claim
- not sufficient for a formal method conclusion

## 2. baseline vs local-module 核心对比

Overall numbers move up slightly:
- Accuracy: `0.5384181818181818 -> 0.5507272727272727`
- AUROC: `0.8754560336 -> 0.8773497972`
- fake_recall: `0.4924 -> 0.505992`

Slice-level readout:
- `background` improves and remains easy.
- `stuff` improves modestly.
- `small` improves from essentially zero to still essentially zero.
- `medium` improves slightly but remains very weak.

This is a real behavioral shift, but a small one.

## 3. Slice Interpretation

### `background`

This remains the easy regime.
The probe does not break it, and it improves slightly.
That is a positive stability signal.

### `stuff`

This is still the clearest weak slice.
The local probe nudges fake_recall upward by about `+0.0106`, but the slice
remains far below the clean reference.
This is a positive signal, but not strong enough to call the slice fixed.

### `small`

This remains effectively blocked.
The change from `0.0` to `0.0008988764044943821` is measurable but tiny.
This does not support a claim that the current hard probe solves small-area
blind spots.

### `medium`

This is the most useful positive movement after `stuff`, but it is still weak.
The gain is only `+0.0035` fake_recall.
That suggests local evidence is present, but the current hard top-k aggregation
is not extracting it strongly.

## 4. Pattern Classification

The result is best classified as:

- **B. 有变化但不稳定**

Why not A:
- The probe does change the decision surface.
- The change is visible in overall and slice-level numbers.

Why not C:
- The improvement is modest.
- The weak slices are still weak.
- The signal is not concentrated enough to justify a stronger claim.

Why not D:
- The baseline is not destroyed.
- The easy regime remains easy.
- There is no sign that the insertion point is structurally broken.

## 5. M4 Close Decision

My judgment:
- **M4 can close**
- but only as a capability / probe milestone
- and only with documented limitations

Reason:
- The probe behaves as intended.
- The comparison is credible.
- The result is useful diagnostically.
- It is enough to stop M4 from being open-ended.

## 6. M5 Decision

My judgment:
- **do not enter M5 immediately**

Reason:
- The signal is positive, but weak.
- The probe did not sharply recover the known blind spots.
- The evidence is not strong enough to justify a training-stage commitment yet.

What would have supported M5 more strongly:
- a clearer lift on `stuff`
- a clearer lift on `small` / `medium`
- or a stronger sign that hard top-k is the bottleneck, not the local line
  itself

## 7. Verdict

**Verdict 2: M4 可以 close，但不建议立刻进 M5，先补更多诊断。**

Grounding:
- close, because the probe works and the evidence is credible
- not M5 yet, because the effect size is too small and too broad to justify the
  next training step

## 8. Remaining Risks

- The gain may not survive a different local-module parameter choice.
- The hard top-k formulation may still be too rigid.
- The current probe is only one narrow insertion point, so it may understate
  what a trainable local scoring path could recover.

## 9. Recommendation

Close M4 with limitations documented.
Do not promote the current result to a formal benchmark claim.
If the project later revisits M5, use this run as diagnostic motivation rather
than as proof of method success.

## 10. Multi-Seed Stability Audit

An M4 multi-seed audit was launched in this workspace through
`scripts/run_m4_multi_seed_audit.py`.

Observed result:
- run id: `m4_multi_seed_20260402T133603Z_unknown`
- requested seeds: `0,1,2,3,4`
- successful seeds: `0`
- failed seeds: `5`
- all five seeds failed before inference completed

Failure cause:
- the manifest loader hit a missing forged image file in the local data mirror
- the first reported missing asset was
  `D:\home\workspace\AIGC\data\BRGen\BR-Gen\Forged\BrushNet\Background\COCO\000000000772_background.png`
- the corresponding mask file exists locally, but the forged image file does not

Interpretation:
- this blocks any seed-stability conclusion in the current workspace
- there is no basis to call the single-run gain a lucky seed or a stable effect
  from the multi-seed audit, because the multi-seed audit never reached model
  inference
- the only usable M4 behavioral evidence remains the single-run restricted-pilot
  comparison

## 11. Multi-Seed Stability Audit Update

The blocked workspace attempt above is historical. The final Linux rerun
completed successfully and is the basis for the current stability judgment.

Run facts:
- run id: `m4_multi_seed_20260403T024452Z_unknown`
- seeds: `0,1,2,3,4`
- successful seeds: `5/5`
- failed seeds: `0/5`

Slice-level summary:
- `background`: stable improvement, easy regime preserved
- `stuff`: stable improvement across all seeds
- `small`: measurable but still effectively blocked
- `medium`: stable but weak improvement
- `large`: positive sanity check
- `subtlety`: blocked in all five seeds

Aggregate interpretation:
- `stuff`, `small`, and `medium` all improve in the same direction across all
  five seeds
- the blind-spot signal is therefore structural, not a lucky seed
- `overall_auroc` is only weakly positive and is not the main evidence for this
  milestone

Updated pattern classification:
- **A. Stable positive**

Updated verdict:
- M4 can close as capability complete + seed-stability audited diagnostic
  evidence
- the current no-train probe is worth keeping as diagnostic evidence
- M5 is now justified as a separate milestone if the project wants to test
  trainable amplification of the same local-evidence signal

Updated reading:
- current verdict on M4 itself does not change
- current seed-stability audit status is blocked by data completeness
- if the full forged-image mirror becomes available later, the multi-seed audit
  should be rerun before revisiting any stronger stability claim
