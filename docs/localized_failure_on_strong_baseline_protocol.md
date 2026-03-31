# Localized Failure on Strong Baseline Protocol

## 1. Document Goal

This document defines the experimental protocol for validating the following core research claim:

> Even when a detector is strengthened by generator-diverse training and shows strong image-level generalization on full-image AIGI detection, it can still fail systematically on localized editing detection, especially for small-area, subtle, and deployment-degraded edits.

This protocol is designed to convert the above claim into a falsifiable experimental program.
Its role is not to propose the final method directly, but to establish a strong and fair baseline setting under which the necessity of:
- a local branch / local evidence aggregation module, and
- deployment-aware consistency learning

can be justified.

---

## 2. Core Research Position

### 2.1 What we are **not** trying to prove

We are **not** trying to prove:

- that a local branch can always improve a weak detector;
- that any extra module can improve AIGI detection;
- that localized editing is hard only because current baselines are weak.

These claims are too weak and are vulnerable to reviewer criticism.

### 2.2 What we are trying to prove

We aim to prove a stronger and more meaningful claim:

> After a baseline has already been strengthened with generator-diverse training and has become a strong image-level fake detector, localized editing failure still remains as a distinct and structured failure mode.

More specifically, we want to test whether the residual failure is concentrated on:
- small edited regions,
- subtle semantic changes,
- background / stuff edits,
- and deployment perturbations such as JPEG, resize, blur, and crop.

If this claim is validated, then a local branch is justified as a mechanism for recovering sparse local evidence, and consistency learning is justified as a mechanism for stabilizing that evidence under realistic perturbations.

---

## 3. Main Hypotheses

### H1. Strong global baseline hypothesis

Increasing generator diversity in training significantly improves image-level AIGI detection on full-image fake images, including unseen-generator settings.

This hypothesis is used to establish the legitimacy of the strong baseline.

### H2. Residual localized failure hypothesis

Even after generator-diverse training, a global image-level detector still underperforms on localized editing detection, especially on:
- small-area edits,
- subtle edits,
- background / stuff edits.

This hypothesis captures the residual failure mode we care about.

### H3. Global pooling dilution hypothesis

The residual failure of the strong baseline is not random, but structurally related to the fact that global pooling / global decision mechanisms dilute sparse local forgery evidence.

This is the mechanism-level interpretation behind H2.

### H4. Module-to-failure-mode alignment hypothesis

A local branch should mainly improve localized slices, while deployment-aware consistency should mainly improve degraded localized slices.

If this alignment is observed, it supports the argument that the proposed modules are not generic tricks, but targeted solutions to specific failure modes.

---

## 4. Experimental Logic

The full logic of the protocol is:

1. Build a strong baseline using generator-diverse training.
2. Verify that it is indeed stronger on global full-image AIGI detection.
3. Evaluate the same baseline on localized editing detection.
4. Show that strong global performance does **not** imply strong localized performance.
5. Add a local branch and check whether improvements are concentrated on localized slices.
6. Add consistency learning and check whether improvements are concentrated on degraded localized slices.

The protocol is only successful if the argument chain above is supported end-to-end.

---

## 5. Experimental Groups

To make the argument clean, the backbone and most training settings should remain fixed.
The main changes should be controlled and minimal.

### 5.1 Baseline groups

#### B0: Weak reference baseline
- Backbone: frozen VFM encoder
- Head: linear probe
- Training data: standard / narrow generator fake set
- Purpose:
  - provide a lower reference;
  - show what happens when both model head and generator coverage are weak.

#### B1: Stronger probe baseline
- Backbone: frozen VFM encoder
- Head: MLP probe
- Training data: standard / narrow generator fake set
- Purpose:
  - isolate the effect of a stronger classifier head;
  - separate “probe strength” from “generator diversity”.

#### B1-diverse: Strong generator-diverse baseline
- Backbone: same as B1
- Head: same as B1
- Training data: generator-diverse fake set
- Purpose:
  - isolate the effect of generator diversity;
  - establish the strong global baseline.

This is the most important baseline in the protocol.

### 5.2 Method groups

#### M1: Localized enhancement model
- Base: B1-diverse
- Add: local branch / local evidence aggregation module
- Purpose:
  - test whether explicit local modeling improves localized editing sensitivity.

#### M2: Localized enhancement + deployment-aware consistency
- Base: M1
- Add: realistic perturbation consistency learning
- Purpose:
  - test whether consistency stabilizes localized evidence under deployment perturbations.

---

## 6. Fairness Constraints

To avoid invalid comparisons, the following must be controlled:

- same backbone for B1, B1-diverse, M1, M2;
- same input resolution unless explicitly stated otherwise;
- same optimizer, training epochs / steps, batch size, and scheduler;
- same real-image pool;
- same localized training data ratio when comparing B1-diverse vs M1 vs M2;
- same test splits;
- same threshold selection protocol.

