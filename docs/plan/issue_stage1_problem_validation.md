# issue_stage1

Status note:
- This file belongs to the earlier aggressive Stage 1 draft.
- It is no longer the current execution split.
- Current macro roadmap is now:
  - `M1: Data and Metric Pipeline Bootstrap`
  - `M2: Community Forensics Integration`
  - `M3: Strong Baseline Localized Failure Validation`
- A new issue split should be drafted after the new milestone docs are reviewed.

This file lists the issues for a single stage.
Each issue should be independently executable, reviewable, and closable.

---

# Issue 1.1 — Freeze Stage 1 Data/Config Manifests and Artifact Contract

## Background

Stage 1 的第一步不是先写模型，而是先把数据、配置、结果产物三件事的语义固定下来。
否则后续即使代码能跑，也很容易出现：

- baseline 组别含义漂移
- full-image 与 localized 评测混在一起
- 结果无法回溯到数据、配置与 split

## Suggested Branch

- `codex/stage1-contract-manifests`

## Goal

为 `B0` / `B1` / `B1-diverse` 建立最小可执行的数据清单、配置约定与 artifact 输出契约，
并把 Linux 服务器执行边界写清楚。

## In Scope

- [x] 定义 Stage 1 所需的数据 split / manifest 字段
- [x] 定义 baseline 组别与配置约定
- [x] 定义 outputs 下的最小 artifact 结构
- [x] 写清楚哪些命令可本地 smoke，哪些必须迁移到 Linux 服务器

## Out of Scope

- [x] 模型结构创新
- [x] 大规模训练
- [x] M1 / M2 实现

## Relevant Files / Paths

- `docs/contracts/contract_freeze_stage1_problem_validation.md`
- `docs/plan/plan_stage1_problem_validation.md`
- `data/`
- `src/`
- `scripts/`
- `outputs/`

## Constraints

Project-specific constraints:
- 不要自行决定未经确认的数据源名称、checkpoint 来源或 slice 标注规则
- 任何大计算量命令都只能整理为 runbook，不能虚报为已本地运行
- 不要改变 Stage 1 的 baseline 组别定义

## Suggested Workflow

Recommended execution order:

1. read the relevant docs and entry files
2. inspect affected modules
3. make the smallest viable change
4. run narrow validation
5. update docs/tests if needed
6. summarize changes and risks

## Done When

This issue is done when all are true:

- [x] Stage 1 配置字段和数据清单字段可被说明并加载
- [x] artifact 输出结构可被后续 issue 直接复用
- [x] 本地 smoke 与 Linux server run 的边界被写清楚

## Required Validation

Minimum evidence required:

- command / check 1:
  - 配置解析或 manifest 读取 smoke check
- command / check 2:
  - 输出目录 / 文件命名约定的写出测试
- manual sanity check:
  - 人工确认 full-image 与 localized 评测输入没有被混用
- optional broader check:
  - 真实数据路径全量扫描

## Report Format

Final report should include:

1. changed files
2. what changed in each file
3. validation run
4. known risks / limitations
5. suggested next issue

## Stop and Report If

- baseline source 或数据来源无法确认
- 需要改 Stage 1 freeze 才能表达当前数据语义
- 需要引入新依赖才能做基础配置加载

---

# Issue 1.2 — Implement B0 / B1 / B1-diverse Baseline Pipeline

## Background

Stage 1 要先站住 strong baseline，而不是先做方法模块。
当前仓库 `src/` 与 `scripts/` 为空，因此需要在冻结边界内建立最小训练/评测骨架，
并保证 `B1-diverse` 相对 `B1` 的核心差异只来自 generator diversity。

## Suggested Branch

- `codex/stage1-baseline-pipeline`

## Goal

实现可复用的 baseline 训练与推理闭环，支持 `B0`、`B1`、`B1-diverse` 三组模型。

## In Scope

- [x] baseline model build
- [x] feature extraction / probe 连接
- [x] train / val / test 基础闭环
- [x] checkpoint 与 summary 写出

## Out of Scope

- [x] M1 / M2
- [x] localized 特定模块创新
- [x] 额外 benchmark 扩张

## Relevant Files / Paths

- `src/`
- `scripts/`
- `outputs/`
- `docs/contracts/contract_freeze_stage1_problem_validation.md`

