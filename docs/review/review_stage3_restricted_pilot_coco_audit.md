# M3 Restricted Pilot COCO Audit

## 状态

- Milestone: `M3 Strong Baseline Localized Failure Validation`
- Evaluation scope: `restricted_pilot`
- Dataset scope: `COCO-only`
- Run status: `completed`
- Run type: `expanded full-COCO restricted pilot`
- Formal M3 benchmark status: `blocked / not completed`

## 目的

本报告基于本次传回的 expanded `COCO-only restricted_pilot` 产物，
重新审计以下问题：

1. 当前 restricted pilot 是否已经从旧的 64-cap pilot 扩展为 full COCO
2. 扩展后 coverage 是否真正变宽
3. strong baseline 在哪些 localized slices 上仍然强，哪些 slices 上出现更可信的 failure evidence
4. 现阶段哪些结论可以说，哪些仍然不能说

本报告不是 formal M3 closeout，也不是论文 benchmark claim。

## 审计产物

本次审计基于以下实际文件：

- `data/mirrored/br_gen/subsets/restricted_pilot/manifest/layout_audit.json`
- `data/mirrored/br_gen/subsets/restricted_pilot/manifest/clean_manifest.jsonl`
- `data/mirrored/br_gen/subsets/restricted_pilot/manifest/formal_manifest.jsonl`
- `outputs/m3/restricted_pilot/eval/summary.json`
- `outputs/m3/restricted_pilot/eval/localized_failure_summary.json`
- `outputs/m3/restricted_pilot/eval/localized_coverage_summary.json`
- `outputs/m3/restricted_pilot/eval/coverage_audit.md`
- `outputs/m3/restricted_pilot/eval/failure_evidence_map.md`
- `outputs/m3/restricted_pilot/eval/localized_failure_report.md`
- `outputs/m3/restricted_pilot/predictions.jsonl`

## 执行摘要

这次传回的结果已经不是旧的 64-cap pilot，而是一个真正的 expanded
`COCO-only restricted_pilot`：

- fake sample cap 已移除
- `candidate_fake_pairs_before_cap = 50000`
- `selected_fake_pairs_after_cap = 50000`
- `fake_sample_cap_applied = false`
- clean records = `55000`
- formal records = `275000`

coverage 相比旧 pilot 明显变宽：

- generator: `1 -> 5`
- region: `1 -> 2`
- edit-area bins: 从极端失衡且几乎不可分析，扩展为 `small / medium / large` 全部可见
- degradation: `5` 组齐全

这次 expanded run 的核心结论与旧 pilot 已经不同：

- 当前结果仍然不是 formal M3
- 但它已经提供了更可信的 localized failure evidence
- baseline 不再呈现“整体很强”的 easy pilot 形态
- 当前最清晰的 failure 结构是：
  - `background` 明显更容易
  - `stuff` 明显更难
  - `small / medium` 编辑面积明显更难
  - `large` 相对更容易，但也并不稳健

因此，这次 expanded restricted pilot 可以支持如下更强但仍受限的诊断性结论：

> 在 expanded COCO-only restricted pilot 中，Community-Forensics strong baseline 的 localized performance 呈现出显著 slice sensitivity。failure evidence 主要集中在 `stuff` 区域和 `small / medium` 编辑面积，而 `background` 和部分 `large-area` slices 仍保持 easy-regime 特征。

这仍然不是 formal benchmark 结论，但已经足以支撑后续 failure-oriented 方法设计。

## 从旧 pilot 到本次 expanded pilot 的关键变化

### 旧 pilot

- total eval rows: `640`
- clean fake: `64`
- clean real: `64`
- 实际接近：
  - `COCO-only`
  - `BrushNet-only`
  - `background-only`
  - `large-area` 主导

### 本次 expanded pilot

- total eval rows: `275000`
- clean positive: `50000`
- clean negative: `5000`
- unique clean positive base ids: `50000`
- unique clean negative base ids: `5000`

manifest 级 coverage：

- generators:
  - `BrushNet: 10000`
  - `LaMa: 10000`
  - `MAT: 10000`
  - `PowerPaint: 10000`
  - `SDXL: 10000`
- regions:
  - `background: 25000`
  - `stuff: 25000`
- source:
  - `COCO: 50000`
- edit-area bins:
  - `small: 2225`
  - `medium: 7140`
  - `large: 40635`

结论：

- 这次已经是 full COCO restricted pilot
- fake slice 不再受 `64` cap 限制
- 当前 evidence base 已经足够支持 region / area / generator 级别的诊断判断

## 核心指标

### Overall localized_edit

