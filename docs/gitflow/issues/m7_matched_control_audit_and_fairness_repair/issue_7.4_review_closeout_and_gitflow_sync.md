# Issue 7.4 - Review, Closeout, and Gitflow Sync

## Background

M7 has completed the repaired matched-control audit and the follow-on trainable-stage real-recall protocol repair. The repo now has enough evidence to make the local-vs-control attribution fair again, but the GitHub side still needs a structured closeout record so that the milestone can be closed without losing the evidence trail.

The closeout must reflect the actual repo truth:

- same-split M4 reference is healthy
- old trainable-stage protocol produces real-side collapse for both `current_local` and `matched_global_only_control`
- `balanced_sampler` is the validated stop-loss repair
- `weighted_bce` and `balanced_sampler_weighted_bce` are higher-budget follow-up / ceiling-search arms, not the core fairness proof

## Suggested Branch

`codex/stage7-closeout-sync`

## Goal

Write the M7 review and closeout record, sync the GitHub milestone / issue set to the same evidence chain, and publish the final verdict that the milestone can be closed with documented limitations.

## Tasks

- summarize the completed fairness audit and replay evidence
- state clearly why the old control was not a fair attribution baseline
- document the validated stop-loss repair and the remaining follow-up arms
- record the final recommendation for the milestone state on GitHub
- sync the repo docs so they remain the source of truth after GitHub is closed
- keep the closeout wording aligned with the repaired-protocol metrics:
  - `paper_real_recall_at_0_5`
  - `paper_manipulated_recall_at_0_5`
  - `balanced_accuracy_at_0_5`
  - `blindspot_score`

## Resource Boundary

- use only completed evidence already present under `outputs/m7/`
- do not introduce new architecture work or new data scope
- do not turn the closeout into a new method milestone
- do not overclaim the combined `balanced_sampler_weighted_bce` ceiling search as a prerequisite for closure

## Non-Goals

- no new model code
- no new data boundary
- no benchmark expansion
- no extra-seed mandate beyond the documented replay evidence
- no new fairness theory beyond the already completed protocol repair

## Deliverable

- a readable closeout / handoff doc
- a GitHub milestone sync note
- a GitHub issue / PR mapping that lets the milestone be closed cleanly

## Acceptance

- the closeout explains the real-side collapse and the repaired protocol clearly
- the final verdict distinguishes:
  - protocol artifact
  - repaired-protocol tradeoff frontier
  - remaining follow-up experiments
- the GitHub sync record points to the exact docs and outputs used for closure
- the milestone is safe to close on GitHub with documented limitations
