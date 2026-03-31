# milestone_closeout

## Milestone Info

- Milestone ID: `m3_strong_baseline_localized_failure_validation`
- Milestone name: `M3: Strong Baseline Localized Failure Validation`
- Status:
  - [ ] complete
  - [x] partially complete
  - [ ] blocked
  - [x] handed off with risks
- Date: `2026-03-31`
- Related stage / branch:
  - `codex/stage3-github-sync`
  - `codex/stage4-coco-local-module-entry`
- Related plan doc:
  - `docs/gitflow/milestones/m3_strong_baseline_localized_failure_validation.md`
- Related issue doc:
  - `docs/gitflow/issues/m3_strong_baseline_localized_failure_validation/README.md`

---

## 1. Executive Summary

M3 原本要回答的是：在当前仓库冻结的数据、metric、runner contract 下，Community Forensics 这个 strong baseline 是否在 localized edits 上仍然存在结构化 failure。

实际完成情况分成两条线：
- formal benchmark 线没有完成，也不会作为当前主线继续推进
- `COCO-only restricted_pilot` 线已经从早期窄 pilot 扩成了 full-COCO restricted pilot，并已经形成可信的 failure evidence map

当前 milestone 已经足以支撑进入下一个 milestone，但支撑方式不是“formal M3 已成立”，而是“COCO-only engineering line 已经有足够清晰的 weak-slice 证据，可以用来驱动 local module 设计”。

最大的剩余问题不是代码缺口，而是边界问题：
- formal M3 仍未建立
- `subtlety` 仍 blocked
- 当前所有方法证据都必须按 restricted-pilot 口径解释

---

## 2. What Was Completed

- [x] formal/restricted pilot manifest pipeline 已实现
  - 对应代码/文档位置：
    - `src/aigc_detection/data/br_gen_formal.py`
    - `scripts/prepare_br_gen_m3_formal.py`
    - `docs/contracts/contract_freeze_stage3_strong_baseline_localized_failure_validation.md`
  - 如何验证：
    - focused tests 已通过
    - Linux 上 restricted pilot manifest 已成功生成
  - 是否已经达到预期：
    - 对 restricted-pilot 路径，达到预期

- [x] Community Forensics baseline 已接通 repo-compatible export/eval path
  - 对应代码/文档位置：
    - `scripts/export_community_forensics_predictions.py`
    - `scripts/run_m3_formal_eval.py`
    - `src/aigc_detection/eval/m3_runner.py`
  - 如何验证：
    - Linux 上 full-COCO restricted pilot export + eval 已跑通
  - 是否已经达到预期：
    - 达到 restricted-pilot 工程线预期

- [x] localized sidecar 已扩展为 failure evidence map
  - 对应代码/文档位置：
    - `outputs/m3/restricted_pilot/eval/localized_failure_summary.json`
    - `outputs/m3/restricted_pilot/eval/localized_coverage_summary.json`
    - `outputs/m3/restricted_pilot/eval/coverage_audit.md`
    - `outputs/m3/restricted_pilot/eval/failure_evidence_map.md`
  - 如何验证：
    - expanded full-COCO restricted pilot 已产出完整 artifacts
  - 是否已经达到预期：
    - 达到 M3 restricted-pilot 诊断目标

- [x] expanded full-COCO restricted pilot 已执行完成
  - 对应代码/文档位置：
    - `data/mirrored/br_gen/subsets/restricted_pilot/manifest/layout_audit.json`
    - `outputs/m3/restricted_pilot/eval/summary.json`
    - `docs/review/review_stage3_restricted_pilot_coco_audit.md`
  - 如何验证：
    - `candidate_fake_pairs_before_cap = 50000`
    - `selected_fake_pairs_after_cap = 50000`
    - `fake_sample_cap_applied = false`
    - eval rows = `275000`
  - 是否已经达到预期：
    - 已达到 “full COCO restricted pilot” 的执行预期

---

## 3. What Was Not Completed

- [ ] formal M3 benchmark 没有完成
  - 为什么没完成：
    - ImageNet / Places negatives 仍然不可用
  - 是 scope 调整、时间原因、依赖缺失，还是结果不支持继续：
    - 外部数据依赖缺失 + 当前主线决策调整
  - 是否应该进入下一个 milestone：
    - 否。M4 不再追这条线

- [ ] `subtlety` 维度没有解锁
  - 为什么没完成：
    - 当前 manifest / metadata 中没有 subtlety 字段
  - 是 scope 调整、时间原因、依赖缺失，还是结果不支持继续：
    - metadata blocked
  - 是否应该进入下一个 milestone：
    - 否，除非数据侧先补齐

- [ ] formal benchmark claim 不能建立
  - 为什么没完成：
    - 当前结果只有 restricted-pilot 口径
  - 是 scope 调整、时间原因、依赖缺失，还是结果不支持继续：
    - contract 边界决定
  - 是否应该进入下一个 milestone：
    - 否。M4 先做工程线比较

---

## 4. Key Files and Changes

### Code

- `src/aigc_detection/data/br_gen_formal.py`
  - 作用：
    - 生成 formal/restricted pilot manifests
  - 在本 milestone 中承担什么责任：
    - 让 COCO-only restricted pilot 可执行

- `src/aigc_detection/eval/m3_runner.py`
  - 作用：
    - 产出 localized coverage 和 failure evidence artifacts
  - 在本 milestone 中承担什么责任：
    - 将 M3 从 overall-score 检查推进到 slice-level diagnosis

