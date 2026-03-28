# Issue 1.1 — Freeze Stage 1 data/config manifests and artifact contract

## Background

Stage 1 不能先写模型再回头补边界。
在 strong baseline 问题成立性验证中，数据 split、配置字段、artifact 输出结构如果先不冻结，
后续即使代码能跑，也很容易让比较失去可回溯性。

## Suggested Branch

`codex/stage1-contract-manifests`

## Goal

把 `B0` / `B1` / `B1-diverse` 所需的数据 manifest、配置约定、artifact 目录结构和 Linux 服务器 handoff 规则固定下来，
作为 Stage 1 后续所有实现与运行的统一输入。

## Tasks

- 定义 Stage 1 的数据 split / manifest 字段
- 定义 baseline 组别与配置约定
- 定义 `outputs/` 下的最小 artifact 结构
- 写清楚本地 smoke 与 Linux server run 的边界

## Resource Boundary

- 区分清楚“schema 已冻结”和“真实数据已到位”是两件事
- 如果数据源、checkpoint 来源或 slice 标注不清，应显式暴露为依赖，不要假装已确认
- 大计算量扫描或训练不在本 issue 内

## Non-Goals

- 不实现模型结构
- 不启动大规模训练
- 不实现 `M1 / M2`

## Deliverable

- Stage 1 可执行配置/manifest 约定
- artifact 路径与命名规则
- server handoff 说明

## Acceptance

- 配置字段和 manifest 字段可被说明并加载
- artifact 输出结构可被后续 issue 复用
- 本地 smoke 与 Linux server run 的边界被写清楚
