# Data Layout

## Purpose

This document defines the repository-side data layout for the early project stage.

The goal is to support:
- no fixed primary dataset yet;
- one or more future candidate datasets;
- local mirrored subsets copied from the Linux server;
- manifest-driven evaluation and rehearsal;
- clear separation between raw files, manifests, and temporary/generated artifacts.

This layout is intentionally conservative.
It should support current `M1` and early `M2` work without forcing a final long-term dataset choice.

---

## Design Principles

### 1. Dataset-agnostic root

Do not assume `BR-Gen` is permanently the primary dataset.

The top-level structure should let multiple datasets coexist, for example:
- `BR-Gen`
- a future full-image fake dataset
- a future localized-edit benchmark

### 2. Manifest-first evaluation

Code should rely on manifests, not on implicit folder semantics.

Folder structure helps organization, but the contract-relevant truth should remain in:
- manifest files
- explicit metadata
- relative paths referenced by manifests

### 3. Separate mirrored subsets from full data

The local machine should hold only:
- small mirrored subsets
- directory structure snapshots
- manifests
- rehearsal artifacts

The Linux server remains the place for full-scale data and heavy runs.

### 4. Keep generated files out of raw dataset folders

Generated files such as:
- temporary predictions
- rehearsal outputs
- derived manifests

should not be mixed into copied raw image folders.

---

## Recommended Layout

```text
data/
  README.md
  registry/
    datasets/
    manifests/
    schemas/
  mirrored/
    br_gen/
      README.md
      subsets/
        smoke/
          manifest/
          images/
          masks/
          predictions/
        rehearsal/
          manifest/
          images/
          masks/
          predictions/
        formal/
          manifest/
      snapshots/
    placeholders/
  external/
    README.md
  tmp/
    README.md
```

---

## Directory Roles

### `data/registry/`

This stores repo-side metadata and contracts, not large data payloads.

#### `data/registry/datasets/`

Use this for one file per dataset candidate.

Recommended file naming:
- `br_gen.dataset.md`
- `community_forensics_support.dataset.md`
- `future_dataset_name.dataset.md`

Each file should describe:
- dataset purpose
- source location
- whether it supports `full_image_fake` or `localized_edit`
- whether it is a training source or evaluation source
- whether the local repo contains a mirrored subset only

#### `data/registry/manifests/`

Use this for checked-in example manifests or manifest templates that are small enough for git.

Recommended uses:
- schema examples
- tiny smoke manifests
- reference manifest templates

Do not put large full manifests here if they are unstable or too big.

#### `data/registry/schemas/`

Use this for schema notes or future machine-readable schema definitions if needed.

For now, the main active schema source of truth remains:
- `docs/contracts/contract_freeze_stage1_data_metric_bootstrap.md`

### `data/mirrored/`

This is the local landing zone for subsets copied from the Linux server.

Each dataset gets its own folder, for example:
- `data/mirrored/br_gen/`

Do not assume these folders contain the full dataset.
They are local mirrors or partial mirrors only.

### `data/mirrored/br_gen/subsets/smoke/`

Use this for the smallest local subset used for:
- loader checks
- manifest validation
- runner smoke checks

This can be replaced or regenerated as needed.

### `data/mirrored/br_gen/subsets/rehearsal/`

Use this for the first realistic mirrored subset used before formal milestone close or before baseline integration.

This is the best place for the real mirrored-subset rehearsal we discussed.

Expected contents:
- `manifest/`
- `images/`
- `masks/` when available
- `predictions/` for dummy or baseline exports

### `data/mirrored/br_gen/subsets/formal/`

Use this for formal M3 manifest artifacts derived from the official external BR-Gen root.

Expected contents:
- `manifest/`

Important:
- this folder stores manifests and layout-audit outputs, not a copied full BR-Gen raw tree
- the official BR-Gen raw data should remain at the external Linux source root

### `data/mirrored/br_gen/snapshots/`

Use this for lightweight directory snapshots, notes, or inventories copied from the server.

Examples:
- tree snapshots
- filename inventories
- dataset notes

### `data/mirrored/placeholders/`

Use this when the final dataset choice is not fixed yet but you want to reserve structure for another candidate.

### `data/external/`

Use this for human-written notes about external dataset sources that are not mirrored locally yet.

Do not use it for actual raw files.

### `data/tmp/`

Use this for throwaway local helper files that should not be committed as research assets.

Examples:
- temporary manifest conversion outputs
- temporary prediction exports
- path audit files

---

## Manifest Placement Rule

For early-stage work, manifests should live close to the subset they describe.

Recommended rule:
- subset-local manifests go under the subset folder, such as:
  - `data/mirrored/br_gen/subsets/rehearsal/manifest/manifest.jsonl`
- tiny checked-in examples or templates may also appear under:
  - `data/registry/manifests/`

This gives two layers:
- local operational manifest near the copied files
- repo reference manifest or template in the registry

---

## Current Recommendation for BR-Gen

If you next prepare a real rehearsal subset from `BR-Gen`, place it here:

```text
data/mirrored/br_gen/subsets/rehearsal/
  manifest/
    manifest.jsonl
  images/
  masks/
  predictions/
```

Minimum viable contents for the next rehearsal:
- `manifest/manifest.jsonl`
- copied sample files under `images/`

Optional but useful:
- `masks/`
- `predictions/dummy_predictions.jsonl`
- `predictions/community_forensics_predictions.jsonl`

For formal M3 localized validation, generate manifests from the official external source root into:

```text
data/mirrored/br_gen/subsets/formal/
  manifest/
    clean_manifest.jsonl
    formal_manifest.jsonl
    layout_audit.json
```

Recommended command:

```text
python scripts/prepare_br_gen_m3_formal.py --source-root /media/ruanzhengsen/02EE2033DCBE79181/xyj/BRGen/BR-Gen --output-root data/mirrored/br_gen/subsets/formal
```

This keeps the full raw dataset outside the repository while still creating traceable formal manifests.

If the first source drop arrives outside the recommended layout, for example under:

```text
data/BR-Gen/
```

do not manually reorganize the raw files first.
Instead, generate the rehearsal manifest and dummy predictions with:

```text
python scripts/prepare_br_gen_rehearsal.py --source-root data/BR-Gen --output-root data/mirrored/br_gen/subsets/rehearsal
```

This keeps the source drop untouched while still creating an operational rehearsal subset.

---

## Why This Layout Is Better Than a Single Hardcoded Dataset Folder

If we instead used something like:

```text
data/
  br_gen/
```

too early, we would create three problems:
- it would implicitly declare `BR-Gen` as the permanent primary dataset;
- it would mix raw files, manifests, and generated artifacts too easily;
- it would make later multi-dataset evaluation harder to reason about.

The recommended layout avoids that while staying simple enough for the current project stage.

---

## Short-Term Usage Rule

For the next step in this repository:

1. keep repo smoke fixtures in `tests/fixtures/local_mirror/`
2. put the first real copied subset under `data/mirrored/br_gen/subsets/rehearsal/`
3. run the rehearsal using the manifest stored inside that subset
4. keep generated evaluation outputs under `outputs/`, not under `data/`

---

## Future Revision Trigger

This document should be revised only when one of the following becomes true:
- a primary dataset is officially frozen;
- multiple datasets are actively used in training or evaluation;
- full-manifest management becomes complex enough to require machine-readable schema files or manifest tooling;
- Linux-server-to-local sync rules need to be formalized.
