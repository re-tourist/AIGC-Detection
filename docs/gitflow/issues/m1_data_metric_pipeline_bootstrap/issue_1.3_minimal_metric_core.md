# Issue 1.3 — Implement minimal metric core

## Background

M1 只需要最小可用 metric core，不需要一次性做完全部 slice reporting。
目标是先让 overall metrics 可算，再在 metadata 明确存在时支持高优先级 grouped reporting。

## Suggested Branch

`codex/stage1-metric-core`

## Goal

实现最小 metric core，覆盖 overall 指标以及高优先级 grouped reporting，
并为不支持的 slice 维度给出明确 blocked/unsupported 状态。

## Tasks

- 实现 AUROC
- 实现 Accuracy
- 实现 fake_recall
- 支持 by task_type grouped reporting
- 支持 by degradation grouped reporting when metadata exists
- 对 region_type / subtlety / edit_area_ratio bins 输出 blocked/unsupported 状态

## Resource Boundary

- 不发明 metadata 语义
- 没有显式 metadata 就不能偷偷补 grouped reporting
- `edit_area_ratio` 如果 derivation rule 未冻结，就不能做 bins

## Non-Goals

- 不实现 baseline scoring
- 不实现 full execution harness
- 不把全部 slice reporting 变成 M1 刚需

## Deliverable

- minimal metric core
- grouped reporting for P1 dimensions
- blocked status for unsupported P2 dimensions

## Acceptance

- overall metrics 可在小样本上运行
- by task_type grouped reporting 可运行
- by degradation 仅在 metadata 存在时运行
- unsupported slice dimensions 会被明确标记
