# Stage4 Next-Thread Context Prompt

下面这段 prompt 只提供上下文和边界，不替代你自己的正式 M4 实现提示词。

```text
请在仓库 `D:\MyProject\AIGC-Detection` 中继续工作。

先对齐当前真实状态，不要回头重开 M3：

1. M3 已经正式收口，但收口方式是：
   - `COCO-only restricted_pilot` 工程线已完成
   - formal M3 benchmark 没有完成，且当前不再继续推进
   - M3 的结论只能按 restricted-pilot diagnostic evidence 来使用
   - 不要把 M3 写成 formal benchmark success

2. 当前 M3 的关键结论：
   - expanded full-COCO restricted pilot 已完成
   - `stuff` 是稳定 weak slice
   - `small / medium` edit area 是稳定 weak slice
   - `background` 仍然是 easy regime
   - `subtlety` 仍 blocked

3. 当前应视为 source-of-truth 的文件：
   - `docs/handoff/milestone_closeout_stage3_strong_baseline_localized_failure_validation.md`
   - `docs/review/review_stage3_restricted_pilot_coco_audit.md`
   - `docs/gitflow/milestones/m3_strong_baseline_localized_failure_validation.md`
   - `outputs/m3/restricted_pilot/eval/failure_evidence_map.md`
   - `outputs/m3/restricted_pilot/eval/localized_failure_summary.json`
   - `outputs/m3/restricted_pilot/eval/summary.json`
   - `data/mirrored/br_gen/subsets/restricted_pilot/manifest/layout_audit.json`

4. GitHub 当前状态：
   - M3 milestone 已关闭：`milestone/4`
   - M3 issues `#17-#22` 已全部关闭
   - M4 milestone 已创建：`milestone/5`
   - M4 issues 已创建并保持 open：
     - `#23`
     - `#24`
     - `#25`
     - `#26`

5. 进入新工作前必须遵守：
   - 不要重新打开 formal M3 线路
   - 不要引入 ImageNet / Places negatives
   - 不要把 restricted-pilot 结果包装成 benchmark claim
   - 不要改动现有 M1/M2 metric contract
   - 优先复用现有 Community Forensics baseline export / eval / sidecar 路径

6. 当前本地工作区不是干净的：
   - 存在与本任务无关的未提交和未跟踪文件
   - 不要回滚或混入无关改动
   - 只在你自己的 scope 内增量修改

7. 当前起始分支与提交：
   - branch: `codex/stage4-coco-local-module-entry`
   - commit: `a17c860`

你接下来具体怎么做，以我后续补充的正式 M4 提示词为准。
在开始实现前，先读取上述文档并复述你理解到的边界，再进入具体工作。
```
