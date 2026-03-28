# plan_stage1

Status note:
- This file is an earlier aggressive Stage 1 draft.
- It should not be used as the current execution entry.
- Current macro milestone planning has been reset to:
  - `M1: Data and Metric Pipeline Bootstrap`
  - `M2: Community Forensics Integration`
  - `M3: Strong Baseline Localized Failure Validation`
- Until the new issue split is drafted, treat this file as archived planning context only.

## Stage Title

- Stage ID: `stage1_problem_validation`
- Stage name: `Strong Generator-Diverse Baseline Problem Validation`
- Suggested branch family: `codex/stage1-*`
- Status:
  - [ ] draft
  - [ ] active
  - [x] frozen
  - [ ] complete

---

## 1. Background

当前仓库已经有三份关键启动文档：

- `docs/experiment_background.md`
- `docs/localized_failure_on_strong_baseline_protocol.md`
- `docs/实验开展先决条件分析.md`

它们共同把当前研究切口收敛到一个更硬的问题：

> 在 strong generator-diverse baseline 已经成立的前提下，localized editing 是否仍然是独立且结构性的 failure mode。

这意味着 Stage 1 的职责不是直接推进方法创新，而是先完成一轮“问题成立性验证”。
只有在强 baseline 先被站稳、其 localized failure 被结构化暴露之后，后续 M1 / M2 才有充分正当性。

此外，当前仓库尚未形成可执行训练/评估入口，因此 Stage 1 既是第一轮实验实现，也是第一轮实验工程定型。

---

## 2. Goal

在不引入 local branch / consistency 方法模块的前提下，建立并验证 `B0 / B1 / B1-diverse`，
完成 full-image global qualification 与 localized clean / degraded slice evaluation，
并产出足以支持或反驳 H1 / H2 的第一轮证据。

---

## 3. In Scope

- [x] 建立 Stage 1 所需的 baseline 组别定义与对应实现边界：`B0` / `B1` / `B1-diverse`
- [x] 建立 full-image fake 与 localized edit 两类评测输入的配置、清单或 manifest 约定
- [x] 实现 strong baseline qualification 所需的全图评测流程
- [x] 实现 localized clean / degraded 及 slice 级评测流程
- [x] 产出第一轮结果表、图、artifact 目录约定与 stage closeout

---

## 4. Out of Scope

- [x] 实现 `M1 = local evidence aggregation / local branch`
- [x] 实现 `M2 = deployment-aware consistency`
- [x] 大范围 benchmark 扩写、论文正文撰写或最终 submission packaging
- [x] 因为结果不理想而临时重写 task definition、slice 含义或评测口径
- [x] 未经批准的新依赖与重大目录重构

---

## 5. Inputs and Dependencies

Required upstream inputs:

- docs:
  - `AGENTS.md`
  - `docs/ai/PROJECT_CONTEXT.md`
  - `docs/localized_failure_on_strong_baseline_protocol.md`
  - `docs/contracts/contract_freeze_stage1_problem_validation.md`
- configs:
  - `.codex/config.toml`
  - future experiment config files under `src/` / `scripts/` or dedicated config directory
- code modules:
  - `src/` and `scripts/` currently empty; Stage 1 需在冻结边界内建立最小训练/评测入口
- datasets / assets:
  - full-image real/fake 数据
  - localized edit clean / degraded 数据
  - slice 所需的面积、subtlety、语义区域元信息或其可推导信号
- previous milestone outputs:
  - 本轮 bootstrap 文档

Blocking dependencies:
- 基线 reference 实现、backbone、checkpoint 来源尚未在仓库内固化
- 数据集清单、访问路径与授权状态尚未在仓库内固化
- 大计算量训练/评测需要迁移到 Linux 服务器执行

---

## 6. Proposed Issue Breakdown

### Issue 1.1
- Title: `Freeze Stage 1 data/config manifests and artifact contract`
- Goal: 把 baseline 组别、数据 split、输出物结构与 server handoff 规则落成可执行配置边界
- Main files / directories:
  - `docs/contracts/`
  - `src/`
  - `scripts/`
  - `data/`
  - `outputs/`
- Expected output:
  - 最小可加载配置
  - 数据清单或 manifest 约定
  - artifact 命名与输出目录约定