## Constraints

Project-specific constraints:
- 不要通过“顺手改 backbone / 头结构 / 数据比率”来掩盖 generator diversity 的控制变量
- 不要为了快而写一次性旁路脚本，优先形成能复用到后续 issue 的正式入口
- 大计算量训练命令应整理后交给 Linux 服务器

## Suggested Workflow

Recommended execution order:

1. read the relevant docs and entry files
2. inspect affected modules
3. make the smallest viable change
4. run narrow validation
5. update docs/tests if needed
6. summarize changes and risks

## Done When

This issue is done when all are true:

- [x] `B0` / `B1` / `B1-diverse` 能通过统一入口构建
- [x] 至少能完成 toy / smoke 级别的 train-eval 闭环
- [x] 输出物可被后续 qualification 与 localized eval issue 复用

## Required Validation

Minimum evidence required:

- command / check 1:
  - dummy / toy data forward smoke check
- command / check 2:
  - 小规模 train-eval smoke run
- manual sanity check:
  - `B1-diverse` 与 `B1` 的差异只来自 generator diversity 相关配置
- optional broader check:
  - 单 seed first-pass baseline run

## Report Format

Final report should include:

1. changed files
2. what changed in each file
3. validation run
4. known risks / limitations
5. suggested next issue

## Stop and Report If

- baseline reference 实现无法接入
- 为了跑通 pipeline 必须改变 Stage 1 baseline 语义
- 需要未经批准的新依赖或大规模目录重构

---

# Issue 1.3 — Implement Strong Baseline Qualification Evaluation

## Background

如果不能先证明 `B1-diverse` 在 full-image image-level detection 上比 `B1` 更像一个 strong baseline，
那后续所有 “localized failure” 结论都会被怀疑只是 baseline 太弱。

## Suggested Branch

- `codex/stage1-global-qualification`

## Goal

建立 full-image clean / unseen / degraded 评测与汇总流程，输出 Stage 1 的 baseline qualification 结果。

## In Scope

- [x] checkpoint 加载与 inference
- [x] AUROC / AUPR(or AP) / Accuracy / fake recall 等基础指标
- [x] clean / unseen / degraded 维度上的结果汇总
- [x] Table 1 风格报表

## Out of Scope

- [x] localized slice 评测
- [x] M1 / M2
- [x] 大规模 parameter / data ablation

## Relevant Files / Paths

- `src/`
- `scripts/`
- `outputs/`
- `docs/localized_failure_on_strong_baseline_protocol.md`

## Constraints

Project-specific constraints:
- 不要只报一个 overall accuracy
- 不要在看到结果后再临时改 unseen / degraded 的口径
- 指标、阈值、数据 split 含义必须能回溯

## Suggested Workflow

Recommended execution order:

1. read the relevant docs and entry files
2. inspect affected modules
3. make the smallest viable change
4. run narrow validation
5. update docs/tests if needed
6. summarize changes and risks

## Done When

This issue is done when all are true:

- [x] 可独立运行 baseline qualification eval
- [x] 输出 clean / unseen / degraded 结果表
- [x] 能明确判断 strong baseline 是否被站稳

## Required Validation

Minimum evidence required:

- command / check 1:
  - metric 计算 sanity check
- command / check 2:
  - inference summary 写出检查
- manual sanity check:
  - `B1-diverse` 相比 `B1` 的改动没有越过 contract
- optional broader check:
  - first-pass unseen / degraded 评测

## Report Format

Final report should include:

1. changed files
2. what changed in each file
3. validation run
4. known risks / limitations
5. suggested next issue

## Stop and Report If

- 指标口径与协议文档冲突
- unseen / degraded 数据定义在实现时变得不可确认
- 需要改变 contract 才能解释当前评测输出

---

# Issue 1.4 — Implement Localized Clean / Degraded Slice Evaluation

## Background

Stage 1 最关键的不是把 full-image fake 做得多高，而是验证“强 global baseline 仍然会在 localized edit 上结构性掉分”。
这要求 localized evaluation 不是一个总分脚本，而是能分解到 area / subtlety / region / degradation 的 slice 评测器。

## Suggested Branch

- `codex/stage1-localized-slices`

## Goal

实现 localized clean / degraded 与 slice 级评测流程，输出足以支撑 H2 的结构化结果。