The only intended differences should be:
- generator diversity in training fake data;
- presence / absence of local branch;
- presence / absence of deployment-aware consistency.

If these are not controlled, the conclusions become ambiguous.

---

## 7. Dataset Design

The protocol requires separating **global fake detection** from **localized edit detection**.

### 7.1 Training data

Training data should be divided conceptually into two sources:

#### A. Full-image fake training source
Used to build strong general fake-image detection capability.

Composition:
- real images;
- full-image fake images generated from multiple generators.

Two versions are required:
- narrow-generator version for B0/B1;
- generator-diverse version for B1-diverse/M1/M2.

#### B. Localized edit training source
Used to expose the model to partial edits.

This data should be included in a controlled way.
It should not overwhelm the overall training distribution, otherwise reviewer criticism may shift to:
“you only improved because you gave the model much more localized edit supervision.”

Recommended principle:
- keep localized edit data ratio fixed across B1-diverse / M1 / M2;
- allow only architecture / objective changes to explain differences.

### 7.2 Test data

Test data should be divided into four disjoint evaluation sets:

#### T1. Full-image fake clean set
Purpose:
- verify that generator-diverse training really strengthens image-level AIGI detection.

#### T2. Full-image fake unseen-generator set
Purpose:
- verify that the strong baseline has genuine cross-generator strength.

#### T3. Localized edit clean set
Purpose:
- measure whether strong global detection transfers to localized editing.

#### T4. Localized edit degraded set
Purpose:
- measure whether deployment perturbations further damage localized evidence.

---

## 8. Localized Slice Design

This is the heart of the protocol.

Localized editing should not be treated as a single flat benchmark.
It should be decomposed into interpretable slices.

### 8.1 Slice by edited area ratio

Suggested buckets:
- Small: edited area ratio in a low range
- Medium: edited area ratio in a middle range
- Large: edited area ratio in a high range

Exact thresholds should be dataset-dependent, but the principle must remain stable:
the protocol should reveal whether performance degrades as local evidence becomes sparser.

### 8.2 Slice by edit subtlety

Suggested categories:
- subtle edits
- obvious edits

Operational definition may depend on available annotations or heuristic scoring.
The key goal is to distinguish:
- large semantic / visual deviations that are easy to detect;
- small or plausible edits that may be hidden by global semantics.

### 8.3 Slice by semantic region type

Suggested categories:
- object / foreground edits
- background / stuff edits

Rationale:
background edits are often more weakly represented in global semantic features,
and may therefore be more easily diluted.

### 8.4 Optional slice by edit operation type

If the dataset supports it, add:
- insertion
- removal
- replacement
- style-consistent modification

This is optional in the minimum protocol, but useful for error analysis.

---

## 9. Deployment Perturbation Design

Localized evidence is likely fragile under realistic perturbations.
The degraded localized setting should therefore simulate realistic post-processing.

### 9.1 Required perturbations

At minimum:
- JPEG compression
- resize
- blur
- crop

Optional:
- padding
- rotation
- mild shear

### 9.2 Perturbation protocol

Two rules:
1. perturbations should remain realistic and moderate;
2. clean and degraded evaluations must be reported separately.

The goal is not to break all images aggressively,
but to test whether localized evidence survives plausible deployment transformations.

---

## 10. Metrics

The protocol must avoid relying on a single metric.

### 10.1 Required image-level metrics

At minimum:
- AUROC
- AUPR or AP
- Accuracy
- Fake recall at a fixed threshold

### 10.2 Required slice-level reporting

For localized evaluation, report metrics on:
- overall localized set
- small / medium / large edits
- subtle / obvious edits
- object / background edits
- clean / degraded localized sets

### 10.3 Optional calibration-related reporting

If possible, add:
- threshold sensitivity analysis;
- calibration error or score distribution plots.

Rationale:
a reviewer may argue that localized failure is merely threshold miscalibration.
These analyses help prevent that critique.

---

## 11. Core Tables

### Table 1. Strong baseline qualification table

Purpose:
show that B1-diverse is genuinely stronger than B1 on full-image AIGI detection.

Suggested rows:
- full-image fake clean
- full-image fake unseen-generator
- generator-family split
- degraded full-image fake

Suggested columns:
- B0
- B1
- B1-diverse

Expected result:
- B1 > B0 due to stronger probe;
- B1-diverse > B1 due to generator diversity.

### Table 2. Localized failure table

Purpose:
show that stronger global detection does not eliminate localized failure.

Suggested rows:
- localized overall
- small edit
- medium edit
- large edit
- subtle edit
- obvious edit
- object edit
- background edit

Suggested columns:
- B1
- B1-diverse
- M1
- M2

Expected result:
- B1-diverse improves somewhat over B1;
- but localized slices, especially small/subtle/background, remain weak;
- M1 shows strongest gains on localized slices;
- M2 may not dominate all clean slices, but should remain competitive.

