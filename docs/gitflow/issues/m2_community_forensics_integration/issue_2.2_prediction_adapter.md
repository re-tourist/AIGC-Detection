# Issue 2.2 - Implement prediction adapter and sample alignment

## Background

The current runner expects prediction JSONL keyed by `sample_id`. Community Forensics must be adapted into that contract without heuristic matching.

## Suggested Branch

`codex/stage2-community-forensics-integration`

## Goal

Implement the smallest adapter that converts Community Forensics-style prediction outputs into the repo prediction JSONL format.

## Tasks

- Support deterministic `sample_id` alignment from normalized relative paths.
- Support explicit mapping-table alignment when upstream IDs differ from manifest IDs.
- Allow exact passthrough when the upstream record already uses the repo `sample_id` verbatim.
- Enforce a frozen score contract where higher score means more likely fake.
- Emit repo-compatible prediction JSONL with optional provenance in `meta`.

## Resource Boundary

- No changes to the M1 loader, metrics, or runner.
- No runtime heuristic matching.
- No new slice metadata derivation.

## Non-Goals

- No model training.
- No segmentation metrics.
- No generator-diverse retraining.

## Deliverable

- Adapter module and CLI script.

## Acceptance

- Adapter output passes the existing prediction JSONL loader.
- Alignment is deterministic and explicit.
- Score direction is frozen and documented.
