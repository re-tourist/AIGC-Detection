# issue_stage1

This file lists the issues for the active M1 stage.
Each issue should be independently executable, reviewable, and closable.

---

# Issue 1.1 — Freeze M1 data contract, manifest schema, and artifact contract

## Background

M1 的第一步必须先冻结 contract，不允许先写 loader / metric 再回头补语义。

## Suggested Branch

- `codex/stage1-data-contract`

## Goal

冻结 M1 的 active plan、issue split、contract freeze，以及 manifest schema、metric priority、artifact contract 和 stop rules。

## In Scope

- [x] active M1 plan doc
- [x] active M1 issue doc
- [x] active M1 contract
- [x] required / optional / derived field categories
- [x] metric priority
- [x] stop rules

## Out of Scope

- [x] loader implementation
- [x] metric implementation
- [x] Community Forensics integration

## Relevant Files / Paths

- `docs/ai/PROJECT_CONTEXT.md`
- `docs/plan/plan_stage1_data_metric_bootstrap.md`
- `docs/plan/issue_stage1_data_metric_bootstrap.md`
- `docs/contracts/contract_freeze_stage1_data_metric_bootstrap.md`

## Constraints

- area-ratio derivation rule 如果不冻结，就必须显式 blocked
- `localized_edit` 是 primary path
- 不允许在 contract 中留下需要实现者再自行决定的空白

## Suggested Workflow

1. read active roadmap and protocol docs
2. freeze schema / metric / stop boundaries
3. sync project context
4. check docs for consistency
5. commit and report

## Done When

- [x] active plan / issue / contract doc 完整可执行
- [x] required raw / optional raw / derived fields 已明确
- [x] metric priority 与 stop rules 已冻结

## Required Validation

- path/reference consistency check
- manual sanity check on frozen boundaries

## Report Format

1. changed files
2. what changed in each file
3. validation run
4. known risks / limitations
5. suggested next issue

## Stop and Report If

- contract 仍然存在高影响空白
- schema 需要依赖未知数据事实才能冻结

---

# Issue 1.2 — Implement local mirror loader and normalized sample object

## Background

M1 的输入是 local mirror pack，而不是全量服务器数据。

## Suggested Branch

- `codex/stage1-data-loader`

## Goal

实现 manifest-driven loader，把 local mirror samples 转成 normalized sample objects。

## In Scope

- [x] manifest parsing
- [x] required field validation
- [x] optional field parsing
- [x] normalized sample object
- [x] loader smoke tests

## Out of Scope

- [x] baseline inference
- [x] grouped metrics
- [x] full execution harness

## Relevant Files / Paths

- `src/`
- `tests/`
- `data/`
- `docs/contracts/contract_freeze_stage1_data_metric_bootstrap.md`

## Constraints

- local mirror pack 缺失时必须停下
- `full_image_fake` 只是 compatibility path
- derived fields 不得从 manifest raw 输入里偷偷混入

## Suggested Workflow

1. implement manifest schema validation
2. implement normalized sample object
3. add local fixtures and smoke tests
4. run narrow validation
5. commit and report

## Done When

- [x] localized samples 可被加载成 normalized sample objects
- [x] full_image_fake compatibility path 不报错
- [x] missing optional fields 不会导致 loader 崩溃

## Required Validation

- unit tests for required field validation
- loader smoke test on local fixtures

## Report Format

1. changed files
2. what changed in each file
3. validation run
4. known risks / limitations
5. suggested next issue

## Stop and Report If

- local mirror samples 无法进入 normalized sample object
- 实现需要发明 metadata semantics

---

# Issue 1.3 — Implement minimal metric core

## Background

M1 只需要 overall metrics 和高优先级 grouped reporting。

## Suggested Branch

- `codex/stage1-metric-core`

## Goal

实现 AUROC、Accuracy、fake_recall，以及 by task_type / by degradation 的最小 grouped reporting。

## In Scope

- [x] AUROC
- [x] Accuracy
- [x] fake_recall
- [x] by task_type
- [x] by degradation when metadata exists
- [x] blocked status for unsupported P2 dimensions