### Table 3. Degraded localized robustness table

Purpose:
show that deployment-aware consistency improves robustness specifically under degraded localized conditions.

Suggested rows:
- localized clean
- localized JPEG
- localized resize
- localized blur
- localized crop
- robustness drop

Suggested columns:
- B1-diverse
- M1
- M2

Expected result:
- M1 improves clean localized performance;
- M2 reduces performance drop under perturbation.

---

## 12. Core Figures

### Figure 1. Edit area ratio vs detection performance

X-axis:
- edited area ratio

Y-axis:
- fake score, AUROC, or recall

Curves:
- B1
- B1-diverse
- M1
- M2

Purpose:
visualize whether strong global detectors collapse as edited area becomes small.

This figure directly tests the “global pooling dilutes sparse local evidence” hypothesis.

### Figure 2. Clean vs degraded localized performance gap

Plot:
- localized clean performance
- localized degraded performance
- drop under each perturbation

Purpose:
show whether consistency learning stabilizes localized evidence.

---

## 13. Required Ablations

To make the conclusions reviewer-resistant, the following ablations are recommended.

### A1. Probe strength ablation
Compare:
- linear probe
- MLP probe

Purpose:
separate the effect of head capacity from generator diversity.

### A2. Generator diversity ablation
Compare:
- narrow-generator training
- generator-diverse training

Purpose:
establish the strong baseline fairly.

### A3. Local branch ablation
Compare:
- B1-diverse
- M1

Purpose:
test whether explicit local modeling is necessary.

### A4. Consistency ablation
Compare:
- M1
- M2

Purpose:
test whether deployment-aware consistency improves degraded localized robustness.

### A5. Parameter-count / naive-localization control
Optional but recommended.

Compare M1 against one or more controls such as:
- larger MLP head
- naive multi-crop aggregation
- patch feature averaging without explicit local branch

Purpose:
prevent the conclusion “it only works because it has more parameters or more views.”

### A6. More-data control
Optional but important if feasible.

Compare:
- stronger baseline with more localized edit samples
- M1 with the same amount of localized edit samples

Purpose:
show that improvements do not come only from more localized supervision.

---

## 14. Success Criteria

The protocol is considered successful if the following evidence chain is observed:

### Stage S1. Strong baseline is established
- B1-diverse clearly outperforms B1 on full-image fake detection, especially unseen-generator evaluation.

### Stage S2. Residual localized failure is exposed
- B1-diverse still performs unsatisfactorily on localized editing detection.
- Failure is not uniform; it is concentrated on small/subtle/background slices.

### Stage S3. Local branch is justified
- M1 yields disproportionate gains on localized slices rather than only generic gains everywhere.

### Stage S4. Consistency is justified
- M2 mainly reduces degradation-induced performance drop on localized edits.

If only S1 is true, then no method justification exists yet.
If S1 + S2 are true, then the problem definition becomes strong.
If S1 + S2 + S3 are true, the local branch becomes justified.
If all four are true, the full method story becomes coherent.

---

## 15. Failure Cases and Interpretation

### Case F1. B1-diverse already solves localized editing well
Interpretation:
- the proposed problem may not be strong enough under the current benchmark;
- need to check whether the localized dataset is too easy or dominated by large edits.

Action:
- harden the localized benchmark;
- increase the proportion of small/subtle/background edits.

### Case F2. B1-diverse fails, but M1 does not help
Interpretation:
- either the local branch is ineffective,
- or localized failure is not caused by global pooling dilution.

Action:
- revisit mechanism hypothesis;
- inspect whether failure is due to data quality, label noise, or training mismatch.

### Case F3. M1 helps everywhere equally
Interpretation:
- improvement may come from generic capacity increase rather than localized evidence recovery.

Action:
- strengthen parameter-count control and naive-local controls.

### Case F4. M2 hurts clean performance without robustness gains
Interpretation:
- consistency design is not aligned with deployment perturbations.

Action:
- re-check perturbation realism and objective weighting.

---

## 16. Minimal Executable Version

If resources are limited, prioritize the following minimum sequence:

1. Build B1 and B1-diverse.
2. Verify B1-diverse > B1 on full-image unseen-generator detection.
3. Evaluate B1 and B1-diverse on localized clean slices.
4. Add M1 and re-evaluate localized clean slices.
5. Add M2 and evaluate localized degraded slices.

This minimum version is enough to validate or reject the main argument chain.

---

## 17. Final Expected Contribution of This Protocol

If validated, this protocol will support the following paper-level message:

> Strong generator-diverse baselines are necessary and should be treated as the proper starting point for modern AIGI detection.
> However, even these strong baselines retain structured failure modes on localized editing, especially when evidence is sparse and deployment perturbations are present.
> This motivates explicit local evidence modeling and deployment-aware consistency learning as targeted remedies rather than generic architectural additions.

---