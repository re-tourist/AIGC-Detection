# M3 Linux Runbook

## Purpose

This runbook describes the Linux-only commands needed to turn the implemented M3 path into a restricted COCO-only pilot.

It is not a closeout document.
Use it to separate:
- local implementation and tests
- restricted pilot validation
- blocked formal M3 work

## Runtime BR-Gen Source Root

- host path:
  - `/media/ruanzhengsen/02EE2033DCBE79181/xyj/BRGen`
- container mount:
  - `/home/workspace/AIGC/data/BRGen`
- container runtime source root used by commands below:
  - `data/BRGen/BR-Gen`
- expected raw roots under it:
  - `Forged`
  - `Mask` or `Masked`
  - `Real`, `RealImage`, or `real`

If the layout differs from the frozen M3 contract, stop before running export or evaluation.

## Current Stage Status

- formal M3:
  - blocked
- restricted pilot:
  - enabled
- source scope:
  - `COCO` only

## What Can Run Locally

- repository tests:
  - `python -m unittest discover -s tests -p 'test_*.py' -v`
- doc review and command preparation

These local checks do not count as formal M3 benchmark evidence.

## What Must Run On Linux

- COCO real subset materialization from `COCO_image_list.txt`
- restricted pilot manifest preparation from the official BR-Gen root
- Community Forensics inference export on the restricted pilot manifest
- minimal runner plus M3 localized-failure sidecar on restricted pilot manifests

## Restricted Pilot Run

Use the restricted pilot only to validate path, contract, and artifact wiring.
Do not treat it as a research conclusion.

```bash
python scripts/materialize_br_gen_real_subset.py \
  --source-root data/BRGen/BR-Gen \
  --source-dataset COCO \
  --output-root data/BRGen/BR-Gen/RealImage

python scripts/prepare_br_gen_m3_formal.py \
  --source-root data/BRGen/BR-Gen \
  --output-root data/mirrored/br_gen/subsets/restricted_pilot \
  --max-fake-samples 64 \
  --allowed-sources COCO

python scripts/export_community_forensics_predictions.py \
  --manifest data/mirrored/br_gen/subsets/restricted_pilot/manifest/formal_manifest.jsonl \
  --output outputs/m3/restricted_pilot/predictions.jsonl \
  --device cuda \
  --batch-size 16

python scripts/run_m3_formal_eval.py \
  --manifest data/mirrored/br_gen/subsets/restricted_pilot/manifest/formal_manifest.jsonl \
  --predictions outputs/m3/restricted_pilot/predictions.jsonl \
  --output-dir outputs/m3/restricted_pilot/eval
```

Expected restricted pilot artifacts:
- `data/BRGen/BR-Gen/RealImage/COCO/COCO_materialization_audit.json`
- `data/mirrored/br_gen/subsets/restricted_pilot/manifest/layout_audit.json`
- `data/mirrored/br_gen/subsets/restricted_pilot/manifest/clean_manifest.jsonl`
- `data/mirrored/br_gen/subsets/restricted_pilot/manifest/formal_manifest.jsonl`
- `outputs/m3/restricted_pilot/predictions.jsonl`
- `outputs/m3/restricted_pilot/eval/summary.json`
- `outputs/m3/restricted_pilot/eval/localized_failure_summary.json`

## Formal M3 Status

Formal M3 remains blocked.

It must not be unblocked by:
- fake-only evaluation
- COCO-only restricted pilot results
- heuristic replacement for missing ImageNet / Places real negatives

## Reporting Rule

Any future closeout must separate:
- already run locally
- implemented but not run
- restricted pilot run
- blocked formal M3 work

Do not write a formal M3 milestone closeout until ImageNet / Places real negatives are available or the contract is explicitly revised.