- sample_count: `275000`
- AUROC: `0.8754560336`
- Accuracy: `0.5384181818181818`
- fake_recall: `0.4924`

### Clean localized reference

- sample_count: `55000`
- AUROC: `0.881333958`
- Accuracy: `0.5233636363636364`
- fake_recall: `0.47572`

### 按 degradation

- `jpeg`
  - AUROC: `0.85279667`
  - Accuracy: `0.4834`
  - fake_recall: `0.43188`
- `resize`
  - AUROC: `0.887249036`
  - Accuracy: `0.5583090909090909`
  - fake_recall: `0.51426`
- `blur`
  - AUROC: `0.887058682`
  - Accuracy: `0.5869454545454545`
  - fake_recall: `0.54598`
- `crop`
  - AUROC: `0.885117014`
  - Accuracy: `0.5400727272727273`
  - fake_recall: `0.49416`

## Coverage 审计

### 覆盖是否真正变宽

是。当前 coverage 宽度已经足以推翻旧 pilot 的“过窄结论”。

### Generator coverage

- `5` 个 generator 全覆盖
- 每个 generator clean positive 都是 `10000`
- 不存在 low-support generator slice

### Region coverage

- `background` 和 `stuff` 两类区域都已覆盖
- 每类 clean positive 都是 `25000`
- 不存在 low-support region slice

### Edit-area coverage

- `small = 2225`
- `medium = 7140`
- `large = 40635`

这里仍有面积分布不平衡，但与旧 pilot 不同：

- `small` 和 `medium` 已不再是“几乎没有样本”的状态
- 当前这两个面积桶已经有足够支持度，可形成诊断性判断

### Degradation coverage

- `clean / jpeg / resize / blur / crop` 全覆盖
- 每组总样本数都是 `55000`

### Exploratory coverage

- `region_by_degradation`: `10` 组
- `edit_area_ratio_by_degradation`: `15` 组
- `generator_by_region`: `10` 组

### Blocked metadata

- `subtlety`: 仍 blocked
- 原因：manifest 中没有显式 subtlety metadata

## Failure Evidence Map

## 1. Region 是当前最清晰的 failure 分界

### `background`

- AUROC: `0.981785168`
- Accuracy: `0.8136666666666666`
- fake_recall: `0.77644`
- label: `easy_regime`

### `stuff`

- AUROC: `0.780882748`
- Accuracy: `0.31246666666666667`
- fake_recall: `0.175`
- label: `failure_evidence`

region 是这次最强的 failure axis：

- `background` 明显容易
- `stuff` 明显困难
- 且二者都具有高支持度，不是小样本幻觉

## 2. Edit-area bins 给出了更可信的 localized failure 证据

### `small`

- positives: `2225`
- AUROC: `0.590646606741573`
- Accuracy: `0.6919031141868512`
- fake_recall: `0.0`
- label: `failure_evidence`

### `medium`

- positives: `7140`
- AUROC: `0.6377218487394958`
- Accuracy: `0.42215815485996705`
- fake_recall: `0.01764705882352941`
- label: `failure_evidence`

### `large`

- positives: `40635`
- AUROC: `0.9400559911406423`
- Accuracy: `0.6280048208611811`
- fake_recall: `0.5822566752799311`
- label: `failure_evidence`

这组结果的关键含义不是 “所有 area 都失败”，而是：

- `small / medium` 的 failure 已经非常明显
- `large` 虽然显著强于 `small / medium`，但固定阈值下 fake_recall 仍然不稳
- 这说明 baseline 对 localized area 的敏感性非常强，而且主要劣化发生在更小面积编辑

## 3. Generator slices 不是主要 failure axis，但仍有差异

### 较弱 generators

- `SDXL`
  - fake_recall: `0.3942`
  - AUROC: `0.86563671`
- `LaMa`
  - fake_recall: `0.4049`
  - AUROC: `0.88585324`

### 相对较强 generators

- `MAT`
  - fake_recall: `0.5461`
  - AUROC: `0.89548903`
- `PowerPaint`
  - fake_recall: `0.5336`
  - AUROC: `0.88189406`
- `BrushNet`
  - fake_recall: `0.4998`
  - AUROC: `0.87779675`

解释上应更谨慎：

- generator 之间存在差异
- 但更强的主导因素是 `region`
- 因为在 `generator × region` 组合里，所有 generator 的 `background` 都偏 easy，而所有 generator 的 `stuff` 都偏 weak

## 4. Degradation 不是主要 failure 来源

当前 degradation 的表现是：

- clean 本身就已经弱：
  - fake_recall: `0.47572`