## Out of Scope

- [x] baseline scoring
- [x] full slice reporting
- [x] area-ratio derivation

## Relevant Files / Paths

- `src/`
- `tests/`
- `docs/contracts/contract_freeze_stage1_data_metric_bootstrap.md`

## Constraints

- 没有显式 metadata 就不能输出 grouped metrics
- unsupported dimensions 必须显式标注
- 不允许在 metric 层补数据语义

## Suggested Workflow

1. implement overall metrics
2. implement grouped reporting for P1 dimensions
3. emit blocked status for unsupported dimensions
4. run narrow metric tests
5. commit and report

## Done When

- [x] overall metrics 可运行
- [x] task_type grouped reporting 可运行
- [x] degradation grouped reporting 仅在 metadata 存在时运行
- [x] unsupported P2 dimensions 被显式标记

## Required Validation

- metric unit tests
- grouped reporting smoke tests

## Report Format

1. changed files
2. what changed in each file
3. validation run
4. known risks / limitations
5. suggested next issue

## Stop and Report If

- grouped reporting 需要发明 metadata semantics
- area-ratio bins 需要未冻结的 derivation rule

---

# Issue 1.4 — Implement minimal evaluation runner and artifact save path

## Background

M1 需要最小的端到端 smoke path，但不需要完整 harness。

## Suggested Branch

- `codex/stage1-minimal-eval-runner`

## Goal

实现一个最小 evaluation runner，读取 manifest + predictions，输出最小 artifact bundle。

## In Scope

- [x] runner CLI
- [x] manifest + predictions consumption
- [x] summary JSON
- [x] metrics CSV
- [x] smoke report Markdown
- [x] config snapshot

## Out of Scope

- [x] training harness
- [x] Community Forensics integration
- [x] Linux orchestration

## Relevant Files / Paths

- `scripts/`
- `src/`
- `tests/`
- `outputs/`

## Constraints

- runner 不能依赖全量数据存在
- 只能消费 normalized samples 和 external predictions
- 不能把 M1 扩成完整 execution framework

## Suggested Workflow

1. implement minimal runner
2. wire artifact outputs
3. add smoke fixture predictions
4. run runner tests
5. commit and report

## Done When

- [x] runner 可端到端写出最小 outputs
- [x] output 包含 provenance
- [x] local smoke path 可复现

## Required Validation

- runner smoke test
- output existence and content checks

## Report Format

1. changed files
2. what changed in each file
3. validation run
4. known risks / limitations
5. suggested next issue

## Stop and Report If

- runner 需要隐式假设全量数据或 baseline inference 已存在
- output 语义无法与 contract 对齐

---

# Issue 1.5 — Review and milestone closeout

## Background

M1 结束时必须明确哪些能力已建立，哪些仍 blocked。

## Suggested Branch

- `codex/stage1-closeout`

## Goal

完成 M1 review 和 milestone closeout，形成 M2 handoff。

## In Scope

- [x] self-review against `docs/review/code_review.md`
- [x] milestone closeout
- [x] blocked items summary
- [x] M2 handoff

## Out of Scope

- [x] M2 implementation
- [x] 追加 M1 scope

## Relevant Files / Paths

- `docs/review/`
- `docs/handoff/`
- `docs/contracts/contract_freeze_stage1_data_metric_bootstrap.md`

## Constraints

- 不把 blocked items 写成已解决
- 不把 smoke 结果写成正式验证结果

## Suggested Workflow

1. review scope / contract / validation evidence
2. write milestone closeout
3. summarize blocked items and handoff
4. commit and report

## Done When

- [x] review 结论明确
- [x] closeout 可供下一阶段直接阅读
- [x] M2 handoff assumptions 已写清楚

## Required Validation

- review checklist pass
- closeout completeness check

## Report Format

1. changed files
2. what changed in each file
3. validation run
4. known risks / limitations
5. suggested next issue

## Stop and Report If

- review 发现 P0/P1 contract or validation issue
- closeout 仍然无法明确 M2 可以依赖什么
