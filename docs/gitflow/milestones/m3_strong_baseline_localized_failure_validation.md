# M3: Strong Baseline Localized Failure Validation

GitHub milestone:
- `https://github.com/re-tourist/AIGC-Detection/milestone/4`
- state: `CLOSED`

## Status

- Local repo status:
  - M3 code paths for formal BR-Gen manifest preparation, perturbation-aware
    Community Forensics export, and localized-failure sidecar reporting are
    implemented
  - the expanded full-COCO restricted pilot has been executed on Linux and the
    resulting failure-evidence artifacts are available in the workspace
  - an explicit M3 closeout and M4 handoff has been written
  - focused local tests pass in the current workspace
- Remaining milestone status:
  - the active executed path is the expanded `COCO-only restricted_pilot`
  - formal M3 remains unavailable because ImageNet / Places real negatives are
    unavailable
  - formal M3 is not the active next step and is being explicitly deferred
- Current evidence level:
  - restricted-pilot failure mapping exists
  - restricted-pilot evidence is sufficient for M4 method entry
  - formal benchmark evidence does not exist
  - the milestone is being closed with documented limitations, not as a formal
    benchmark success

## Goal

Formally validate whether a strong baseline still shows structured failure on
localized edits under the current repository data, metric, and runner contract.

Current execution note:

- the expanded full-COCO restricted pilot is complete
- formal M3 is intentionally deferred
- current M3 evidence is diagnostic and restricted-pilot scoped, not formal
  benchmark evidence
- the practical handoff target is M4 on the COCO-only engineering line

## In Scope

- audit the official BR-Gen raw layout from the Linux server root
- prepare clean and degraded localized manifests without copying the full
  dataset into the repository
- reuse the existing Community Forensics export path to produce repo-compatible
  prediction JSONL
- run the existing minimal runner plus an M3 sidecar report
- execute and analyze the expanded `COCO-only restricted_pilot`
- write a Linux runbook that separates restricted-pilot evidence from the
  blocked formal full run
- write a closeout that explicitly hands off to M4 on the COCO-only
  engineering line

## Out of Scope

- any change to the frozen M1 contract
- Community Forensics paper reproduction
- generator-diverse retraining
- heuristic inference of new slice metadata
- treating `data/tmp/cf_smoke/` as benchmark evidence
- treating restricted-pilot results as formal benchmark evidence
- formal M3 continuation without restored negatives

## Execution Contract

### Official BR-Gen root

- formal M3 work must take an explicit external source root
- the current official root is:
  - `/media/ruanzhengsen/02EE2033DCBE79181/xyj/BRGen/BR-Gen`
- M3 must not silently fall back to `data/BR-Gen`

### Raw layout assumptions

- fake images must be discovered under:
  - `Forged/<generator>/<region>/<source>/<file>`
- mask root may be either:
  - `Mask`
  - `Masked`
- real root may be either:
  - `Real`
  - `RealImage`
  - `real`
- ambiguous roots, invalid fake layout, or missing fake/mask/real pairing are
  hard errors

### Manifest contract

- `clean_manifest.jsonl` contains clean localized real and fake samples only
- `formal_manifest.jsonl` contains the clean set plus fixed degraded variants:
  - `jpeg`
  - `resize`
  - `blur`
  - `crop`
- raw manifest records do not carry `edit_area_ratio`
- degraded variants are represented through explicit `meta.perturbation`

### Perturbation contract

- JPEG quality:
  - `85`
- resize scale:
  - `0.90`
- Gaussian blur sigma:
  - `1.0`
- crop mode:
  - centered crop retaining `90%` image area
- degraded images are generated on the fly during export and are not written
  back as copied dataset assets

### Reporting contract

- the existing minimal runner remains the first artifact writer
- M3 adds a sidecar localized-failure report that summarizes:
  - overall clean localized metrics
  - metrics by degradation
  - metrics by `region_type`
  - metrics by `edit_area_ratio` bins
  - blocked `subtlety`
  - clean-to-degraded deltas
  - worst-slice ranking
  - coverage audit and failure evidence map for restricted-pilot analysis

## Exit Criteria

- the official BR-Gen layout can be audited and manifests can be written
  reproducibly
- Community Forensics export can emit repo-compatible predictions for both the
  restricted pilot and, when unblocked, the formal manifest
- the minimal runner and M3 sidecar report both produce traceable artifacts
- restricted-pilot evidence clearly states:
  - what it shows
  - what remains blocked
  - why it is not a formal benchmark claim
- the milestone closeout explicitly states that M3 is being handed off through
  the `COCO-only restricted_pilot` line
- the formal path is either executed or explicitly deferred before leaving M3

## Issue Set

- #17 Issue 3.0 - Sync M3 GitHub milestone and issue set
- #18 Issue 3.1 - Freeze M3 contract and audit official BR-Gen raw layout
- #19 Issue 3.2 - Prepare formal BR-Gen manifests and perturbation-aware export
- #20 Issue 3.3 - Add localized-failure sidecar reporting on top of the current runner
- #21 Issue 3.4 - Formal Linux run and formal closeout path (deferred)
- #22 Issue 3.5 - Expand restricted pilot evidence and failure mapping
