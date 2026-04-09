# MILESTONE_ROADMAP

## Purpose

This document is the current macro-level milestone source of truth.

当前路线已经从“先追 formal localized benchmark”调整成“两阶段推进”：
- 先把 restricted-pilot 证据线跑实
- 再沿 COCO-only engineering line 做方法验证

因此 roadmap 必须显式区分：
- benchmark 级结论
- engineering 级方法验证

---

## Roadmap

### M1: Data and Metric Pipeline Bootstrap

目标：
- 先把 localized eval 所需的数据、schema、metric、artifact contract 建起来

核心内容：
- localized eval data pipeline
- full-image / localized unified sample schema
- clean / degraded / slice metadata loading
- metric pipeline
- result / artifact schema
- smoke checks

### M2: Community Forensics Integration

目标：
- 将 Community Forensics 作为 strong baseline 候选接入当前 repo pipeline

核心内容：
- baseline adapter
- repo-compatible prediction export
- smoke fixture and runner sanity
- M2 contract freeze and integration closeout

### M3: Strong Baseline Localized Failure Validation

目标：
- 在当前 repo contract 下判断 strong baseline 是否存在结构化 localized failure

实际收口状态：
- expanded full-COCO `restricted_pilot` 已完成
- formal M3 未完成，也不再作为当前主线继续推进
- M3 当前按“close with documented limitations”处理
- M3 的有效产出是一张 restricted-pilot 级 failure evidence map

当前可复用结论：
- `stuff` 区域是稳定 weak slice
- `small / medium` edit area 是稳定 weak slice
- `background` 仍然是 easy regime

### M4: Community Forensics Local Module on COCO Engineering Line

目标：
- 在 Community Forensics baseline 之上接入一个 local module
- 仅在 `COCO-only restricted_pilot` 工程线上判断它是否改善 M3 已识别的 weak slices

核心内容：
- freeze M4 的 COCO-only engineering boundary
- 找到 local module 的最小集成点
- baseline vs local-module 对比
- 重点看：
  - `stuff`
  - `small / medium` edit area
  - degradation 下的 slice 行为

边界：
- 不追 formal M3
- 不引入 ImageNet / Places negatives
- 不做 benchmark overclaim

---

## Planning Rule

当前宏观顺序调整为：
1. `M1` 建 data / metric pipeline
2. `M2` 接 Community Forensics baseline
3. `M3` 建 restricted-pilot 级 failure evidence
4. `M4` 在 COCO-only engineering line 上验证 local module

不要把当前 M4 误写成 formal benchmark continuation。
---

### M5: Trainable Soft Local Aggregation on COCO Restricted Pilot

Goal:
- test whether a minimal trainable soft local aggregation path can amplify the
  stable local-evidence signal from M4 without breaking the easy regime

Core content:
- frozen-backbone validation only
- COCO-only restricted pilot
- frozen holdout split contract
- baseline vs M4 vs M5 comparison on the same frozen holdout

Boundary:
- not a benchmark milestone
- not cross-dataset completion
- not subtlety completion
- not consistency work
- not full finetuning

Planning rule update:
1. `M1` build the data / metric pipeline
2. `M2` integrate Community Forensics baseline
3. `M3` validate restricted-pilot failure evidence
4. `M4` validate the no-train local probe on the COCO engineering line
5. `M5` test trainable soft local aggregation on the same restricted-pilot boundary

### M5b: Local-Module Attribution Closeout

Goal:
- keep M5 frozen and separate localized training effect from local-module structural effect

Core content:
- `localized_train_global_only_control`
- paired `control vs M5` attribution
- multi-seed paper-minimum evidence

Boundary:
- not a new milestone
- not benchmark expansion
- not consistency / robustness / subtlety work

Planning rule update:
6. `M5b` runs after M5a closeout as a phase-style attribution closeout within M5

### M6: BR-Gen-style Evaluation Protocol Alignment

Goal:
- align the repo evaluation/reporting grammar with BR-Gen-style reporting
  without changing the current task boundary

Core content:
- preserve `accuracy / auroc / fake_recall`
- add paper-style `F1` and `Recall@50` style reporting
- add threshold-difference audit fields
- derive `generator_family` and `area_bin` for reporting
- export standardized JSON / CSV / Markdown artifacts
- support `overall`, `background`, `stuff`, `GAN`, `Diffusion`,
  `small`, `medium`, `large`, `clean`, `degraded`, and degradation-detail rows

Boundary:
- not a new method milestone
- not segmentation-heavy localization benchmarking
- not IoU formalization
- not itself a method verdict repair milestone

Planning rule update:
7. `M6` calibrates the evaluation ruler before any further method push

Closeout note:
- GitHub milestone `#6` is closed
- the repo now carries a finalized closeout record and fixture-backed paper-style summary

### M7: Matched-Control Audit and Fairness Repair

Goal:
- audit every fairness dimension that can distort the attribution verdict
  between `current_local` and the existing `control`
- repair the control into a conceptually matched `global-only` arm
- rerun the attribution question under a fairer three-arm protocol

Core content:
- forward-path audit
- freeze / no-grad audit
- head / trainable-parameter audit
- optimization / protocol parity audit
- memory / compute audit
- repaired `matched_global_only_control`
- seed `42/43` required replay plus seed `44` canary

Boundary:
- not a new local-module method milestone
- not gated fusion / new loss / consistency work
- not benchmark expansion
- not formal benchmark overclaim
- not a replacement of historical M5b artifacts

Planning rule update:
8. `M7` repairs the attribution/control ground truth before any further local-module push
