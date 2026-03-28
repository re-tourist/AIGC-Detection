# M1: Data and Metric Pipeline Bootstrap

## Goal

先把验证实验需要的 data pipeline 和 metric pipeline 搭起来，
让 localized failure validation 具备正确的数据承载、指标计算和结果输出基础。

## In Scope

- localized eval data pipeline
- full-image / localized 的统一 sample schema
- clean / degraded / slice 元信息读取
- metric pipeline
- result / artifact schema
- 小样本 smoke check

## Out of Scope

- Community Forensics baseline integration
- 大规模训练与正式验证实验
- local branch / consistency 方法开发

## Exit Criteria

- 可以稳定读取本地小样本与服务器目录结构
- localized eval 所需的 schema / slice / metric 定义已冻结
- 结果输出格式可供后续 M2 / M3 直接复用

## Planning Note

- localized eval dataset 全量保留在 Linux 服务器
- 本地只需要目录结构、manifest 和小样本用于 smoke check
