# M3 Restricted Pilot Success Criteria

## Purpose

This document defines what counts as success for the `COCO-only restricted_pilot`
under `M3 Strong Baseline Localized Failure Validation`.

It exists to prevent a category error:

- running the pilot is not the same as completing formal M3
- high overall metrics are not the same as obtaining useful localized evidence

## Scope Boundary

The active pilot remains strictly bounded as:

- evaluation scope: `restricted_pilot`
- dataset scope: `COCO-only`

This document does not redefine:

- formal M3
- the frozen M1 metric contract
- the formal benchmark boundary

## What Pilot Success Does Not Mean

Pilot success does not mean:

- formal M3 has closed
- strong baseline failure has been proven
- a paper-ready benchmark result has been produced
- overall AUROC or Accuracy is high

## What Pilot Success Should Mean

Restricted pilot success is defined by diagnostic quality, not by optics.

The pilot is successful when it improves the team’s ability to answer these questions:

1. Which localized slices are actually covered by the current restricted pilot
2. Which slices remain easy for the strong baseline
3. Which slices begin to show credible failure evidence
4. Which dimensions remain blocked by metadata gaps or insufficient support

## Required Success Conditions

The restricted pilot should be treated as successful only if all of the following hold.

### 1. Expanded evidence coverage

Compared with the narrow capped pilot, the current run should materially widen at least one of:

- generator coverage
- region coverage
- edit-area coverage
- degradation coverage
- exploratory slice coverage

If coverage remains effectively single-generator, single-region, and single-area-bin,
the pilot is still too narrow.

### 2. Slice visibility

The localized sidecar must expose, at minimum:

- by generator
- by region
- by edit-area bin
- by degradation
- by source, when meaningful

If a dimension is unavailable, it must be explicitly labeled `blocked` or `missing metadata`.

### 3. Support visibility

Each reported slice must include:

- sample count
- positive count
- negative count
- low-support status

If low-support slices are not clearly flagged, the pilot is not diagnostically trustworthy.

### 4. Failure evidence map quality

The pilot must produce a structured failure evidence map that distinguishes:

- `easy_regime`
- `failure_evidence`
- `inconclusive`
- `inconclusive_low_support`
- `blocked`

The purpose is not to prove failure at all costs.
The purpose is to make the current diagnostic landscape explicit.

### 5. Honest blocked-state reporting

If a key dimension is still blocked, for example `subtlety`, the pilot is only successful if
that blocked state is made explicit rather than hidden.

## What Counts As A Successful Outcome Even If The Baseline Stays Strong

The pilot can still be considered successful when the overall baseline remains strong, provided that:

- coverage becomes materially wider
- the slice map becomes clearer
- easy slices and weak slices can be separated
- blocked dimensions are clearly surfaced

In other words:

> a pilot that clarifies the evidence landscape is successful, even if it does not yet show dramatic failure

## What Counts As Pilot Failure

The restricted pilot should be treated as unsuccessful if one or more of the following remain true:

- expanded coverage is still effectively narrow
- only one generator or one region remains visible
- edit-area support is still dominated by a single bin
- low-support slices dominate the failure map
- key localized dimensions remain invisible because of missing metadata
- the output still focuses mostly on overall metrics instead of slice evidence

## Interpretation Rules

### High overall metrics

High overall metrics mean only that the current restricted pilot may still be easy.
They do not imply that the pilot succeeded diagnostically.

### Low-support weak slices

A weak slice with very low support is not strong evidence.
It should remain labeled `inconclusive_low_support`.

### Strong slices

If expanded coverage still produces mostly strong slices, the correct conclusion is:

- strong baseline remains strong under the current restricted pilot

This is an acceptable pilot result as long as the evidence map is honest and complete.

## Deliverables Expected From A Successful Pilot

At minimum, a successful restricted pilot should generate:

- `summary.json`
- `localized_failure_summary.json`
- `localized_failure_report.md`
- `localized_coverage_summary.json`
- `coverage_audit.md`
- `failure_evidence_map.md`

## Relationship To Formal M3

Formal M3 remains blocked unless the formal boundary is satisfied.

This restricted pilot is allowed to support:

- pipeline validation
- failure discovery
- diagnostic evidence
- later method design

It is not allowed to substitute for:

- formal benchmark evidence
- milestone closeout
- final paper claim

## Bottom Line

The correct success criterion is:

> The restricted pilot succeeds when it produces wider, more trustworthy, and more interpretable localized evidence.

It does not succeed merely because it runs.
It does not succeed merely because overall metrics are high.