- `scripts/export_community_forensics_predictions.py`
  - 作用：
    - 导出 repo-compatible predictions
  - 在本 milestone 中承担什么责任：
    - 承载 Community Forensics baseline 的 restricted-pilot 推理

### Docs

- `docs/review/review_stage3_restricted_pilot_coco_audit.md`
  - 作用：
    - 审计 expanded full-COCO restricted pilot 结果
  - 是否已与实现同步：
    - 是

- `docs/analysis/m3_restricted_pilot_success_criteria.md`
  - 作用：
    - 定义 restricted pilot 成功标准
  - 是否已与实现同步：
    - 是

- `docs/gitflow/milestones/m3_strong_baseline_localized_failure_validation.md`
  - 作用：
    - 记录 M3 当前状态与边界
  - 是否已与实现同步：
    - 本次 closeout 后已同步成 handoff 状态

### Config / Scripts / Assets

- `data/mirrored/br_gen/subsets/restricted_pilot/manifest/`
  - 作用：
    - 保存 full-COCO restricted pilot manifests 与 layout audit
  - 当前是否可直接复用：
    - 可以，M4 继续沿用

- `outputs/m3/restricted_pilot/eval/`
  - 作用：
    - 保存 restricted pilot 的 eval / coverage / failure artifacts
  - 当前是否可直接复用：
    - 可以，M4 直接用作 baseline evidence

---

## 5. Validation Summary

### Validation Run

- focused local tests：
  - `python -m unittest discover -s tests -p 'test_*.py' -v`
- Linux restricted pilot manifest/export/eval：
  - 已完成
- expanded full-COCO restricted pilot artifact audit：
  - 已完成

### What These Checks Actually Prove

- 证明了什么：
  - 当前 repo 能完整执行 Community Forensics 的 COCO-only restricted pilot
  - current sidecar 已足够输出 failure map
  - `stuff` 与 `small / medium area` 是当前最可信的 weak slices
- 没证明什么：
  - formal benchmark
  - ImageNet / Places negatives 下的表现
  - subtlety 维度的 failure

### Missing or Weak Validation

- formal BR-Gen full benchmark 没有执行
- 当前没有 formal closeout 所需的跨源 negatives 验证

---

## 6. Risks and Known Limitations

### P0 / blocking

- formal 线当前已被主动递延
  - 风险出现在哪里：
    - 任何未来写作若误把 restricted pilot 当 formal benchmark，会直接越界
  - 会影响什么：
    - benchmark 表述与 milestone 定性
  - 是否会误导下一个 milestone：
    - 会，所以必须在 handoff 里写死

### P1 / serious but not blocking

- 当前所有方法证据都来自 `COCO-only restricted_pilot`
  - 会影响什么：
    - 不能直接外推成 formal benchmark claim

- `subtlety` 仍然 blocked
  - 会影响什么：
    - 无法把 failure 分析推进到更细的隐蔽性层级

### P2 / should improve later

- 当前结果解释仍需同时看 ranking 和 fixed-threshold behavior
- future M4 如果只看 overall score，容易错过真正的 slice-level 改善或退化

---

## 7. Contract / Scope Notes

- [x] 完全在冻结 contract 内执行
- [ ] 有小范围偏离，但已说明
- [ ] 出现了 contract 级别问题
- [x] 发生了实际 scope 漂移
- [ ] 没有正式 contract freeze

补充说明：
- M3 的原标题是 formal localized failure validation
- 实际收口是 restricted-pilot engineering handoff
- 这次 scope 调整是显式决策，不是偷偷缩窄
- formal 线被明确递延，不得在 M4 中被误写成“已经完成”

---

## 8. Recommended Next Entry Point

### Recommended first task

- 在 Community Forensics baseline 之上接入一个 local module，并在现有 full-COCO restricted pilot 上做 baseline vs local-module 对比

### Recommended first files to read

- `docs/gitflow/milestones/m4_community_forensics_local_module_coco_engineering_line.md`
- `docs/handoff/milestone_closeout_stage3_strong_baseline_localized_failure_validation.md`
- `docs/review/review_stage3_restricted_pilot_coco_audit.md`
- `outputs/m3/restricted_pilot/eval/failure_evidence_map.md`

### Recommended first checks

- 确认 M4 仍然严格停留在 `COCO-only restricted_pilot`
- 先看 `stuff` 和 `small / medium area` 这两条 failure axes
- 确认新模块接入后仍然复用现有 prediction/eval/sidecar contract

### Recommended decision to make before coding

- local module 的最小集成点放在 Community Forensics 的哪一层
- M4 的成功判据是“slice 改善是否真实”，而不是“overall 看起来更高”

---

## 9. Handoff Guidance

- 不要再为 formal M3 补做工程线之外的收尾。
- 不要把 restricted pilot 结果包装成论文 benchmark。
- M4 的入口不是“重跑 M3”，而是“复用 M3 结果，针对已知 weak slices 做 engineering comparison”。
- 任何新模块都必须先在 `stuff` 和 `small / medium area` 上回答是否有改善。
- `subtlety` 缺失不是 bug，是已知 metadata 限制。

---

## 10. Final Verdict

- [ ] milestone can be cleanly closed
- [x] milestone can be closed with documented limitations
- [ ] milestone should remain open pending one last validation
- [ ] milestone should not be closed because the result is not yet reliable

最后一句总结：
- 当前结论：M3 可以作为一个“restricted-pilot-only, COCO-only engineering handoff”关闭；formal benchmark 问题仍未解决，但这已经不再阻止进入 M4。
