# contract_freeze

## Contract Title

- Contract ID: `contract_stage1_problem_validation_20260327`
- Related stage / milestone: `stage1_problem_validation`
- Status:
  - [ ] proposed
  - [x] frozen
  - [ ] revised
  - [ ] retired
- Owner:
  - human research owner
  - codex bootstrap docs
- Last updated: `2026-03-27`

## 1. Purpose

This contract freeze exists to lock the current working boundary for this stage.

Its purpose is to prevent:
- silent scope drift
- accidental interface changes
- semantic changes hidden inside “small implementation tweaks”
- repeated redesign during an execution phase

This document is not a full design spec.
It is a boundary document.

对 Stage 1 而言，它主要锁定一件事：

> 本阶段只做 strong baseline 的问题成立性验证，不做 local branch / consistency 的方法创新。

---

## 2. What This Contract Covers

Current contract scope:
- item 1:
  - Stage 1 的核心目标：建立并验证 `B0` / `B1` / `B1-diverse`
- item 2:
  - Stage 1 的评测含义：full-image global qualification 与 localized clean / degraded slice evaluation
- item 3:
  - Stage 1 的输出物：可回溯配置、评测结果、图表、closeout

---

## 3. Frozen Objectives

The following goals are fixed for this stage:

- Objective 1:
  - 证明或证伪：增加 generator diversity 后，`B1-diverse` 是否成为更可信的 strong global baseline
- Objective 2:
  - 证明或证伪：即便 strong baseline 成立，localized editing 是否仍保留结构性失败
- Objective 3:
  - 产出足以决定是否进入 `M1 / M2` 方法阶段的第一轮证据

These objectives must not be reinterpreted during normal implementation work.

If execution reveals they are no longer valid, stop and report instead of redefining them silently.

---

## 4. Frozen Inputs / Outputs

### Inputs
- Input A:
  - source:
    - `docs/localized_failure_on_strong_baseline_protocol.md`
    - future baseline reference implementation / checkpoint
  - expected form:
    - 支持 `B0` / `B1` / `B1-diverse` 的统一 baseline 定义
  - meaning:
    - Stage 1 用于验证 strong baseline 与 localized failure 的核心实现基础
- Input B:
  - source:
    - full-image real/fake 数据
    - localized edit clean / degraded 数据
    - slice 所需元信息
  - expected form:
    - 可通过配置或 manifest 明确区分训练/验证/测试及 full-image / localized 评测用途
  - meaning:
    - 支撑 H1 / H2 的正式输入，不允许混淆 full-image 与 localized 任务
- Input C:
  - source:
    - `docs/plan/plan_stage1_problem_validation.md`
    - `docs/plan/issue_stage1_problem_validation.md`
  - expected form:
    - 可执行 stage / issue 拆分
  - meaning:
    - 固定 Stage 1 的 task definition 与 split protocol

### Outputs
- Output A:
  - location / API / artifact:
    - baseline configs / manifests / run scripts
  - expected form:
    - 可回溯的 `B0` / `B1` / `B1-diverse` 配置与命令记录
  - meaning:
    - 保证 strong baseline qualification 的可复查性
- Output B:
  - location / API / artifact:
    - Stage 1 result tables / plots / summaries under `outputs/` and `docs/`
  - expected form:
    - 至少包含 full-image qualification 结果与 localized slice 结果
  - meaning:
    - 用来回答 strong baseline 是否仍存在结构性 localized failure
- Output C:
  - location / API / artifact:
    - `docs/handoff/milestone_closeout_stage1_problem_validation.md`
  - expected form:
    - 清楚记录已完成、未完成、验证与风险
  - meaning:
    - 决定是否进入 Stage 2

If an implementation needs to change any of the above, it must trigger a freeze review.

---

## 5. Frozen Interfaces

Frozen interfaces:
- Interface 1:
  - baseline 组别语义固定为：
    - `B0 = frozen backbone + linear probe`
    - `B1 = frozen backbone + MLP probe`
    - `B1-diverse = B1 + generator-diverse fake training`
- Interface 2:
  - 评测分层语义固定为：
    - full-image clean / unseen / degraded
    - localized clean / degraded
    - localized slices 至少覆盖 area、subtlety、region 三个维度
- Interface 3:
  - Stage 1 只允许比较 baseline 侧结果，不允许把 `M1 / M2` 混入主结论
