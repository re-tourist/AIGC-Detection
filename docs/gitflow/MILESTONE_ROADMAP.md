# MILESTONE_ROADMAP

## Purpose

This document is the current macro-level milestone source of truth.

它替代了此前过于激进、把 baseline implementation、qualification、localized validation 混在一起的旧拆分。
新的规划先补评测底座，再接 baseline，最后做真正的验证实验。

---

## Roadmap

### M1: Data and Metric Pipeline Bootstrap

目标：
- 先把验证实验的底座搭起来，而不是直接跑强 baseline。

核心内容：
- localized eval data pipeline
- full-image / localized 的统一 sample schema
- clean / degraded / slice 元信息读取
- metric pipeline
- result / artifact schema
- 小样本 smoke check

为什么先做这个：
- 当前项目几乎没有可执行实验基础设施
- 没有 data pipeline 和 metric pipeline，就无法“正确验证”
- 这一步的目标是让后续 baseline integration 有稳定承载面

### M2: Community Forensics Integration

目标：
- 把 Community Forensics 作为 baseline 候选接入当前 pipeline，并确认其开源实现至少能正常运行、推理和被评测。

核心内容：
- 接通 Community Forensics 开源仓库或其关键实现
- 对齐输入输出与当前 repo 的 data / metric pipeline
- 跑 inference / eval path 的最小 sanity check
- 明确哪些部分借用它的方法定义，哪些不需要复刻其论文原始 eval protocol

边界：
- M2 不是完整复现 Community Forensics 论文的评测体系
- M2 的重点是“在本项目协议下可接入、可运行、可被评测”

### M3: Strong Baseline Localized Failure Validation

目标：
- 在你的 localized eval protocol 下，正式验证 strong baseline 是否仍然存在结构性 localized failure。

核心内容：
- 在大量 localized edit 测试样本上评测 baseline
- 报 overall + slice
- 分 clean / degraded
- 回答 strong baseline 是否仍然在 localized edit 上系统性不足
- 为是否进入 local branch + consistency 提供决策依据

---

## Planning Rule

从现在开始，macro planning 按下面顺序走：

1. `M1` 先立 data / metric pipeline
2. `M2` 再接 Community Forensics baseline
3. `M3` 最后做正式验证实验

不要再把这三类工作合并到一个 milestone 里。
