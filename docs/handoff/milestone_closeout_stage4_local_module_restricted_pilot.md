# M4 Local Module Restricted Pilot Closeout

## Milestone Info

- Milestone: `M4 Local Evidence Module on the COCO Restricted Pilot`
- Status: `closed with limitations`
- Evaluation scope: `restricted_pilot`
- Dataset scope: `COCO-only`

## 1. What M4 Completed

- Added a minimal local evidence probe on top of the verified CF-ViT path.
- Kept the baseline forward path intact when the probe is disabled.
- Ran a fair baseline-vs-local-module restricted-pilot comparison.
- Verified that the probe changes behavior without breaking the easy regime.

## 2. What M4 Did Not Complete

- It did not prove the local probe is the final method.
- It did not train a new model.
- It did not change the frozen M1/M2 eval substrate.
- It did not produce a formal benchmark claim.

## 3. What the Results Say

The run is credible and slice-aligned:
- same manifest
- same sample order
- same eval scope
- same support regime
- only local probe activation differs

Measured effect:
- overall metrics improved slightly
- `background` remained easy and improved
- `stuff` improved modestly
- `small` and `medium` improved only marginally and remain weak

Interpretation:
- the local probe is not inert
- the current hard top-k formulation is too weak to claim a decisive fix
- the result is useful diagnostic evidence, not method validation

## 4. Why This Is Still Not a Benchmark Claim

The evidence comes from a restricted-pilot engineering line.
That line is explicitly diagnostic.

It does not have:
- formal benchmark negatives
- formal M3 closure
- a claim of cross-dataset generality
- a claim that the local module is the final architecture

## 5. Decision

M4 is closed with limitations.

The project should not jump straight into M5 as if the current probe already
proved the method.
The better reading is:
- the local line is viable
- it produced a positive but weak signal
- more diagnostics would be required before a training-stage commitment

## 6. Next Stage Recommendation

Do not start M5 immediately.
If M5 is ever opened, it should be because the project wants to test whether
trainable local scoring and soft aggregation can amplify the weak positive
signal observed here.

That decision should be made as a new milestone, not as an automatic extension
of this one.

## 7. Multi-Seed Audit Addendum

After the original single-run closeout, an M4 multi-seed stability audit was
attempted in this workspace.

Actual outcome:
- run id: `m4_multi_seed_20260402T133603Z_unknown`
- requested seeds: `0,1,2,3,4`
- successful seeds: `0`
- failed seeds: `5`
- the audit never reached model inference on any seed

Root cause:
- the local data mirror is missing a forged BR-Gen image referenced by the
  manifest
- the first reported missing file was
  `D:\home\workspace\AIGC\data\BRGen\BR-Gen\Forged\BrushNet\Background\COCO\000000000772_background.png`
- the corresponding mask file is present, which confirms this is a forged-image
  availability gap rather than a general directory mismatch

Implication:
- the multi-seed stability question remains unresolved in this workspace
- this does not overturn the single-run closeout
- it does mean we should not overstate seed-stability until the full forged-image
  mirror is available and the audit is rerun

## 8. Multi-Seed Stability Closeout

The later Linux rerun completed successfully and supersedes the earlier blocked
workspace attempt for the purpose of the final M4 judgment.

Final run facts:
- run id: `m4_multi_seed_20260403T024452Z_unknown`
- successful seeds: `5/5`
- failed seeds: `0/5`

Final reading:
- the no-train local probe is seed-stable on the blind-spot slices
- `stuff`, `small`, and `medium` all improve in the same direction across all
  five seeds
- `background` stays easy and improves
- `overall_auroc` is weakly positive, but not the main signal

Closeout statement:
- `M4 = capability complete + seed-stability audited diagnostic evidence`
- M4 remains a restricted-pilot diagnostic milestone, not a benchmark claim
- M5 is now justified only as a new milestone if the project wants to test
  trainable amplification of the same local-evidence signal
