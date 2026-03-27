# WORKFLOW_GUIDE

## Purpose

This document explains how to use the starter kit as a real workflow.

It is not a design document.
It is an operational guide for humans and agents.

The workflow goal is:

- keep project rules inside the repository
- let Codex execute within documented boundaries
- let reviewer do first-pass checks
- keep humans focused on high-level decisions

---

## Core Principle

Use the repository as the source of truth.

Do not rely on:
- long chat history
- repeated manual prompt rewriting
- human copy-paste of project context

Instead, keep durable context in:
- `AGENTS.md`
- `docs/ai/PROJECT_CONTEXT.md`
- `docs/plan/*`
- `docs/contracts/*`
- `docs/review/*`

---

## Role Split

### Human owns
- project goal
- milestone design
- issue acceptance
- contract freeze
- evaluation meaning
- research / product direction
- final go / no-go decisions

### Implementer owns
- scoped implementation
- narrow validation
- docs / config / test sync
- structured execution report

### Reviewer owns
- scope review
- contract review
- validation review
- semantic risk review
- structured accept / revise / stop recommendation

---

## Standard Lifecycle

### Phase 0 — Bootstrap

Use this when entering a new repository.

1. create starter kit structure
2. run `repo-snapshot`
3. generate `docs/snapshots/project_snapshot.md`
4. generate or rewrite project `AGENTS.md`
5. human fills `docs/ai/PROJECT_CONTEXT.md`

At the end of Phase 0, the repo should be understandable enough for scoped execution.

---

### Phase 1 — Planning

Use this before coding a new stage.

1. generate or write `docs/plan/plan_stageX.md`
2. split into `docs/plan/issue_stageX.md`
3. human reviews scope and ordering
4. create or update relevant contract docs if execution is about to begin

At the end of Phase 1, the stage should be executable in issue-sized chunks.

---

### Phase 2 — Freeze

Use this before a stage enters active execution.

1. create `docs/contracts/contract_freeze_*.md`
2. lock:
   - stage objective
   - stable interfaces
   - allowed change window
   - forbidden changes
   - stop conditions
3. human confirms the freeze

At the end of Phase 2, agents should know where execution freedom stops.

---

### Phase 3 — Execute

Use implementer for a single issue or a tightly scoped milestone task.

Recommended order:

1. read `AGENTS.md`
2. read `PROJECT_CONTEXT.md`
3. read relevant stage / issue / contract docs
4. plan briefly
5. implement minimally
6. run narrow validation
7. sync docs/tests/config if needed
8. write structured issue report or PR description

At the end of Phase 3, the task should be reviewable.

---

### Phase 4 — Review

Use reviewer after implementation, before merge or milestone close.

Reviewer should inspect:

- scope drift
- contract violations
- validation adequacy
- docs/config mismatch
- semantic correctness risk

Reviewer should produce:

- approve / revise / stop
- severity classification
- recommended next step

At the end of Phase 4, a human should be able to decide quickly.

---

### Phase 5 — Closeout

Use this when a milestone is done or paused.

1. update `docs/handoff/milestone_closeout*.md`
2. record:
   - completed work
   - missing work
   - key risks
   - next entry point
3. decide whether the milestone can be closed cleanly

At the end of Phase 5, the next stage should have a clear handoff entry.

---

## Minimal First Real Run

For the first real test of this starter kit, do not choose the most complex project.

Choose a project that is:
- moderately structured
- has a readable README
- has a small but real issue to implement
- has limited architectural ambiguity

Recommended first run:

1. run `repo-snapshot`
2. draft `AGENTS.md`
3. fill `PROJECT_CONTEXT.md`
4. write one `plan_stage1.md`
5. write one `issue_stage1.md`
6. freeze one small contract
7. run implementer on one issue
8. run reviewer
9. human checks whether manual coordination effort went down

---

## Success Criteria for the Workflow

This starter workflow is working if:

- agents read repo docs instead of asking for repeated context
- implementation reports become structured and predictable
- reviewer catches meaningful issues, not just style trivia
- humans spend less time doing copy-paste orchestration
- milestone transitions become easier to reason about

---

## Failure Signs

The workflow is not yet working well if:

- humans still rewrite long prompts every time
- agents ignore `AGENTS.md`
- reviewer only repeats the implementer summary
- scope drift happens frequently
- contract docs exist but do not affect behavior
- docs are present but never referenced during execution

---

## How to Evolve Beyond V0

Only upgrade after repeated real use.

Good candidates for V1+:
- more reusable Skills
- nested `AGENTS.md`
- CI-triggered reviews
- project-type specializations
- richer repo-snapshot automation
- plan / issue drafting Skills
- milestone review automation

Do not expand just because it sounds nice.
Expand only after repeated friction shows what is truly reusable.