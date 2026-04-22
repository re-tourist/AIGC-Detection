# Review: M7 Matched-Control Audit and Fairness Repair

## Status

- review complete with documented limitations
- protocol repair evidence has been collected
- GitHub closeout sync is the remaining repo-admin step

## Review Questions

1. Does `current_control_legacy` differ from `current_local` in more than the local branch?
2. Does `matched_global_only_control` truly align with the local path semantics?
3. Are the required fairness dimensions audited in the fixed order?
4. Are memory conclusions based on isolated-process evidence rather than `nvidia-smi` impressions?
5. After repair, can the local-module verdict be judged fairly?

## Required Readouts

Priority order:

1. `stuff`
2. `small`
3. `medium`
4. `background`
5. overall

Required statistics:

- current local vs legacy control deltas
- current local vs matched control deltas
- matched control vs legacy control deltas
- required seed status
- canary seed status

Observed conclusion:

- the same-split M4 reference is healthy
- the old trainable-stage protocol collapses real-side recall for both
  `current_local` and `matched_global_only_control`
- `balanced_sampler` restores a fair operating point without destroying the
  blind-spot recovery signal
- `weighted_bce` and `balanced_sampler_weighted_bce` are ceiling-search arms
  rather than the core fairness proof

## Verdict Matrix

- old control was mismatched; repaired control restores a fair comparison
- repaired control still shows no local-module edge
- repaired control rescues the local-module case
- repaired control is implemented, but replay evidence is still incomplete

## Review Outcome Placeholder

- forward-path audit: complete
- freeze/no-grad audit: complete
- replay: complete with documented limitations
- final verdict: local-vs-control attribution is now fair enough to close M7
