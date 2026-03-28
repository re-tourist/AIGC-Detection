# plan_stage1

## Stage Title

- Stage ID: `stage1_data_metric_bootstrap`
- Stage name: `Data and Metric Pipeline Bootstrap`
- Suggested branch family: `codex/stage1-*`
- Status:
  - [ ] draft
  - [x] active
  - [x] frozen
  - [ ] complete

---

## 1. Background

当前项目几乎没有任何可执行实验基础设施。
在 Community Forensics 接入和正式 localized failure validation 之前，必须先建立一个最小但语义清晰的 data / metric substrate。

本阶段不解决 baseline integration，也不解决 formal validation。
它只负责把后续实验会依赖的底层数据契约、manifest loader、minimal metrics 和最小 artifact 输出搭起来。

---

## 2. Goal

建立 manifest-driven 的 local mirror data loader、normalized sample object、minimal metric core 和 minimal evaluation runner，
使 localized failure validation 在本地小样本上具备可验证、可回溯、可落盘的基础能力。

---

## 3. In Scope

- [x] active M1 plan / issue split / contract freeze
- [x] local mirror manifest schema
- [x] normalized sample object
- [x] minimal metric core
- [x] minimal evaluation runner
- [x] minimal artifact save path
- [x] 小样本 smoke validation

---

## 4. Out of Scope

- [x] Community Forensics integration
- [x] 正式 localized failure validation
- [x] 大规模 Linux 服务器运行
- [x] local branch / deployment-aware consistency
- [x] 任何需要发明 metadata 语义的逻辑

---

## 5. Inputs and Dependencies

Required upstream inputs:

- docs:
  - `AGENTS.md`
  - `docs/ai/PROJECT_CONTEXT.md`
  - `docs/gitflow/MILESTONE_ROADMAP.md`
  - `docs/localized_failure_on_strong_baseline_protocol.md`
  - `docs/contracts/contract_freeze_stage1_data_metric_bootstrap.md`
- data:
  - 来自 Linux 服务器的 local mirror pack
  - 至少包括目录结构、少量样本、manifest 所需显式字段
- code modules:
  - `src/`
  - `scripts/`
  - `tests/`

Blocking dependencies:
- local mirror pack 缺失
- manifest 所需 required raw fields 缺失
- 要求实现 grouped reporting 的 metadata 在样本中并不存在

---

## 6. Proposed Issue Breakdown

### Issue 1.1
- Title: `Freeze M1 data contract, manifest schema, and artifact contract`
- Goal: 冻结 active plan / issue split / contract，以及 required raw / optional raw / derived fields、metric priority、artifact contract、stop rules
- Main files / directories:
  - `docs/plan/`
  - `docs/contracts/`
  - `docs/ai/`
- Expected output:
  - 可执行的 M1 语义边界

### Issue 1.2
- Title: `Implement local mirror loader and normalized sample object`
- Goal: 读取 manifest，校验字段，输出 normalized sample object
- Main files / directories:
  - `src/`
  - `tests/`
  - `data/`
- Expected output:
  - loader + normalized sample object + loader smoke test

### Issue 1.3
- Title: `Implement minimal metric core`
- Goal: 实现 overall metrics 和高优先级 grouped reporting
- Main files / directories:
  - `src/`
  - `tests/`
- Expected output:
  - metric core + grouped reporting + blocked status for unsupported dimensions

### Issue 1.4
- Title: `Implement minimal evaluation runner and artifact save path`
- Goal: 用最小 runner 消费 normalized samples 与 predictions，并写出最小 outputs
- Main files / directories:
  - `scripts/`
  - `src/`
  - `tests/`
  - `outputs/`
- Expected output:
  - minimal runner + artifact outputs + smoke run

### Issue 1.5
- Title: `Review and milestone closeout`
- Goal: 完成 M1 review、blocked item 汇总和 M2 handoff
- Main files / directories:
  - `docs/review/`
  - `docs/handoff/`
- Expected output:
  - review note + milestone closeout

---

## 7. Deliverables

At the end of this stage, the repository should contain:

- [x] active contract-backed M1 docs
- [x] local mirror loader and normalized sample object
- [x] minimal metric core
- [x] minimal evaluation runner
- [x] JSON / CSV / Markdown / config snapshot artifact outputs
- [x] M1 closeout

---

## 8. Acceptance Criteria

This stage is accepted only if:

- [x] localized samples can be loaded into normalized sample objects
- [x] overall metrics can run on a tiny mirrored sample set
- [x] minimal outputs can be saved
- [x] unsupported grouped/slice dimensions are reported honestly rather than guessed
- [x] closeout explicitly states what remains blocked for M2 / M3

---

## 9. Validation Plan

Minimum validation for this stage:

- local checks:
  - manifest schema validation
  - loader smoke checks
  - metric smoke checks
- focused tests:
  - path resolution and required field validation
  - derived-field rejection / gating
  - runner output file generation
- manual sanity checks:
  - `localized_edit` remains the M1 primary path
  - `full_image_fake` remains compatibility-only in M1
  - no grouped reporting invents missing metadata
- optional broader checks:
  - additional local mirror samples
  - Linux server handoff rehearsal

---

## 10. Risks

Main risks in this stage:

- Risk 1:
  - local mirror pack still unavailable，导致 loader 无法进行真实 smoke validation
- Risk 2:
  - manifest 字段和实际 mirror 内容不一致，导致 normalized sample contract 失效
- Risk 3:
  - grouped metrics 被误做成“隐式推断 metadata”
- Risk 4:
  - minimal runner 被过度扩展成完整 execution harness

---

## 11. Stop Conditions

If any of these happen, stop and report:

- localized samples 不能被加载成 normalized sample objects
- normalized sample objects 已存在，但 slice metadata 不存在且实现尝试跨越合同边界去补齐
- mask 文件存在，但 area-ratio derivation rule 未冻结
- local mirror pack 缺失
- 继续推进会把 M1 扩展成 M2 或 M3

---

## 12. Handoff Note

At stage close, produce or update:

- closeout summary:
  - `docs/handoff/milestone_closeout_stage1_data_metric_bootstrap.md`
- key changed files:
  - data loader、metrics、runner、M1 active docs
- open problems:
  - Community Forensics integration 还需要哪些输入
  - 哪些 slice 维度仍然 blocked
- suggested next stage entry point:
  - `M2: Community Forensics Integration`
