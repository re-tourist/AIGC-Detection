# Issue 6.1 - Evaluation contract audit

## Background

Current repo evaluation already supports `accuracy`, `auroc`, and
`fake_recall`, and M3 has a localized slice evaluator. What is missing is a
frozen audit that states exactly:

- where legacy metrics are defined
- which metadata fields already exist
- which fields must be derived for paper-style reporting
- which protocol pieces are deferred or blocked

## Suggested Branch

`codex/stage6-eval-audit`

## Goal

Freeze the current evaluation contract and produce a gap audit against the
BR-Gen reporting grammar.

## Deliverables

- audit of legacy metric definitions and implementation locations
- audit of manifest / metadata availability
- explicit `fake_recall` vs paper-style `Recall@50` difference note
- frozen `generator_family` mapping rule and exclusion policy
- frozen `repo_frozen_alignment_bins`
- IoU deferred / blocked reason

## Acceptance Criteria

- legacy metric locations are documented
- metadata availability is documented field by field
- derived vs raw fields are clearly separated
- Split A exclusion rules are explicit
- deferred items are listed with reasons
