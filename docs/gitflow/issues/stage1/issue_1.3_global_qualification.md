# Issue 1.3 — Implement strong baseline qualification evaluation

## Background

如果不能先证明 `B1-diverse` 在 full-image image-level detection 上足够强，
后续所有 localized failure 结论都会被质疑成“只是 baseline 太弱”。

## Suggested Branch

`codex/stage1-global-qualification`

## Goal

建立 full-image clean / unseen / degraded 评测与汇总流程，
输出 Stage 1 的 baseline qualification 结果。

## Tasks

- 建立 checkpoint 加载与 inference 路径
- 计算 AUROC / AUPR(or AP) / Accuracy / fake recall 等基础指标
- 输出 clean / unseen / degraded 维度上的结果汇总
- 形成 Table 1 风格报表

## Resource Boundary

- 不要把一个 overall accuracy 当作 qualification 充分证据
- 如果 unseen / degraded 数据口径不清，应先停下澄清
- first-pass eval 可以先做小规模验证，但必须和正式结论区分

## Non-Goals

- 不做 localized slice 评测
- 不实现 `M1 / M2`
- 不在本 issue 里展开大规模 ablation

## Deliverable

- baseline qualification eval 路径
- clean / unseen / degraded 结果表
- 可回溯的 inference summary

## Acceptance

- qualification eval 可独立运行
- clean / unseen / degraded 结果可被输出与回溯
- 能明确判断 strong baseline 是否被站稳
