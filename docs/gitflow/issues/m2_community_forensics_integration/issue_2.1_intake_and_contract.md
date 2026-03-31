# Issue 2.1 - Intake Community Forensics source and freeze adapter contract

## Background

M2 should start from the upstream Community Forensics source shape and the current repo contract, not from assumptions about the output format.

## Current Workspace State

- The upstream Community Forensics source is available locally under `external/Community-Forensics`.
- The external repo is aligned with `origin/main`.
- The default HF model repo `OwensLab/commfor-model-384` has been downloaded to `external/Community-Forensics/weights/commfor-model-384`.
- The 224-input model remains available upstream, but M2 does not require it.

## Suggested Branch

`codex/stage2-community-forensics-integration`

## Goal

Confirm the upstream Community Forensics entry points and freeze the adapter contract needed to feed the existing prediction JSONL runner.

## Tasks

- Read the upstream Community Forensics README and evaluation entry points.
- Record the evaluation protocol, sample alignment rule, score contract, and localized-failure definition in the milestone doc.
- Confirm that the work stays adapter-first and does not expand into reproduction or method work.

## Resource Boundary

- Do not modify the frozen M1 contract.
- Do not add generator-diverse retraining.
- Do not infer new slice metadata.

## Non-Goals

- No Community Forensics reproduction.
- No runner rewrite.
- No M3 localized validation.

## Deliverable

- Updated M2 milestone doc and issue index.
- Local Community Forensics source and model snapshot are present for adapter integration work.

## Acceptance

- The M2 execution contract is explicit.
- The adapter scope is fixed before code changes.
- The plan states what counts as provisional evidence versus final claim.
