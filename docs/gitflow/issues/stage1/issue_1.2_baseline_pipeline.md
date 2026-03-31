# Issue 1.2 — Implement B0 / B1 / B1-diverse baseline pipeline

## Background

Stage 1 的核心不是“先发明新模块”，而是先把强 baseline 站稳。
当前仓库尚无训练/评测代码，因此需要在冻结边界内建立最小 baseline pipeline，
并保证 `B1-diverse` 相比 `B1` 的核心差异只来自 generator diversity。

## Suggested Branch

`codex/stage1-baseline-pipeline`

## Goal

实现 `B0`、`B1`、`B1-diverse` 的统一 baseline 训练与推理闭环，
为 full-image qualification 与 localized evaluation 提供可复用入口。

## Tasks

- 建立 baseline model build 入口
- 接通 feature extraction / probe 路径
- 建立 train / val / test 基础闭环
- 写出 checkpoint 与 summary

## Resource Boundary

- 区分“pipeline 可跑通”和“长预算训练已完成”
- 大计算量训练应迁移到 Linux 服务器，不要把 smoke run 写成正式结果
- 如果 baseline reference 实现或 checkpoint 无法确认，必须停下汇报

## Non-Goals

- 不实现 `M1 / M2`
- 不扩 benchmark
- 不改 Stage 1 的 baseline 语义

## Deliverable

- baseline 模型构建入口
- 最小 train/eval 闭环
- checkpoint / summary 输出

## Acceptance

- `B0` / `B1` / `B1-diverse` 能通过统一入口构建
- 至少完成 toy / smoke 级别的 train-eval 闭环
- 输出物可被后续 qualification 和 localized eval 复用
