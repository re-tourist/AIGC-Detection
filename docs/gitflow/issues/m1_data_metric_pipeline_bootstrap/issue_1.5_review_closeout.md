# Issue 1.5 — Review and milestone closeout

## Background

M1 的结束条件不是“代码写完”，而是要清楚说明：
哪些底座已经建立、哪些 slice 能算、哪些因为 metadata 或 local mirror 受限而被明确阻塞，
并把这些作为 M2 的 handoff 输入。

## Suggested Branch

`codex/stage1-closeout`

## Goal

对 M1 的 contract/scope/validation 做 review，
并写出 milestone closeout 与 M2 handoff。

## Tasks

- 按 `docs/review/code_review.md` 做 review
- 汇总 M1 已完成能力
- 汇总 blocked items
- 写出 milestone closeout
- 写出 M2 handoff assumptions

## Resource Boundary

- 不在 closeout 阶段顺手扩 scope
- 不把 blocked items 写成已解决
- 不把 smoke 结果写成正式验证结果

## Non-Goals

- 不继续实现 M2
- 不补做大规模运行
- 不隐式重定义 M1 的完成线

## Deliverable

- review summary
- milestone closeout
- M2 handoff note

## Acceptance

- closeout 精确说明完成项、阻塞项和未验证项
- review 明确 scope/contract 是否保持一致
- M2 handoff 说明 Community Forensics integration 可以假设什么
