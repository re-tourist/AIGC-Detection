# M4 Local Evidence Module Results

## Status

Measured on the COCO-only restricted pilot.

This is diagnostic evidence for the M4 probe path, not a benchmark claim.

## Inputs Audited

- Baseline export: `outputs/m4/restricted_pilot/predictions_baseline.jsonl`
- Local-module export: `outputs/m4/restricted_pilot/predictions_local_module.jsonl`
- Baseline eval: `outputs/m4/restricted_pilot/eval_baseline/summary.json`
- Local-module eval: `outputs/m4/restricted_pilot/eval_local_module/summary.json`
- Baseline localized audit: `outputs/m4/restricted_pilot/eval_baseline/localized_failure_summary.json`
- Local-module localized audit: `outputs/m4/restricted_pilot/eval_local_module/localized_failure_summary.json`
- Baseline coverage audit: `outputs/m4/restricted_pilot/eval_baseline/localized_coverage_summary.json`
- Local-module coverage audit: `outputs/m4/restricted_pilot/eval_local_module/localized_coverage_summary.json`

## Credibility Check

- Both prediction files contain `275000` rows.
- `sample_id` order is identical between the two prediction files.
- Both runs use the same manifest and the same `restricted_pilot` eval scope.
- Coverage structure is identical:
  - `background` / `stuff`
  - `small` / `medium` / `large`
  - `subtlety` remains blocked in both runs
- The only visible prediction-side difference in metadata is the explicit
  `meta.local_module` field in the local-module output.

This makes the comparison fair enough to interpret as a probe-vs-baseline
readout.

## Core Results

### Overall

| Metric | Baseline | Local module | Delta |
| --- | ---: | ---: | ---: |
| Accuracy | 0.5384181818181818 | 0.5507272727272727 | +0.0123090909090909 |
| AUROC | 0.8754560336 | 0.8773497972 | +0.0018937636 |
| fake_recall | 0.4924 | 0.505992 | +0.013592 |

### Region slices

| Slice | Baseline fake_recall | Local fake_recall | Delta | Interpretation |
| --- | ---: | ---: | ---: | --- |
| background | 0.77644 | 0.79616 | +0.01972 | Still easy; probe does not destabilize it |
| stuff | 0.175 | 0.1856 | +0.0106 | Weak slice improved, but only modestly |

### Edit-area slices

| Slice | Baseline fake_recall | Local fake_recall | Delta | Interpretation |
| --- | ---: | ---: | ---: | --- |
| small | 0.0 | 0.0008988764044943821 | +0.0008988764044943821 | Still effectively blocked |
| medium | 0.01764705882352941 | 0.021148459383753503 | +0.003501400560224093 | Small positive movement, still very weak |
| large | 0.5822566752799311 | 0.6002460932693491 | +0.01798941798941798 | Already strong; now slightly higher |

## Slice-Aware Interpretation

Observed facts:
- The local probe changes model behavior.
- The overall numbers move up slightly.
- `background` remains an easy regime and stays strong.
- `stuff` improves modestly.
- `small` and `medium` improve only marginally and remain weak.

What this does not show:
- It does not show a decisive rescue of the localized blind spots.
- It does not show a large, isolated gain on `stuff` / `small` / `medium`.
- It does not show evidence that the hard top-k probe is already the final form
  of the method.

Mechanistic readout, limited to this evidence:
- The no-train probe is not inert.
- The residual add path can move decisions in the expected direction.
- The signal is weak enough that the current hard top-k formulation may still
  be too rigid to exploit local evidence fully.

## Trust Notes

- `support.low_support` is `false` for the relevant slices.
- The result is not explained away by sample scarcity.
- There is no manifest / eval mismatch in the audited outputs.
- The result remains restricted-pilot diagnostic evidence only.

## Conclusion

M4 produced a credible probe-vs-baseline readout.

The local module is not useless: it shifts the decision surface in the expected
direction and improves overall and slice-level fake_recall slightly.

However, the gain is small and not sharply concentrated on the weakest slices.
This supports closing M4 as a capability milestone, but not promoting the current
hard top-k probe directly into a training claim.

