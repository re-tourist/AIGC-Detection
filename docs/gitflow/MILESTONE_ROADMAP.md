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
