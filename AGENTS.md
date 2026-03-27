# AGENTS.md

## Purpose

This file is the repository-level operating manual for AI coding agents.

It is not a product README and not a task-specific prompt.
It defines the durable working rules that should apply across normal development work in this repository.

Agents should use this file together with:
- project docs under `docs/`
- project configuration under `.codex/`
- any nested `AGENTS.md` / override docs closer to the working directory

---

## Default working order

Follow this order unless a task explicitly requires otherwise:

1. Read the relevant docs and entry files first
2. Confirm the scope and affected files
3. Make the smallest reasonable change
4. Run the narrowest useful validation first
5. Update docs/config/tests if behavior changed
6. Summarize what changed, what was verified, and what remains uncertain

For multi-file, architecture-affecting, or ambiguous tasks:
- plan first
- then implement
- then review

---

## What this repository expects from agents

Always try to:
- preserve existing structure unless a task explicitly allows refactoring
- prefer small, reviewable diffs
- reuse existing patterns before introducing new abstractions
- keep behavior, config, and docs in sync
- report uncertainty instead of silently guessing

Do not:
- rewrite large areas without clear justification
- introduce unrelated cleanup into feature work
- silently change public behavior, contracts, or file layout
- assume missing project facts are true

---

## Always allowed

Agents may usually do the following without asking first:

- read source files, configs, tests, and docs
- inspect repository structure
- implement scoped changes requested by the current task
- run local, non-destructive validation commands
- update nearby documentation to match behavior changes
- add or update tests directly related to the change

---

## Ask first

Ask before doing any of the following:

- adding new dependencies
- changing project structure significantly
- modifying CI, deployment, infra, or secrets-related files
- changing public APIs, schemas, or stable interfaces
- deleting files
- running expensive full-project workflows when narrow validation is available
- changing data formats, model outputs, or evaluation semantics
- editing lockfiles when the task did not require it

---

## Never do

Never do these without explicit human approval:

- commit directly to protected branches
- push or merge without being asked
- modify secrets, credentials, or private keys
- fabricate benchmark, experiment, or validation results
- claim something was verified if it was not actually run
- hide risk, uncertainty, or failed checks

---

## Preferred validation strategy

Prefer the smallest meaningful validation first:

1. file-level or module-level checks
2. focused unit tests
3. local integration checks
4. full test suite only when needed

If a requested change affects:
- public behavior
- config semantics
- data flow
- training / inference / evaluation outputs
then validation scope must expand accordingly.

---

## Done definition

A task is not complete unless all of the following are true:

- the requested scope is implemented
- the changed code is internally consistent
- the most relevant validation was run, or the gap is explicitly reported
- related docs/config/tests were updated if needed
- the final report clearly states:
  - files changed
  - why they changed
  - what was verified
  - what remains uncertain or unverified

---

## Documentation sync rules

When behavior changes, consider whether these must be updated:

- `README.md`
- `docs/ai/`
- `docs/plan/`
- `docs/review/`
- `docs/contracts/`
- examples, scripts, config comments, or usage snippets

Do not assume code-only changes are sufficient.

---

## Reporting format

When finishing a task, report in this structure:

1. Files changed
2. What changed in each file
3. Validation run
4. Risks / uncertainties
5. Suggested next step

Keep the report concise and factual.

---

## If the task is ambiguous

Do not invent hidden assumptions.
Instead:

- state the ambiguity
- propose the most conservative interpretation
- proceed only within clearly safe bounds
- stop and ask when the ambiguity affects architecture, evaluation, safety, or external behavior

---

## If the repository grows more complex

Move specialized rules out of this file and into:
- nested `AGENTS.md`
- `docs/review/code_review.md`
- `docs/contracts/*`
- reusable Skills under `.agents/skills/`

Keep this root file compact and durable.