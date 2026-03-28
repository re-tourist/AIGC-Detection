# GITHUB_OPERATIONS

## Purpose

This document defines how this repository maps local execution docs to GitHub milestones, issues, branches, commits, and PRs.

它的目标是让 Codex 与 GitHub 的协作有稳定格式，而不是每次手工重新约定。

---

## 1. Source of Truth

GitHub 相关事项以仓库内文档为准：

- milestone docs: `docs/gitflow/milestones/*`
- issue docs: `docs/gitflow/issues/*`
- stage planning docs: `docs/plan/*`
- frozen boundaries: `docs/contracts/*`
- PR template: `.github/pull_request_template.md`

规则：

- 先有 repo 内文档，再把内容同步到 GitHub
- GitHub issue / milestone 应尽量与 repo 文档一一对应
- 如果 GitHub 内容与 repo 文档冲突，以 repo 文档为准并补同步

---

## 2. Milestone Naming

Milestone title format:

```text
M<number>: <short milestone name>
```

Examples:

- `M0: Project Bootstrap`
- `M1: Data and Metric Pipeline Bootstrap`
- `M2: Community Forensics Integration`
- `M3: Strong Baseline Localized Failure Validation`

Milestone description should contain:

1. Goal
2. In Scope
3. Out of Scope
4. Exit Criteria
5. Linked issue set

Milestone docs should live under:

- `docs/gitflow/milestones/`

---

## 3. Issue Naming

Issue title format:

```text
Issue <stage.issue> — <action-oriented title>
```

Examples:

- `Issue 1.1 — Freeze Stage 1 data/config manifests and artifact contract`
- `Issue 1.4 — Implement localized clean / degraded slice evaluation`

Issue docs should live under:

- `docs/gitflow/issues/stage<stage>/`

---

## 4. Issue Body Format

GitHub issue body uses this fixed section order:

1. `Background`
2. `Suggested Branch`
3. `Goal`
4. `Tasks`
5. `Resource Boundary`
6. `Non-Goals`
7. `Deliverable`
8. `Acceptance`

This is the preferred GitHub-facing format because it is:

- shorter than the full stage template
- explicit enough for Codex execution
- easy for reviewers and humans to scan

If extra context is needed, keep it short and place it inside `Background` or `Resource Boundary`.

---

## 5. Branch Mapping

Suggested branch naming rule:

```text
codex/stage<stage>-<short-slug>
```

Examples:

- `codex/stage1-contract-manifests`
- `codex/stage1-baseline-pipeline`
- `codex/stage1-localized-slices`

Rules:

- always keep the `codex/` prefix
- one issue should have one primary working branch
- do not reuse a closed issue branch for a different scope

---

## 6. Commit Format

Each commit should be issue-scoped and use this format:

```text
<type>(<scope> | stage<issue-id>): <short summary>
why:
- ...
- ...

what:
- ...
- ...
```

Example:

```text
feat(train | stage5-9): run paper-aligned smoke training
why:
- validate that the frozen stage5 paper-path can train end to end under a
- small smoke-only budget before main-run work, and record stability plus
- artifact completeness without confusing smoke with final results

what:
- add a dedicated stage5 smoke config, execute an L=5 smoke training run,
- record checkpoints, history, previews, and a smoke report, and attach
- post-run regular eval and blind eval evidence using the existing stage5 paths
```

Recommended `type` values:

- `feat`
- `fix`
- `docs`
- `refactor`
- `chore`
- `review`

Recommended `scope` values for this repo:

- `gitflow`
- `docs`
- `data`
- `train`
- `eval`
- `config`
- `artifacts`

Rules:

- one commit should map cleanly to one issue-sized step
- do not hide unrelated cleanup in the same commit
- `why` explains motivation and frozen-boundary context
- `what` explains concrete repo changes and produced evidence

---

## 7. PR Mapping

PRs should reference:

- one primary issue
- one milestone
- the relevant contract / plan docs

Use `.github/pull_request_template.md`.

Preferred PR rule:

- one issue -> one PR

Allowed exception:

- one issue -> multiple small commits in one PR, if all remain within the same frozen issue scope

Do not:

- combine unrelated issues into one PR
- open a PR before the issue-level validation evidence is ready

---

## 8. Execution Order

For normal GitHub-driven work, use this order:

1. confirm milestone doc exists
2. confirm issue doc exists
3. create milestone on GitHub
4. create issue on GitHub from the issue doc
5. create/switch branch for that issue
6. implement and validate within issue boundary
7. commit using the commit format above
8. open PR referencing the issue and milestone
9. review against `docs/review/code_review.md`

---

## 9. Sync Rule

Whenever a GitHub milestone or issue is created or materially edited:

- update the matching repo doc if the GitHub body changed meaning
- record issue number / URL back into the repo issue index when practical

Do not let GitHub become the only place where execution scope exists.
