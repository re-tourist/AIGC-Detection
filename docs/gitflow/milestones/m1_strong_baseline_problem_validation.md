# Deprecated Draft: M1 Strong Baseline Problem Validation

Status:
- This document reflects an earlier aggressive split that jumped too early into baseline implementation and validation.
- It is kept only as a historical draft for traceability.
- The current macro roadmap is now defined by:
  - `docs/gitflow/MILESTONE_ROADMAP.md`
  - `docs/gitflow/milestones/m1_data_metric_pipeline_bootstrap.md`
  - `docs/gitflow/milestones/m2_community_forensics_integration.md`
  - `docs/gitflow/milestones/m3_strong_baseline_localized_failure_validation.md`

GitHub milestone:
- `https://github.com/re-tourist/AIGC-Detection/milestone/1`

## Goal

在不引入 local branch / consistency 的前提下，建立并验证 `B0` / `B1` / `B1-diverse`，
确认 strong generator-diverse baseline 是否仍存在结构性 localized failure，
并产出决定是否进入 Stage 2 的第一轮证据。

## In Scope

- 建立 Stage 1 的数据 / 配置 / artifact contract
- 建立 `B0` / `B1` / `B1-diverse` baseline pipeline
- 完成 full-image clean / unseen / degraded qualification evaluation
- 完成 localized clean / degraded slice evaluation
- 产出 first-pass result package 与 closeout

## Out of Scope

- `M1 / M2` 方法模块实现
- benchmark 重设计
- 论文定稿与提交包装

## Exit Criteria

- `B0` / `B1` / `B1-diverse` 的定义、配置与结果可回溯
- full-image qualification 与 localized slice 结果都已产出
- 能明确回答 strong baseline 是否仍保留结构性 localized failure
- Stage 2 是否进入有书面化判断依据

## Issue Set

- Issue 1.1 — Freeze Stage 1 data/config manifests and artifact contract
- Issue 1.2 — Implement B0 / B1 / B1-diverse baseline pipeline
- Issue 1.3 — Implement strong baseline qualification evaluation
- Issue 1.4 — Implement localized clean / degraded slice evaluation
- Issue 1.5 — Run first-pass Stage 1 experiments and write closeout
