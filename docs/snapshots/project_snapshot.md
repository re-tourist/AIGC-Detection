# project_snapshot

## 1. Repository Overview

- Repository name: `AIGC-Detection`
- Apparent purpose: 以“strong generator-diverse baseline 上 localized editing 是否仍然结构性失败”为核心问题，先完成问题成立性验证，再决定是否进入 local branch / consistency 方法阶段。
- Repository type:
  - [ ] single-package
  - [ ] monorepo
  - [x] research repo
  - [ ] coursework repo
  - [ ] app/service repo
  - [ ] library/tooling repo
- Primary language(s): 目前已确认的主体内容是 Markdown 文档；预期后续实验代码大概率为 Python / PyTorch，但仓库内尚无可确认实现。
- Main framework(s): `needs confirmation`
- Current documentation quality:
  - [ ] strong
  - [x] usable
  - [ ] weak
  - [ ] unclear

---

## 2. Top-Level Structure

列出主要顶层目录及推测职责。

- `.agents/`
  - likely role: 本地工作流 Skills，包含 `repo-snapshot`、`draft-plan`、`milestone-review` 等 starter-kit 辅助能力。
- `.codex/`
  - likely role: 项目级 Codex 默认配置与子 agent 配置。
- `.github/`
  - likely role: PR 模板；当前未发现 CI workflow。
- `docs/`
  - likely role: 当前最核心目录，包含实验启动文档、starter-kit 模板、workflow 说明。
- `prompts/`
  - likely role: 用于生成 `AGENTS.md`、`PROJECT_CONTEXT.md`、stage plan / issue / review 的提示词。
- `templates/`
  - likely role: task brief、PR、issue report、milestone review 等模板。
- `src/`
  - likely role: 预留源码目录；当前为空。
- `scripts/`
  - likely role: 预留训练/评估脚本目录；当前为空。
- `data/`
  - likely role: 预留数据目录；当前为空。
- `outputs/`
  - likely role: 预留实验产物目录；当前为空。

同时标记：
- 高频代码区：当前未发现已落地代码区，后续大概率为 `src/` 与 `scripts/`。
- 高频文档区：`docs/`、`prompts/`、`templates/`
- 不应轻易改动的稳定区：根级 `AGENTS.md`、`.codex/`、`docs/contracts/`、`docs/plan/`

---

## 3. Key Entry Points

列出理解项目最值得先读的入口。

### Runtime / App entrypoints
- unknown / needs confirmation

### Training / Experiment entrypoints
- unknown / needs confirmation

### Inference / Evaluation entrypoints
- unknown / needs confirmation

### Main configs
- `.codex/config.toml`
- `.codex/agents/implementer.toml`
- `.codex/agents/reviewer.toml`

### Main docs
- `AGENTS.md`
- `docs/experiment_background.md`
- `docs/localized_failure_on_strong_baseline_protocol.md`
- `docs/实验开展先决条件分析.md`
- `docs/ai/WORKFLOW_GUIDE.md`
- `docs/ai/PROJECT_CONTEXT.md`
- `docs/plan/plan_stage1_problem_validation.md`
- `docs/plan/issue_stage1_problem_validation.md`
- `docs/contracts/contract_freeze_stage1_problem_validation.md`

如果无法确认，请标注：
- 当前未发现任何已实现训练脚本、模型入口、评估入口。

---

## 4. Tooling Signals

### Dependency / package manager
- signal: 未发现 `requirements.txt`、`pyproject.toml`、`environment.yml`、`package.json`
- file(s): none confirmed

### Build system
- signal: 未发现
- file(s): none confirmed

### Lint / format
- signal: 未发现
- file(s): none confirmed

### Type checking
- signal: 未发现
- file(s): none confirmed

### Test framework
- signal: 未发现
- file(s): none confirmed

### CI / GitHub Actions
- signal: 仅发现 PR 模板，未发现 GitHub Actions workflow
- file(s): `.github/pull_request_template.md`

### Docker / environment / devcontainer
- signal: 未发现
- file(s): none confirmed

---

## 5. Validation Signals