- Interface 4:
  - 阈值与指标协议必须记录并可回溯；不能看到结果后再改 metric meaning

Allowed tolerance:
- minor internal refactor that preserves interface meaning
- doc clarification without semantic change
- non-breaking validation additions
- 额外增加不改变主语义的辅助图表或统计

Not allowed:
- renaming without approval
- silent semantic drift
- hidden behavior changes behind the same interface
- 将 Stage 1 从 problem validation 改写成 method validation

---

## 6. Allowed Change Window

The following changes are allowed within this frozen stage:

- implementation detail improvements that do not change semantics
- focused bug fixes that restore intended behavior
- additional tests / validation
- documentation sync
- narrow refactors that preserve interfaces and outputs

Project-specific allowed changes:
- Allowed change 1:
  - 在不改变语义的前提下确定具体配置字段、artifact 路径、脚本布局
- Allowed change 2:
  - 增加 localized slice 的诊断统计，只要不改变 slice 定义与主结论口径
- Allowed change 3:
  - 将大计算量命令整理成 Linux 服务器 runbook

---

## 7. Explicitly Forbidden Changes

The following changes must not be made during this stage without explicit approval:

- Forbidden change 1:
  - 引入 `M1`、`M2`、local branch、deployment-aware consistency 或其他新方法模块
- Forbidden change 2:
  - 改写 Stage 1 的目标，使其从“问题成立性验证”变成“方法提分验证”
- Forbidden change 3:
  - 看到结果后再重定义 localized slice、threshold protocol、evaluation meaning
- Forbidden change 4:
  - 未经批准更换 backbone / checkpoint / 数据源，并仍把结论写成同一 Stage 1 比较
- Forbidden change 5:
  - 声称已经完成重训练或大评测，但实际上没有跑

---

## 8. Validation Contract

The following validation expectations are frozen for this stage:

- required local checks:
  - 配置/manifest 解析 smoke check
  - baseline forward / eval dry-run
  - metric 与 slice bucket 的基础 sanity check
- required focused tests:
  - 至少一个小规模 train-eval 闭环
  - 至少一个 localized eval smoke run
  - artifact 写出与回读检查
- required manual sanity checks:
  - 确认 `B1-diverse` 与 `B1` 的差异没有越过 generator diversity
  - 确认 Stage 1 没混入方法模块
  - 确认 Linux 服务器执行与本地 smoke 执行被如实区分
- optional broader checks:
  - 多 seed
  - 更广泛 degradation sweep
  - 更多 parameter / data control ablation

---

## 9. Stop Conditions

If any of the following happen, stop and report:

- the implementation cannot proceed without changing a frozen interface
- validation evidence contradicts the frozen objective
- the requested task implies scope expansion beyond this contract
- missing upstream dependency makes the contract impossible to honor
- semantic correctness becomes uncertain in a way that tests do not catch

Project-specific stop conditions:
- Stop condition 1:
  - 无法确认 strong baseline 的 reference 实现、checkpoint 或数据前提
- Stop condition 2:
  - localized 数据或 slice 标注不足以维持当前评测语义
- Stop condition 3:
  - 需要改 task definition / split protocol / contract freeze 才能继续

---

## 10. Change Control

If someone believes this contract must change, do not silently edit code first.

Use this process:

1. identify the exact frozen item that is no longer viable
2. explain why it blocks execution or correctness
3. propose the smallest necessary revision
4. obtain human approval
5. update this contract explicitly before continuing

---

## 11. Linked Documents

Relevant docs:
- `docs/ai/PROJECT_CONTEXT.md`
- `docs/plan/plan_stage1_problem_validation.md`
- `docs/plan/issue_stage1_problem_validation.md`
- `docs/localized_failure_on_strong_baseline_protocol.md`
- `docs/review/code_review.md`

Project-specific links:
- `docs/experiment_background.md`
- `docs/实验开展先决条件分析.md`

---

## 12. Freeze Review Notes

### Review entry
- date: `2026-03-27`
- requested by: `human bootstrap directive`
- issue: `需要在项目开发前先冻结 Stage 1 的问题定义、issue 拆分与执行边界`
- proposed change: `将 Stage 1 固定为 strong baseline 问题成立性验证，不纳入 M1 / M2`
- decision: `accepted and frozen`
- rationale: `当前仓库尚处于 docs-first bootstrap，先建立硬边界比提前写方法更重要`
