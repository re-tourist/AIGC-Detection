# Issue 3.3 — Add localized-failure sidecar reporting on top of the current runner

GitHub issue:
- pending creation

## Background

The current minimal runner already writes the frozen M1 artifacts. M3 needs
additional localized-failure evidence without changing that base contract.

Current repo truth:

- the M3 sidecar is implemented
- the sidecar now covers generator, region, area, degradation, coverage audit,
  and failure evidence map outputs
- this scope is already completed locally and should be backfilled to GitHub as
  a completed issue

## Suggested Branch

`codex/stage3-strong-baseline-localized-validation`

## Goal

Layer an M3-only localized-failure report on top of the existing runner outputs.

## Tasks

- reuse the existing minimal runner as the first evaluation step
- compute localized clean metrics and degradation summaries from the same
  manifest and prediction inputs
- report `region_type` slices and `edit_area_ratio` bins using explicit masks
  only
- keep `subtlety` blocked when explicit metadata is absent
- write M3 summary JSON, flat CSV, and Markdown report artifacts

## Resource Boundary

- no change to minimal runner artifact semantics
- no additional core metrics beyond `AUROC`, `Accuracy`, and `fake_recall`
- no heuristic slice metadata

## Non-Goals

- no benchmark table automation for future stages
- no calibration or AUPR contract expansion

## Deliverable

- M3 evaluation entry point
- localized-failure sidecar artifacts
- focused tests for degradation, region, area-bin, and blocked subtlety behavior

## Acceptance

- the minimal runner artifacts remain intact
- M3 sidecar artifacts are traceable to the same manifest and predictions
- slice summaries fail only when the underlying explicit data is missing
