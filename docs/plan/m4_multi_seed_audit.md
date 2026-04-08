# M4 Multi-Seed Stability Audit Plan

## Goal

Audit whether the observed no-train local-probe gain on the COCO-only
restricted pilot is stable across random initializations, rather than a lucky
single seed.

This audit is still M4.
It is not M5, not training, and not a benchmark expansion.

## Boundary

- keep `models/local_module.py` unchanged
- keep `models/local_wrapper.py` unchanged
- keep the hard top-k no-train probe
- keep the restricted-pilot eval substrate unchanged
- reuse the existing baseline restricted-pilot result as the control
- do not modify the metric contract or introduce training

## Run Shape

- baseline: reuse `outputs/m4/restricted_pilot/eval_baseline`
- local probe: run 5 seeds by default, 3 minimum if compute is tight
- output root: `outputs/m4/multi_seed_audit/<run_id>/`
- each seed gets its own subdirectory:
  - `seed_000/`
  - `seed_001/`
  - ...

## Command

```bash
python scripts/run_m4_multi_seed_audit.py --seeds 0,1,2,3,4 --device cuda --batch-size 16 --progress-every 100
```

If compute is limited, pass a shorter seed list:

```bash
python scripts/run_m4_multi_seed_audit.py --seeds 0,1,2 --device cuda --batch-size 16 --progress-every 100
```

## Outputs

Per seed:

- `predictions_local_module.jsonl`
- `eval/summary.json`
- `eval/localized_failure_summary.json`
- `eval/localized_coverage_summary.json`
- `export.log`
- `eval.log`
- `metadata.json`
- `export_command.json`
- `eval_command.json`

Top level:

- `summary.json`
- `manifest.json`
- `aggregate_metrics.json`
- `aggregate_metrics.md`
- `run_status.md`

## Success Criteria

- multi-seed audit completes without overwriting previous runs
- baseline reuse is recorded explicitly
- each seed has isolated output and logs
- aggregate stats are generated for overall and slice-level metrics
- the result can be judged as seed-stable, weakly positive, or unstable

## Failure Criteria

- seed outputs collide or overwrite each other
- baseline and seed runs are not comparable
- the audit silently drops failed seeds
- the output only reports a single run without aggregation
- the run drifts into training or a new method definition

## Execution Note

The runner is wired correctly, but the current workspace does not contain the
full forged-image mirror required to complete the audit.

Observed blocker:
- the first missing asset reported by the manifest loader was
  `D:\home\workspace\AIGC\data\BRGen\BR-Gen\Forged\BrushNet\Background\COCO\000000000772_background.png`
- all seeds failed before inference because of that missing forged image

This means the audit is structurally implemented, but seed-stability evidence is
still unavailable in this workspace until the forged-image mirror is complete.

## Repository Workflow Note

- Full restricted-pilot audits and training-scale runs are expected to execute
  on Linux servers with the complete BR-Gen forged-image mirror.
- Local workspace validation is limited to code paths, CLI behavior, config
  parsing, and unit tests.
- When adding a new experiment or rerun, record the exact command in
  `docs/run_order.md` with a timestamped heading and a short note describing the
  purpose, environment, and output root. Preserve prior entries instead of
  overwriting them.
