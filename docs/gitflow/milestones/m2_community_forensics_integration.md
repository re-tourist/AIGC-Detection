# M2: Community Forensics Integration

GitHub milestone:
- `https://github.com/re-tourist/AIGC-Detection/milestone/3`

## Goal

Integrate Community Forensics as a baseline candidate under the current repository contract.
The objective is integration, not paper reproduction.

## In Scope

- Read the upstream Community Forensics repository and its key evaluation entry points.
- Adapt Community Forensics outputs to the existing prediction JSONL contract.
- Prepare a temporary BR-Gen COCO-balanced smoke fixture and export scores from it into the repo prediction JSONL contract.
- Run a minimal sanity check through the current M1 runner.
- Record which upstream assumptions are preserved and which eval details are not reproduced.

## Out of Scope

- Full reproduction of the Community Forensics paper protocol.
- Generator-diverse retraining.
- New slice metadata inference.
- Segmentation metrics.
- M3 localized-failure validation.
- Any change to the frozen M1 contract.

## Execution Contract

### Evaluation protocol

- Dataset: BR-Gen mirrored rehearsal subset.
- Task: image-level real vs fake classification.
- Primary comparison: `full_image_fake` vs `localized_edit`.
- Primary metrics: `AUROC`, `Accuracy`, `fake_recall`.
- M2 does not add segmentation metrics.
- M2 does not infer new slice metadata heuristically.

### Sample alignment

- `prediction.sample_id` must align to `manifest.sample_id`.
- If the upstream record already carries the exact repo `sample_id`, the adapter may pass it through unchanged.
- Allowed strategies:
  - deterministic derivation from normalized relative path
  - explicit mapping table supplied by the adapter
- Runtime heuristic matching is forbidden.

### Score contract

- Adapter output must preserve the existing M1 prediction JSONL schema.
- `score` must always mean: higher score = more likely fake.
- Any logit, probability, sign flip, or normalization rule must be frozen explicitly before implementation and then applied exactly once.

### Failure definition

- Localized failure is indicated when localized-edit performance is worse than full-image-fake performance, for example:
  - `fake_recall(localized_edit) < fake_recall(full_image_fake)`
  - or `AUROC(localized_edit) < AUROC(full_image_fake)`
- If the rehearsal stage only covers a partial source-drop subset, the result is provisional evidence only.
- M2 must not claim a final localized-failure result.

## Exit Criteria

- Community Forensics outputs can be adapted into the repo prediction JSONL contract.
- The adapted predictions can be consumed by the current M1 runner.
- A temporary COCO-balanced smoke fixture can be prepared, scored, and replayed through the current runner.
- The M2 docs explicitly state the protocol, alignment, score, and failure rules.

## Issue Set

- Issue 2.1 - Intake Community Forensics source and freeze adapter contract
- Issue 2.2 - Implement prediction adapter and sample alignment
- Issue 2.3 - Sanity-check adapter with BR-Gen rehearsal manifest
- Issue 2.4 - Review and milestone closeout