列出仓库中实际能确认的验证入口。

### Install
- not clearly discoverable

### Run
- not clearly discoverable

### Test
- not clearly discoverable

### Lint
- not clearly discoverable

### Build
- not clearly discoverable

### Focused / local checks
- 当前唯一可确认的窄验证是文档一致性检查、路径存在性检查、后续配置/数据清单 smoke check。

如果没有明确命令，请写：
- 目前项目仍处于 docs-first bootstrap 状态，正式验证命令需在 Stage 1 实现时建立。

---

## 6. Risk Zones

列出敏感区。

### Sensitive directories/files
- `AGENTS.md`
- `.codex/config.toml`
- `.codex/agents/*.toml`
- `docs/contracts/`
- `docs/plan/`

### Potentially generated files
- `outputs/` 下未来的实验结果、日志、checkpoint、summary

### Infra / deployment / secrets-related areas
- 当前未发现 secrets 或 deployment 文件

### Public interfaces / schemas / stable outputs
- Stage 1 冻结后应稳定的实验组命名：`B0` / `B1` / `B1-diverse`
- Stage 1 冻结后应稳定的评测含义：full-image clean / unseen / degraded，localized clean / degraded 与 slice 定义
- 后续应稳定的输出物类型：config snapshot、metrics summary、result tables、closeout doc

### Places where small edits could have repo-wide impact
- `docs/contracts/contract_freeze_stage1_problem_validation.md`
- `docs/ai/PROJECT_CONTEXT.md`
- `docs/plan/plan_stage1_problem_validation.md`
- `docs/plan/issue_stage1_problem_validation.md`

---

## 7. Documentation State

### Existing docs
- `README.md`: 只有仓库标题，几乎不提供执行上下文。
- `AGENTS.md`: 已有 durable repo-level working rules，可直接作为 agent 执行边界。
- `docs/...`: 已有三份实验启动文档与 starter-kit 模板/指南，是当前最主要的信息来源。
- other relevant docs:
  - `.github/pull_request_template.md`
  - `prompts/*.prompt.md`
  - `templates/*.md`

### Likely missing docs
- [ ] AGENTS.md
- [ ] PROJECT_CONTEXT.md
- [ ] stage plan
- [ ] issue breakdown
- [ ] review checklist
- [ ] contract freeze
- [x] closeout doc

### Suspected stale docs
- `docs/gitflow/issue_stage1.md`: 更像早期 milestone 草案，当前不应作为 Stage 1 的唯一权威拆分依据。

---

## 8. Working Recommendations

根据当前 repo 状态，建议 agent：

### Read first
- `AGENTS.md`
- `docs/experiment_background.md`
- `docs/localized_failure_on_strong_baseline_protocol.md`
- `docs/实验开展先决条件分析.md`
- `docs/ai/PROJECT_CONTEXT.md`
- `docs/contracts/contract_freeze_stage1_problem_validation.md`

### Avoid touching casually
- `.codex/`
- 根级 `AGENTS.md`
- `docs/contracts/`
- `docs/plan/`

### Validate first
- 任何新建配置或脚本先做路径/参数/dry-run 级别验证
- 任何重训练命令先单独整理并移交 Linux 服务器执行，不要在当前 Windows 工作机上默认重跑

### Document before coding if missing
- baseline 来源与 checkpoint 选型
- 数据集清单、split 与 slice 元信息来源
- 训练/评估命令与产物目录约定

---

## 9. Open Uncertainties

列出无法从 repo 本身确认的事实。

- uncertainty 1: Stage 1 将复用的具体 backbone、官方 reference repo、checkpoint 来源尚未在仓库中落地。
- uncertainty 2: full-image fake / localized edit 数据集的具体名称、路径、授权状态与现成 split 尚未在仓库中声明。
- uncertainty 3: 未来训练与评估的 Python 环境、依赖管理方式、Linux 服务器运行约定尚未写入仓库。
- uncertainty 4: `docs/gitflow/issue_stage1.md` 是否只是旧草案、是否已有人工确认版本，仓库内暂无明确标识。

这部分要严格区分于已确认事实。
