# M2: Community Forensics Integration

## Goal

把 Community Forensics 作为 baseline 候选接入当前项目，
确认其开源实现至少能在本项目的 data / metric pipeline 上正常运行、推理和被评测。

## In Scope

- 读取 Community Forensics 论文、代码仓库与必要笔记
- 接入其开源实现或关键实现路径
- 对齐输入输出与当前 repo 的 data / metric pipeline
- 跑 inference / eval path 的最小 sanity check

## Out of Scope

- 完整复刻 Community Forensics 论文原始 eval protocol
- 正式的大规模 localized failure 验证
- local branch / consistency 方法模块

## Exit Criteria

- Community Forensics 在当前 repo 中可被接入
- baseline inference / eval path 能跑通
- 明确哪些设计必须保留，哪些论文 eval 细节不需要复刻

## Planning Note

- M2 的重点是 integration，不是 paper reproduction
- 是否需要额外借用其论文中的 eval 细节，到时按实际接入需求再判断
