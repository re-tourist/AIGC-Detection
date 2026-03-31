# Issue 1.5 — Run first-pass Stage 1 experiments and write closeout

## Background

Stage 1 不能停在“代码已经接好”。
它必须产出第一轮 evidence package，回答 strong baseline 是否站住、localized failure 是否结构化、
以及 Stage 2 是否值得进入。

## Suggested Branch

`codex/stage1-problem-validation-runs`

## Goal

完成第一轮 `B0` / `B1` / `B1-diverse` 运行、整理结果，
并写出能支撑下一阶段决策的 closeout。

## Tasks

- 运行 first-pass baseline experiments
- 汇总 full-image qualification results
- 汇总 localized failure results
- 写出 Stage 1 closeout draft

## Resource Boundary

- 必须清楚区分 smoke-only、first-pass、main-run 三种执行状态
- Linux 服务器上执行的命令、配置和 artifact 路径必须被记录
- 如果资源限制挡住 full-budget run，要把它写成资源约束，不要埋成实现细节

## Non-Goals

- 不在这里扩展为方法阶段
- 不因为结果不理想就临时改 protocol
- 不在本 issue 里加更多未冻结的控制实验

## Deliverable

- first-pass Stage 1 结果产物
- qualification / localized failure 汇总
- `docs/handoff/milestone_closeout_stage1_problem_validation.md`

## Acceptance

- 有一轮可回溯的 Stage 1 baseline 结果
- closeout 清楚说明已完成、未完成与风险
- 是否进入 Stage 2 有明确书面输入
