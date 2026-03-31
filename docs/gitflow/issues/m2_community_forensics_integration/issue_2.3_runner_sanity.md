# Issue 2.3 - Sanity-check adapter with BR-Gen rehearsal manifest

## Background

Once the adapter exists, the next step is a minimal integration sanity check on the current BR-Gen rehearsal path.
Because the current BR-Gen source drop is still positive-only in the mirrored rehearsal manifest, the sanity check uses a temporary COCO-balanced smoke fixture under `data/tmp/cf_smoke/`.

## Suggested Branch

`codex/stage2-community-forensics-integration`

## Goal

Generate repo-compatible predictions from the adapter and replay them through the existing M1 runner.
Keep the smoke fixture temporary and delete it after validation.

## Tasks

- Prepare the temporary COCO-balanced smoke fixture from the BR-Gen source drop.
- Export Community Forensics scores from the smoke manifest into repo-compatible prediction JSONL.
- Feed the resulting prediction JSONL into the existing runner.
- Verify that the report artifacts are produced from the same contract as M1.
- Emit a temporary `data/tmp/cf_smoke/feedback.json` so the smoke run has a concrete local result file.

## Resource Boundary

- Do not extend into full Community Forensics reproduction.
- Do not add new evaluation protocols.
- Do not interpret partial rehearsal evidence as the final research claim.

## Non-Goals

- No M3 localized validation.
- No new slice inference.

## Deliverable

- BR-Gen rehearsal sanity evidence and temporary smoke artifacts.

## Acceptance

- Adapter-emitted predictions are consumable by the current runner.
- Alignment and score conversion are observable in the output provenance.
- The temporary smoke fixture can be rebuilt from `scripts/prepare_br_gen_coco_smoke.py` and replayed through `scripts/run_minimal_eval.py`.
- The one-shot smoke wrapper can rebuild the fixture, export predictions, run the runner, and write `feedback.json`.
- Any partial rehearsal result is labeled provisional.
