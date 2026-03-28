# Issue 1.4 — Implement minimal evaluation runner and artifact save path

## Background

M1 不需要完整 execution harness。
它只需要一个最小 runner，把 normalized samples 和外部 prediction 输入接起来，算出最小指标并落最小输出。

## Suggested Branch

`codex/stage1-minimal-eval-runner`

## Goal

实现最小 evaluation runner 和 artifact save path，
让 M1 能用小样本做端到端 smoke validation。

## Tasks

- 消费 normalized samples
- 读取 prediction input
- 运行 minimal metric core
- 输出 JSON summary、CSV metrics、Markdown smoke report、config snapshot

## Resource Boundary

- 不把这一层扩写成完整 training/inference harness
- 不在本 issue 中写 Linux 服务器 orchestration
- 只做最小可验证落盘路径

## Non-Goals

- 不做 Community Forensics integration
- 不实现服务器规模 eval
- 不写复杂 report automation

## Deliverable

- minimal evaluation runner
- minimal artifact save path
- runner smoke test

## Acceptance

- runner 能消费 normalized samples 并写出最小 outputs
- output 包含 command/config provenance
- 没有对全量数据存在性做 repo-tracked 假设
