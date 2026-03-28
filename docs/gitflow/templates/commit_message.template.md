# Commit Message Template

```text
<type>(<scope> | stage<issue-id>): <short summary>
why:
- ...
- ...

what:
- ...
- ...
```

## Example

```text
feat(train | stage5-9): run paper-aligned smoke training
why:
- validate that the frozen stage5 paper-path can train end to end under a
- small smoke-only budget before main-run work, and record stability plus
- artifact completeness without confusing smoke with final results

what:
- add a dedicated stage5 smoke config, execute an L=5 smoke training run,
- record checkpoints, history, previews, and a smoke report, and attach
- post-run regular eval and blind eval evidence using the existing stage5 paths
```

## Notes

- `why` 写动机、冻结边界和为什么现在做。
- `what` 写实际改动、执行内容和产物。
- 不要把 unrelated cleanup 混进同一个 commit。