## Multi-Seed Audit Attempt

An M4 multi-seed stability audit was executed through
`scripts/run_m4_multi_seed_audit.py` in this workspace.

Observed outcome:
- run id: `m4_multi_seed_20260402T133603Z_unknown`
- requested seeds: `0,1,2,3,4`
- successful seeds: `0`
- failed seeds: `5`
- aggregate stats: unavailable because no seed reached a successful export/eval

Failure pattern:
- all seeds failed in the export stage
- the first missing asset reported by the manifest loader was
  `D:\home\workspace\AIGC\data\BRGen\BR-Gen\Forged\BrushNet\Background\COCO\000000000772_background.png`
- the local workspace contains the corresponding mask file, but not the forged
  image file

Interpretation:
- this is a data-availability blocker, not a model-behavior result
- no seed-stability conclusion can be drawn from this workspace run
- the single-run positive signal remains the only usable M4 diagnostic evidence

## Multi-Seed Stability Audit

The earlier workspace attempt above is historical and is superseded by a
successful Linux rerun.

Audited run:
- run id: `m4_multi_seed_20260403T024452Z_unknown`
- output root: `outputs/m4/multi_seed_audit/m4_multi_seed_20260403T024452Z_unknown`
- successful seeds: `5/5`
- failed seeds: `0/5`

Baseline control:
- reused `outputs/m4/restricted_pilot/eval_baseline`
- same manifest, same restricted-pilot eval scope, same slice support
- baseline sample count: `275000`

### Aggregate Readout

| Metric | Baseline | Local mean ± std | Delta mean | Improved seeds | Interpretation |
| --- | ---: | ---: | ---: | ---: | --- |
| overall_accuracy | 0.5384181818181818 | 0.5446567272727273 ± 0.0039427897158993315 | +0.006238545454545497 | 5/5 | Stable overall lift |
| overall_auroc | 0.8754560336 | 0.876344663584 ± 0.0011314559473426316 | +0.0008886299839999667 | 4/5 | Weak positive, one seed slightly below baseline |
| overall_fake_recall | 0.4924 | 0.49928800000000007 ± 0.004357513970144001 | +0.006888000000000061 | 5/5 | Stable overall lift |
| background_fake_recall | 0.77644 | 0.787992 ± 0.005454935380002233 | +0.011552000000000007 | 5/5 | Easy regime preserved and improved |
| stuff_fake_recall | 0.175 | 0.181448 ± 0.003378686135171478 | +0.006448000000000009 | 5/5 | Stable weak-slice gain |
| small_fake_recall | 0.0 | 0.0006292134831460674 ± 0.00024616744157535553 | +0.0006292134831460674 | 5/5 | Measurable but still effectively blocked |
| medium_fake_recall | 0.01764705882352941 | 0.02042016806722689 ± 0.0007304428465213064 | +0.002773109243697478 | 5/5 | Stable but still weak |
| large_fake_recall | 0.5822566752799311 | 0.5928091546696198 ± 0.005281708533255125 | +0.01055247938968873 | 5/5 | Positive sanity check |

### Stability Readout

- `stuff`, `small`, `medium`, and `background` all moved in the same direction
  across all five seeds.
- `small` is still practically blocked in absolute terms, even though the
  direction is consistent.
- `overall_auroc` is the only mixed metric; it is positive on average, but the
  effect size is smaller than the run-to-run variation.
- `subtlety` stayed `blocked` for all five seeds.

### Trust Notes

- `support.low_support` is `false` for the relevant slices.
- There is no evidence of sample scarcity or manifest mismatch.
- The effect is therefore not explained away by low support.

### Final Reading

- The no-train local probe is seed-stable on the blind-spot slices.
- The effect size is modest, but it is consistent and not a lucky seed.
- M4 can be closed as capability complete + seed-stability audited diagnostic
  evidence.
- M5 is now justified as a separate milestone only if the project wants to
  test whether trainable local scoring / soft aggregation can amplify this
  stable signal.