### Issue 1.2
- Title: `Implement B0 / B1 / B1-diverse baseline pipeline`
- Goal: 在统一工程内跑通 baseline 训练与推理闭环
- Main files / directories:
  - `src/`
  - `scripts/`
  - `outputs/`
- Expected output:
  - baseline 模型构建、训练、推理与 checkpoint 保存

### Issue 1.3
- Title: `Implement strong baseline qualification evaluation`
- Goal: 建立 full-image clean / unseen / degraded 的评测与汇总
- Main files / directories:
  - `src/`
  - `scripts/`
  - `outputs/`
  - `docs/`
- Expected output:
  - Table 1 风格的 baseline qualification 汇总

### Issue 1.4
- Title: `Implement localized clean / degraded slice evaluation`
- Goal: 建立 localized editing 的 overall + slice 级评测与可视化
- Main files / directories:
  - `src/`
  - `scripts/`
  - `outputs/`
  - `docs/`
- Expected output:
  - localized failure 报表
  - edit area ratio / slice 分析图

### Issue 1.5
- Title: `Run first-pass Stage 1 experiments and write closeout`
- Goal: 完成第一轮 B0 / B1 / B1-diverse 运行、记录结果与已知风险
- Main files / directories:
  - `scripts/`
  - `outputs/`
  - `docs/handoff/`
- Expected output:
  - 第一轮结果产物
  - Stage 1 closeout 草案
  - Stage 2 是否值得进入的判断输入

---

## 7. Deliverables

At the end of this stage, the repository should contain:

- [x] B0 / B1 / B1-diverse 的最小可运行训练与评测入口
- [x] full-image qualification 与 localized slice evaluation 的结果汇总
- [x] 至少一份可回溯的 Stage 1 result summary / closeout

---

## 8. Acceptance Criteria

This stage is accepted only if:

- [x] `B0` / `B1` / `B1-diverse` 的定义、配置与 artifact 能被明确区分并回溯
- [x] 同一套仓库流程能够输出 full-image baseline qualification 结果与 localized slice 结果
- [x] 最终汇报能明确回答“强 baseline 是否仍保留结构性 localized failure”，即使答案是否定的

---

## 9. Validation Plan

Minimum validation for this stage:

- local checks:
  - 配置加载与路径解析 smoke check
  - 数据清单与 split 一致性检查
  - baseline forward / eval dry-run
- focused tests:
  - metric 计算 sanity check
  - localized slice bucket 统计 sanity check
  - artifact 写出与回读检查
- manual sanity checks:
  - 确认 `B1-diverse` 与 `B1` 的核心差异只来自 generator diversity
  - 确认 Stage 1 没有引入 M1 / M2
  - 确认 heavy training/eval 命令已单列给 Linux 服务器，而不是误报为本地已跑
- optional full-suite checks:
  - 多 seed 或更广泛 ablation
  - 更完整的 degraded robustness sweep

---

## 10. Risks

Main risks in this stage:

- Risk 1:
  - strong baseline 参考实现、checkpoint 或数据来源不清，导致 Stage 1 一开始就无法保持“强 baseline”前提
- Risk 2:
  - localized 数据若没有足够 slice 元信息，结果会退化成模糊 overall 分数，无法支撑机制叙事
- Risk 3:
  - Stage 1 很容易被“顺手开始做 local branch / consistency”的冲动拖出冻结边界
- Risk 4:
  - 当前仓库没有任何既有代码，Stage 1 既要立工程骨架又要出结果，节奏上容易失控

---

## 11. Stop Conditions

If any of these happen, stop and report:

- 无法确认 backbone / checkpoint / baseline source，导致 `B1-diverse` 的“强 baseline”含义无法成立
- localized 数据与 slice 定义不足以支持 small / subtle / background / degraded 分层
- 继续推进必须改动 Stage 1 contract freeze
- 继续推进必须把 Stage 1 扩大为方法阶段

---

## 12. Handoff Note

At stage close, produce or update:

- closeout summary:
  - `docs/handoff/milestone_closeout_stage1_problem_validation.md`
- key changed files:
  - baseline pipeline、评测脚本、配置与结果文档
- open problems:
  - 是否已充分建立 strong baseline
  - localized failure 是否足够结构化
  - 是否值得进入 M1 / M2
- suggested next stage entry point:
  - 若 Stage 1 成立，进入 `Stage 2 — Module-to-failure-mode validation`