## In Scope

- [x] localized overall eval
- [x] small / medium / large slice
- [x] subtle / obvious slice
- [x] object / background slice
- [x] degraded localized eval 与结果汇总

## Out of Scope

- [x] local branch / consistency 的任何实现
- [x] 修改 localized slice 语义
- [x] 新 benchmark 设计

## Relevant Files / Paths

- `src/`
- `scripts/`
- `outputs/`
- `docs/localized_failure_on_strong_baseline_protocol.md`
- `docs/contracts/contract_freeze_stage1_problem_validation.md`

## Constraints

Project-specific constraints:
- localized eval 必须与 full-image eval 语义分开
- slice bucket 定义要么来自现成标注，要么来自可解释的固定规则；不能事后为结果调 bucket
- 不要在这个 issue 中偷偷引入方法模块

## Suggested Workflow

Recommended execution order:

1. read the relevant docs and entry files
2. inspect affected modules
3. make the smallest viable change
4. run narrow validation
5. update docs/tests if needed
6. summarize changes and risks

## Done When

This issue is done when all are true:

- [x] localized overall 与 slice 级结果可输出
- [x] clean / degraded localized 被分开汇报
- [x] 结果能够支持“哪里掉、为什么掉”的分析，而不只是总分

## Required Validation

Minimum evidence required:

- command / check 1:
  - slice bucket 统计 sanity check
- command / check 2:
  - localized eval smoke run
- manual sanity check:
  - small / subtle / background / degraded slice 计数和样例抽查
- optional broader check:
  - edit area ratio vs score 图的 first-pass 生成

## Report Format

Final report should include:

1. changed files
2. what changed in each file
3. validation run
4. known risks / limitations
5. suggested next issue

## Stop and Report If

- 缺少生成 slice 所需的关键标注
- degraded localized 数据定义不清
- 继续推进需要改变 split protocol 或 localized 评测语义

---

# Issue 1.5 — Run First-Pass Stage 1 Experiments and Write Closeout

## Background

Stage 1 不是“代码凑齐就算结束”。
它必须产出第一轮 evidence package，让后续能判断：

- strong baseline 是否真的站住
- localized failure 是否够结构化
- 是否值得进入 Stage 2 的 M1 / M2

## Suggested Branch

- `codex/stage1-problem-validation-runs`

## Goal

完成第一轮 B0 / B1 / B1-diverse 实验运行、整理结果、写出 closeout 与下一阶段入口说明。

## In Scope

- [x] first-pass baseline runs
- [x] full-image qualification result summary
- [x] localized failure result summary
- [x] stage closeout draft

## Out of Scope

- [x] 继续扩展为方法阶段
- [x] 结果不好就临时改 protocol
- [x] 未经批准的更多数据 / 更多参数控制实验

## Relevant Files / Paths

- `scripts/`
- `outputs/`
- `docs/handoff/`
- `docs/plan/plan_stage1_problem_validation.md`

## Constraints

Project-specific constraints:
- 只汇报“实际运行过”的结果
- Linux 服务器上执行的命令、配置、artifact 路径必须被明确记录
- closeout 里必须明确哪些没验证、哪些只是 first-pass

## Suggested Workflow

Recommended execution order:

1. read the relevant docs and entry files
2. inspect affected modules
3. make the smallest viable change
4. run narrow validation
5. update docs/tests if needed
6. summarize changes and risks

## Done When

This issue is done when all are true:

- [x] 有一轮可回溯的 Stage 1 baseline 结果
- [x] closeout 文档能清楚说明已完成、未完成与风险
- [x] 下一步是否进入 Stage 2 有明确输入

## Required Validation

Minimum evidence required:

- command / check 1:
  - 实际训练 / 评测命令记录
- command / check 2:
  - artifact 存在性检查
- manual sanity check:
  - result table、配置与输出目录可互相回溯
- optional broader check:
  - 第二 seed 或额外数据切片验证

## Report Format

Final report should include:

1. changed files
2. what changed in each file
3. validation run
4. known risks / limitations
5. suggested next issue

## Stop and Report If

- first-pass run 已显示 contract 前提不成立
- 结果解释必须依赖改 protocol 才能继续
- artifact 不足以回溯命令、配置与数据口径
