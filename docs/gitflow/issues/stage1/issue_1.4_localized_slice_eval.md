# Issue 1.4 — Implement localized clean / degraded slice evaluation

## Background

Stage 1 的关键不是 full-image 指标本身，而是验证：
强 global baseline 是否仍然会在 localized edit 上系统性掉分。
因此 localized evaluation 必须是结构化 slice 评测，而不是一个总分脚本。

## Suggested Branch

`codex/stage1-localized-slices`

## Goal

实现 localized clean / degraded 与 area / subtlety / region slice 级评测流程，
输出足以支撑 H2 的结构化结果。

## Tasks

- 建立 localized overall eval
- 建立 small / medium / large slice
- 建立 subtle / obvious slice
- 建立 object / background slice
- 汇总 degraded localized eval 结果

## Resource Boundary

- 区分“slice 定义已固定”和“slice 样本已足够”是两件事
- 如果缺少关键标注，必须把它记录成显式阻塞项
- 图表 first-pass 可先出草图，但不能伪装成最终结果

## Non-Goals

- 不实现 local branch / consistency
- 不改 localized slice 语义
- 不新造 benchmark

## Deliverable

- localized overall eval
- clean / degraded localized 汇总
- slice 级结果表与图

## Acceptance

- localized overall 与 slice 级结果可输出
- clean / degraded localized 被分开汇报
- 结果能支持“哪里掉、为什么掉”的分析
