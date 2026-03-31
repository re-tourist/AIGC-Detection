# PROJECT_CONTEXT

## 1. Project Summary

- Project name: `AIGC-Detection`
- Project type:
  - [x] research
  - [ ] product
  - [ ] coursework
  - [x] prototype
  - [ ] infrastructure
- One-sentence description:
  - 该项目当前聚焦于验证一个问题命题：在 strong generator-diverse baseline 已经成立的前提下，localized editing 是否仍然是独立且结构性的 failure mode。
- Primary language / stack:
  - 已确认：Markdown 文档驱动工作流
  - needs human confirmation：后续实验代码栈预计为 Python / PyTorch，但仓库内尚无已确认实现

## 2. Current Phase

- Current milestone / stage:
  - 当前处于 `M1 formally closed — ready for M2 Community Forensics integration`
- Why this stage exists:
  - 在 Community Forensics 接入和正式验证实验之前，先建立 localized evaluation 所需的最小 data pipeline 和 metric pipeline。
- What this stage should prove or deliver:
  - 已产出 manifest-driven local mirror loader、normalized sample objects、minimal metric core 和最小 artifact 输出路径，但尚未对真实 mirrored subset 做复核。
- What is explicitly out of scope in this stage:
  - 不接入 Community Forensics
  - 不开始正式 localized failure validation
  - 不做大规模服务器运行
  - 不实现 local branch / deployment-aware consistency

## 3. High-Level Goal

本项目的高层目标不是简单做一个新的 detector，而是先建立一条更硬的研究叙事：
先证明 strong generator-diverse baseline 在 global image-level AIGI detection 上已经足够强，
再证明它在 localized editing 尤其 small / subtle / background / degraded 场景下仍存在结构性失败。
如果这条证据链成立，后续 local evidence aggregation 与 deployment-aware consistency 才具有方法正当性。

在优先级上：
- 研究有效性与实验语义正确性高于“先把代码铺开”
- 可复现性与可审查性高于局部提分
- 结构化文档与阶段边界高于临时聊天约定

## 4. Human-Owned Decisions

这些区域由人类负责，agent 不得擅自改变：

- research / product direction:
  - 是否继续沿着 “strong baseline residual localized failure -> local branch + consistency” 主线推进
- milestone boundaries:
  - Stage 1 是否只做问题成立性验证，还是吸收方法实验
- contract freeze:
  - 若需改变 Stage 1 的 task definition、split protocol、冻结边界，必须停下汇报
- evaluation criteria:
  - localized slice 的最终定义、数据源选择、结果是否足以说服导师
- release / submission decisions:
  - 是否进入导师汇报、论文写作或对外提交
- public API / external commitments:
  - 对外公开的 benchmark、脚本、结果口径

## 5. Agent-Owned Execution Scope

Agents 预期帮助完成：

- M1 contract / plan / issue docs 冻结
- local mirror data loader 与 normalized sample object 实现
- minimal metric core 与最小 evaluation runner
- issue 级报告与 milestone closeout 起草
- review 标准下的自检与结构化汇报

Agents 不应自行决定：

- 研究主线是否要改
- 失败结果是否足以否定当前假设
- 是否把 Stage 1 扩大为方法阶段
- 是否改变成功定义或评价语义

## 6. Project Constraints

Project-specific constraints:
- Constraint 1:
  - 在 M1 内，先冻结 manifest schema、metric priority、artifact contract 和 stop rules，再实现 loader / metric / runner。
- Constraint 2:
  - 大计算量训练/评估命令不要默认在当前工作机执行，必须单独整理给用户迁移到 Linux 服务器。
- Constraint 3:
  - 如果 local mirror pack、显式 slice metadata 或 derived-field rule 缺失，不要自行补齐；应 stop and report。
- Constraint 4:
  - 不要把 “problem-validation experiment” 静默扩大成方法创新阶段。
- Constraint 5:
  - `localized_edit` 是 M1 primary path；`full_image_fake` 在 M1 只是 schema compatibility path。

## 7. Success Criteria for This Phase

A phase is considered successful when:

- [x] `docs/snapshots/project_snapshot.md` 已建立并诚实描述仓库现状与缺口
- [x] `docs/ai/PROJECT_CONTEXT.md` 已明确人类决策边界与 agent 执行边界
- [x] M1 的 active plan / issue split / contract freeze / review checklist 已建立且相互一致

Optional quantitative gates:
- metric / threshold:
  - 当前阶段的最低门槛是 overall metrics 可运行并可落最小 artifact
- runtime / cost budget:
  - 当前阶段仅允许轻量文档与仓库检查
- reproducibility requirement:
  - M1 需要记录 manifest / prediction 输入和 runner 配置快照

## 8. Stop Conditions

If any of these happen, the agent should stop and report instead of pushing forward:

- Stop condition 1:
  - 需要改变 task definition / split protocol / contract freeze 才能继续
- Stop condition 2:
  - local mirror pack、manifest 所需字段、或 slice metadata 的存在性无法确认
- Stop condition 3:
  - 下一步工作必须引入未批准的新依赖、重大结构重排、或把 M1 扩成 baseline integration / formal validation

Examples:
- validation results contradict task assumptions
- required files or configs are missing
- proposed change would violate contract freeze
- implementation requires unapproved dependency or architecture change

## 9. Important Files and Docs

Core files:
- `AGENTS.md`
- `.codex/config.toml`
- `.codex/agents/implementer.toml`
- `.codex/agents/reviewer.toml`

Planning docs:
- `docs/plan/plan_stage1_data_metric_bootstrap.md`
- `docs/plan/issue_stage1_data_metric_bootstrap.md`

Contracts / review docs:
- `docs/contracts/contract_freeze_stage1_data_metric_bootstrap.md`
- `docs/review/code_review.md`

Research context docs:
- `docs/experiment_background.md`
- `docs/localized_failure_on_strong_baseline_protocol.md`
- `docs/实验开展先决条件分析.md`
- `docs/gitflow/MILESTONE_ROADMAP.md`

## 10. Reporting Preference

When reporting progress, prefer this style:

- concise factual summary
- changed files first
- validation second
- open risks last
- do not overclaim certainty
- 明确区分“已运行”“已设计但未运行”“需要 Linux 服务器执行”
