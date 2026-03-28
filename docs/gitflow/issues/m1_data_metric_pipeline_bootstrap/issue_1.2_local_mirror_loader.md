# Issue 1.2 — Implement local mirror loader and normalized sample object

## Background

M1 的主要输入不是全量 64G 数据，而是来自 Linux 服务器的本地 mirror pack：
目录结构、少量代表性样本，以及已有的显式元信息。
如果这一步不能稳定消费 manifest，后续 metric pipeline 无从谈起。

## Suggested Branch

`codex/stage1-data-loader`

## Goal

实现 manifest-driven loader，把 `localized_edit` 和 `full_image_fake` 统一成 normalized sample object，
并优先保证 `localized_edit` 路径可用。

## Tasks

- 读取 local mirror manifest
- 校验 required raw fields
- 解析 optional raw fields
- 明确拒收不允许的 derived raw fields
- 输出 normalized sample object

## Resource Boundary

- `localized_edit` 是 primary path
- `full_image_fake` 在 M1 中只是 schema compatibility path
- 如果 local mirror pack 缺失，停在 loader validation，不继续推进 metric

## Non-Goals

- 不实现 baseline inference
- 不计算 grouped metrics
- 不做服务器规模运行

## Deliverable

- manifest loader
- normalized sample object
- loader smoke test

## Acceptance

- local mirrored samples 能从 manifest 成功加载
- `localized_edit` 样本能变成 normalized sample objects
- `full_image_fake` 兼容分支不成为主开发对象
