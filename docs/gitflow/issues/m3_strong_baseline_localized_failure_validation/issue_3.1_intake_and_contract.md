# Issue 3.1 — Freeze M3 contract and audit official BR-Gen raw layout

GitHub issue:
- pending creation

## Background

M3 starts only after M2 integration is complete. The first task is to freeze the
formal BR-Gen source-root contract and the raw-layout assumptions needed for
localized validation.

Current repo truth:

- M2 integration is complete and closed.
- The official BR-Gen root for M3 is available on Linux:
  - `/media/ruanzhengsen/02EE2033DCBE79181/xyj/BRGen/BR-Gen`
- The official source provides raw real, fake, and mask directories only.
- This work is already implemented locally and should be backfilled to GitHub as
  completed scope.

## Suggested Branch

`codex/stage3-strong-baseline-localized-validation`

## Goal

Make the official BR-Gen root, raw-layout audit rules, and M3 reporting boundary
explicit before formal manifest generation and Linux execution.

## Tasks

- freeze the M3 execution contract without changing the frozen M1 contract
- record the accepted raw-layout rules for fake, mask, and real discovery
- define hard-stop behavior for ambiguous roots, broken pairings, and unsupported
  layout patterns
- sync milestone, issue, and run-order docs to the same contract

## Resource Boundary

- do not change M1 field or metric meaning
- do not infer new metadata beyond the explicit raw layout
- do not start formal benchmark claims from smoke artifacts

## Non-Goals

- no Community Forensics reproduction
- no retraining
- no Linux full run yet

## Deliverable

- frozen M3 contract doc
- updated M3 milestone doc
- explicit issue split and Linux runbook entry point

## Acceptance

- the official BR-Gen root requirement is explicit
- raw-layout ambiguity rules are explicit
- M3 stop conditions are written down before code relies on them
