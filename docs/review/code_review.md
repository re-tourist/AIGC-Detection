# code_review

## Purpose

This document defines the project-level review expectations.

它的重点不是样式，而是确保：

- scope 没漂
- Stage 1 contract 没被悄悄打破
- 验证没有被夸大
- 文档、配置、结果口径保持一致
- 指标改善没有掩盖语义偏移

---

## 1. Scope Review

Check whether the change stays within the intended scope.

Questions:
- Does the diff solve the requested issue or stage objective?
- Did it introduce unrelated cleanup or opportunistic refactors?
- Did it quietly move Stage 1 from problem validation toward method development?
- Did it touch `.codex/`、`AGENTS.md`、`docs/contracts/` 这类高敏感区而没有明确理由？

Mark:
- [ ] in scope
- [ ] partly out of scope
- [ ] clearly out of scope

重点提醒：
- 如果 diff 引入 `M1` / `M2`、local branch、consistency，而当前 issue 属于 Stage 1，应默认视为 out of scope，除非 contract 已更新。

---

## 2. Contract / Interface Review

Check whether the change violates any frozen boundary.

Questions:
- Did it change the meaning of `B0` / `B1` / `B1-diverse`?
- Did it change how full-image vs localized evaluation is defined?
- Did it alter slice definitions after results were seen?
- Did it change threshold protocol, metric meaning, or data split semantics?
- Did it violate anything listed in `docs/contracts/contract_freeze_stage1_problem_validation.md`?

Mark:
- [ ] no contract issue found
- [ ] possible contract issue
- [ ] clear contract violation

---

## 3. Validation Review

Check whether the reported validation is adequate.

Questions:
- Were the most relevant local checks actually run?
- Were heavy runs clearly labeled as Linux server execution rather than local smoke checks?
- Does the evidence match the claim, or is the report silently stronger than the run?
- For Stage 1, was there at least enough evidence to support or reject H1 / H2?

Mark:
- [ ] validation adequate
- [ ] validation incomplete but acceptable
- [ ] validation insufficient

---

## 4. Documentation Sync Review

Check whether repository docs remain aligned with behavior.

Questions:
- Did stage/issue/contract docs remain consistent with the code or scripts that were added?
- Should `PROJECT_CONTEXT.md`、plan、contract、closeout or README have changed?
- Did command examples, artifact paths, or config comments become stale?
- Would the next agent be misled if they only read repo docs?

Mark:
- [ ] docs in sync
- [ ] minor doc sync missing
- [ ] significant doc sync missing

---

## 5. Dependency / Configuration Review

Check for hidden repo-wide impact.

Questions:
- Were new dependencies added?
- Did config semantics expand beyond the frozen contract?
- Were new environment assumptions introduced without documentation?
- Did the change make Linux server execution mandatory without writing down the handoff path?

Mark:
- [ ] no concerning repo-wide impact
- [ ] moderate repo-wide impact
- [ ] high repo-wide impact

---

## 6. Semantic Correctness Review

This is the most important section for this repository.

Questions:
- Could the change improve full-image metrics while no longer testing the intended localized failure question?
- Could it “pass tests” but break the controlled comparison between `B1` and `B1-diverse`?
- Did it accidentally mix localized and full-image examples in a way that weakens the argument?
- Are slice results still interpretable as area / subtlety / region failures, rather than arbitrary buckets?
- Is any claimed strong baseline actually strong for the intended reason, or did some other uncontrolled factor change?

Mark:
- [ ] semantics look aligned
- [ ] semantics uncertain
- [ ] likely semantic mismatch

---

## 7. Risk Summary

Classify review findings:

### P0
Must stop. Merge should not proceed.

Examples:
- false validation claim
- clear contract violation
- strong baseline comparison no longer controlled
- evaluation meaning or slice definition broken

### P1
Serious issue. Fix before merge.

Examples:
- missing focused validation
- significant doc mismatch
- result report cannot be traced back to config/data/artifacts
- Linux server run was required but not documented

### P2
Improvement recommended but not blocking.

Examples:
- report clarity
- missing narrow smoke checks
- implementation is harder to review than necessary

---

## 8. Review Output Format

Review reports should follow this structure:

1. Overall verdict
   - approve / revise / stop
2. Scope status
3. Contract status
4. Validation status
5. Documentation sync status
6. Semantic risk summary
7. Issue list by severity
8. Recommended next action

Keep the review concise and evidence-based.

---

## 9. Merge Guidance

Approve only if all of the following are true:

- the change is in scope
- no P0 / P1 issue remains
- validation is adequate for impact level
- docs/config are not misleading
- semantic intent still matches the Stage 1 research question

If unsure, prefer:
- “revise” over “approve”
- “stop and report” over silent acceptance
