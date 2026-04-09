# M6: BR-Gen-style Evaluation Protocol Alignment

GitHub milestone:
- [#6](https://github.com/re-tourist/AIGC-Detection/milestone/6)

## Status

- Closed on GitHub
- Local implementation completed
- Local code-path / unit / integration validation completed
- This milestone remains a protocol/reporting alignment milestone, not a benchmark finalization milestone
- Entry condition:
  - M5b closeout concluded that the current local-module line does not justify immediate method stacking
  - the repo still needs a stricter paper-comparable reporting contract before any new method push
- Active engineering boundary:
  - `evaluation_scope = restricted_pilot`
  - current evidence remains `diagnostic evidence`
  - current task remains `image-level localized sensitivity reporting`
- Explicitly not active:
  - new model work
  - segmentation-heavy localization benchmark work
  - IoU benchmark claims
  - milestone7 method enhancement

## Goal

Upgrade the repo evaluation contract from an internal diagnostic readout
(`accuracy / auroc / fake_recall`) to a paper-comparable reporting pipeline
that can talk to BR-Gen / "Zooming In on Fakes" tables in a partially
isomorphic way.

## In Scope

- preserve legacy metrics and keep them additive
- add paper-style `F1` and `Recall@50` style reporting
- make threshold rules explicit and auditable
- derive `generator_family` and `area_bin` through a frozen normalization layer
- export standardized JSON / CSV / Markdown artifacts
- support `overall`, `background`, `stuff`, `GAN`, `Diffusion`,
  `small`, `medium`, `large`, `clean`, `degraded`, and degradation-detail rows
- document `fully aligned`, `partially aligned`, and `deferred / blocked`
- ship a fixture-backed sample output under
  `docs/handoff/m6_protocol_alignment_fixture/`

## Out of Scope

- benchmark expansion
- segmentation-heavy task conversion
- mask-level IoU scoring without a frozen prediction/eval contract
- new local-module methods
- new training regimes
- milestone7 planning or execution

## Exit Criteria

- legacy metrics still reproduce
- the unified evaluator exports `F1` and paper-style `Recall@50` fields
- `overall_metrics.json`, `slice_metrics.json`, `slice_metrics.csv`,
  `paper_table_summary.md`, and `protocol_alignment_audit.json` are emitted
- Split A / Split B / area bins / clean-vs-degraded reporting is available
- docs clearly separate `fully aligned`, `partially aligned`, and `deferred`
- IoU is honestly marked as deferred
- the milestone does not drift into segmentation-heavy benchmarking

## Issue Set

- Issue 6.1 - Evaluation contract audit
- Issue 6.2 - Metric alignment implementation
- Issue 6.3 - Metadata and slice reporting alignment
- Issue 6.4 - Docs, closeout, and paper-style outputs

## Deliverable Pointers

- Protocol doc:
  - `docs/contracts/m6_br_gen_style_evaluation_protocol.md`
- Closeout / audit doc:
  - `docs/handoff/m6_br_gen_style_evaluation_protocol_alignment_closeout.md`
- GitHub milestone:
  - https://github.com/re-tourist/AIGC-Detection/milestone/6
- Fixture sample artifacts:
  - `docs/handoff/m6_protocol_alignment_fixture/`