- `jpeg` 最差：
  - fake_recall: `0.43188`
- `blur / resize / crop` 没有造成决定性额外崩塌

因此本次 run 的更合理解释是：

- baseline 的主要问题不是“moderate degradation 使它崩掉”
- 而是 expanded clean COCO localized setting 本身已经暴露出 region / area 维度的 failure structure

## 5. Exploratory 组合切片进一步强化了这个结论

### `region × degradation`

- `background x *` 基本都属于 `easy_regime`
- `stuff x *` 基本都属于 `failure_evidence`

这说明：

- region 差异在不同 degradation 下是稳定的
- `stuff` 的困难不是单一 degradation 偶然造成的

### `generator × region`

所有 `background` 组合都偏 easy，例如：

- `PowerPaint x background`
  - fake_recall: `0.8658`
- `MAT x background`
  - fake_recall: `0.8506`
- `BrushNet x background`
  - fake_recall: `0.821`

所有 `stuff` 组合都偏 weak，例如：

- `SDXL x stuff`
  - fake_recall: `0.1138`
- `LaMa x stuff`
  - fake_recall: `0.1396`
- `BrushNet x stuff`
  - fake_recall: `0.1786`
- `PowerPaint x stuff`
  - fake_recall: `0.2014`
- `MAT x stuff`
  - fake_recall: `0.2416`

这进一步说明：

- 当前最强 failure factor 是 `region`
- 而不是某一个 generator 的偶然异常

### `area × degradation`

- `small x *` 全部显著弱
- `medium x *` 全部显著弱
- `large x blur / resize / crop` 接近 easy
- `large x clean / jpeg` 仍然偏 weak

这说明：

- 面积效应在不同 degradation 下是稳定存在的
- `small / medium` 的 failure 不是由单一 degradation 驱动的

## 关于分数分布与阈值解释

当前结果存在一个重要现象：

- overall AUROC 仍有 `0.8754560336`
- 但 fixed threshold 下 fake_recall 只有 `0.4924`

这意味着：

- 排序能力仍然存在
- 但很多正样本的分数落在阈值 `0.5` 以下

从预测分数看：

- overall positive mean: `0.4926924448234563`
- overall positive median: `0.42285841703414917`
- clean positive mean: `0.4758492011053861`
- clean positive median: `0.26392844319343567`

而 negatives 仍然高度接近 `0`：

- overall negative mean: `0.0026706827158886654`
- overall negative median: `0.00000934402851271443`

这说明当前不是“模型完全没有区分能力”，而是：

- 在 expanded pilot 上，大量 fake 分数并没有被推到稳定高分区
- baseline 对困难 localized slices 的信号不够强
- 因此 fixed-threshold recall 明显下滑

## 结果应该如何解读

### 现在可以安全说的

- expanded `COCO-only restricted_pilot` 已完成
- 当前 run 已经是 full COCO restricted pilot，而不是旧的 64-cap pilot
- coverage 相比旧 pilot 显著变宽
- 当前 evidence map 已足够揭示稳定的 slice-level failure structure
- 当前最可信的 failure dimensions 是：
  - `region_type`
  - `edit_area_ratio`
- 当前最清晰的 easy slice 是：
  - `background`
  - 部分 `large-area` 组合

### 现在仍然不能说的

- formal M3 已完成
- 当前结果可以直接作为论文最终 benchmark
- subtlety 维度上的 failure 已被验证
- 现有 restricted pilot 足以替代 formal M3

## 推荐对内表述

建议用如下措辞：

> We completed an expanded full-COCO restricted pilot for M3. Unlike the earlier 64-cap pilot, the current run covers all 50,000 eligible COCO localized fake-real pairs and exposes materially broader localized evidence. The strong baseline no longer appears uniformly strong. Failure evidence is now consistent on `stuff` regions and `small / medium` edit-area bins, while `background` remains an easy regime. This is strong diagnostic evidence for failure mode discovery, but it is still not a formal M3 benchmark result.

## Bottom Line

这次结果与旧 pilot 的结论不同。

旧 pilot 更像：

- 链路已跑通
- slice 太窄
- overall 偏乐观

本次 expanded pilot 更像：

- full COCO restricted pilot 已完成
- coverage 已显著变宽
- failure map 已经具备诊断价值
- localized failure 并非 uniformly observed，而是明显集中在：
  - `stuff`
  - `small / medium` area

因此，当前 restricted pilot 已经达到了“为后续 failure-oriented 方法设计提供 evidence map”的目标。

但 formal M3 仍然 blocked，论文 benchmark claim 仍不能直接建立在这次 restricted pilot 之上。
