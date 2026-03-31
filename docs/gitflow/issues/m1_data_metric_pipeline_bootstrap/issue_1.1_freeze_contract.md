# Issue 1.1 — Freeze M1 data contract, manifest schema, and artifact contract

## Background

M1 不能先写 loader 和 metric，再回头补 schema 与 stop rule。
当前项目几乎没有可执行实验底座，因此第一步必须先冻结最小数据契约、字段分类、指标优先级和输出边界。

## Suggested Branch

`codex/stage1-data-contract`

## Goal

冻结 `M1` 的 active plan、issue split、contract，以及 manifest schema、metric priority、artifact contract 和 stop rules，
作为后续 loader / metric / runner 的唯一语义边界。

## Tasks

- 建立 M1 的 active stage plan
- 建立 M1 的 active issue breakdown
- 建立 M1 的 active contract freeze
- 区分 required raw / optional raw / derived fields
- 冻结 metric priority 和 explicit stop rules

## Resource Boundary

- 不实现 loader、metric 或 runner 逻辑
- 不引入 Community Forensics
- area-ratio derivation rule 如果本阶段不冻结，就必须显式标记为 blocked

## Non-Goals

- 不读取全量服务器数据
- 不实现大规模运行
- 不做 baseline integration

## Deliverable

- active M1 plan doc
- active M1 issue doc
- active M1 contract freeze
- 明确的 manifest / metric / artifact contract

## Acceptance

- manifest schema 明确 required raw、optional raw、derived 三类字段
- metric priority 与 stop rules 已写入 active contract
- 后续 issue 可以在不再解释语义边界的前提下直接实现
