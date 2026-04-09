# M5b Metric Re-eval

## 2026-04-09 17:20 CST

Purpose:
- 在不触碰既有训练结果的前提下，重评各个 seed 的 control 和 local module 指标
- 生成更全面的 arm-level eval artifact 与 paired comparison artifact
- 让重评估结果落到全新目录，避免任何已有 `train / exports / eval / comparison` 被覆盖

Environment:
- Linux server
- 已有完整 BR-Gen / Community Forensics 输入
- 已有一条成功或部分成功的 M5b run directory

Output root:
- `outputs/m5/restricted_pilot_reeval/<source_run_id>__metric_refresh_<timestamp>`

Safety rules:
- 不要使用 `scripts/run_m5b_local_attribution_validation.py --resume-run-dir ... --force-stage eval`
- 当前 runner 的 `--force-stage eval` 与内部 stage normalization 不一致，可能直接报错
- 本文档只复用已有 prediction export，不重训、不重导出 checkpoint
- 所有新结果必须写到全新的 `restricted_pilot_reeval/` 目录
- `REEVAL_ROOT` 绝不能指向原始 run dir，也不要放在原始 run dir 内部

## Commands

### Read-only preflight

Purpose:
- 只读检查源 run 是否完整
- 提前拒绝错误输出目录，避免误写旧结果

```bash
set -euo pipefail

export SRC_RUN_DIR="outputs/m5/restricted_pilot/m5b_20260406T094651_670984Z_seeds42-43-44-45-46"
export RUN_ID="$(basename "$SRC_RUN_DIR")"
export SEEDS="42,43,44,45,46"
export MANIFEST="data/mirrored/br_gen/subsets/restricted_pilot/splits/m5_frozen_holdout/holdout_manifest.jsonl"
export SPLIT_METADATA="data/mirrored/br_gen/subsets/restricted_pilot/splits/m5_frozen_holdout/split_metadata.json"
export HIST_BASELINE="outputs/m4/restricted_pilot/eval_baseline"
export HIST_M4="outputs/m4/restricted_pilot/eval_local_module"
export REEVAL_ROOT="outputs/m5/restricted_pilot_reeval/${RUN_ID}__metric_refresh_$(date -u +%Y%m%dT%H%M%SZ)"

test -d "$SRC_RUN_DIR"
test -f "$SRC_RUN_DIR/run_metadata.json"
test -f "$MANIFEST"
test -f "$SPLIT_METADATA"
test -d "$HIST_BASELINE"
test -d "$HIST_M4"
test ! -e "$REEVAL_ROOT"

PYTHONPATH=src python - <<'PY'
import os
from pathlib import Path

src_run_dir = Path(os.environ["SRC_RUN_DIR"]).resolve()
reeval_root = Path(os.environ["REEVAL_ROOT"]).resolve()
seeds = [int(item) for item in os.environ["SEEDS"].split(",") if item.strip()]

if reeval_root == src_run_dir or src_run_dir in reeval_root.parents:
    raise SystemExit("REEVAL_ROOT must be outside SRC_RUN_DIR")

missing = []
for seed in seeds:
    seed_dir = src_run_dir / f"seed_{seed:03d}"
    control_pred = seed_dir / "localized_train_global_only_control" / "exports" / "localized_train_global_only_control_predictions.jsonl"
    m5_pred = seed_dir / "m5" / "exports" / "m5_predictions.jsonl"
    required = [
        seed_dir,
        control_pred,
        m5_pred,
    ]
    for path in required:
        if not path.exists():
            missing.append(str(path))

if missing:
    raise SystemExit("Missing required source artifacts:\n" + "\n".join(missing))

print("Preflight OK")
print(f"Source run: {src_run_dir}")
print(f"Re-eval root: {reeval_root}")
print(f"Seeds: {seeds}")
PY
```

### Fresh-output eval refresh

Purpose:
- 基于既有 `localized_train_global_only_control_predictions.jsonl` 与 `m5_predictions.jsonl`
  重跑每个 seed 的 arm eval
- 为 control 和 m5 重新生成 `summary.json`、`localized_failure_summary.json`、
  `overall_metrics.json`、`slice_metrics.json`、`paper_table_summary.md`
- 在新目录中重建每个 seed 的 paired comparison 和 aggregate comparison

```bash
mkdir -p "$REEVAL_ROOT"

PYTHONPATH=src python - <<'PY'
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from aigc_detection.eval import run_m3_formal_eval
from aigc_detection.eval.m5b_attribution import (
    CONTROL_ARM,
    TARGET_ARM,
    build_m5b_pair_summary,
    build_m5b_aggregate_summary,
    write_m5b_pair_artifacts,
    write_m5b_aggregate_artifacts,
)

src_run_dir = Path(os.environ["SRC_RUN_DIR"]).resolve()
reeval_root = Path(os.environ["REEVAL_ROOT"]).resolve()
manifest_path = Path(os.environ["MANIFEST"]).resolve()
split_metadata_path = Path(os.environ["SPLIT_METADATA"]).resolve()
historical_reference_eval_dirs = {
    "original_baseline": Path(os.environ["HIST_BASELINE"]).resolve(),
    "m4_diagnostic_reference": Path(os.environ["HIST_M4"]).resolve(),
}
run_id = os.environ["RUN_ID"]
seeds = [int(item) for item in os.environ["SEEDS"].split(",") if item.strip()]
split_metadata = json.loads(split_metadata_path.read_text(encoding="utf-8"))
seed_runs = []
historical_reference_arms = None


def write_binding(*, eval_dir: Path, seed: int, arm_name: str) -> None:
    summary_path = eval_dir / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    binding = {
        "runner": "m5b_local_module_attribution",
        "comparison_contract_version": 2,
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "run_id": run_id,
        "seed": seed,
        "arm_name": arm_name,
        "paired_control_arm_name": CONTROL_ARM,
        "paired_target_arm_name": TARGET_ARM,
        "evaluation_scope": summary.get("evaluation_scope"),
        "threshold": summary.get("inputs", {}).get("threshold"),
        "manifest_path": str(manifest_path),
        "holdout_manifest_path": str(manifest_path),
        "split_metadata_path": str(split_metadata_path),
        "split_contract_fingerprint": split_metadata.get("split_contract_fingerprint"),
        "split_unit": split_metadata.get("split_unit"),
        "split_seed": split_metadata.get("split_seed"),
        "holdout_fraction": split_metadata.get("holdout_fraction"),
        "source_manifest_path": split_metadata.get("source_manifest_path"),
        "source_manifest_sha256": split_metadata.get("source_manifest_sha256"),
        "source_manifest_checksum_algorithm": split_metadata.get("source_manifest_checksum_algorithm"),
        "export_policy": "fresh_reexport",
        "summary_path": str(summary_path.resolve()),
    }
    (eval_dir / "comparison_binding.json").write_text(
        json.dumps(binding, indent=2, sort_keys=True),
        encoding="utf-8",
    )


preflight_payload = {
    "runner": "m5b_metric_reeval",
    "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "source_run_dir": str(src_run_dir),
    "reeval_root": str(reeval_root),
    "run_id": run_id,
    "manifest_path": str(manifest_path),
    "split_metadata_path": str(split_metadata_path),
    "seeds": seeds,
    "mode": "fresh_output_eval_only",
    "note": "This workflow reuses existing prediction exports and writes all new eval/comparison outputs to a fresh root.",
}
(reeval_root / "preflight.json").write_text(
    json.dumps(preflight_payload, indent=2, sort_keys=True),
    encoding="utf-8",
)

for seed in seeds:
    source_seed_dir = src_run_dir / f"seed_{seed:03d}"
    target_seed_dir = reeval_root / f"seed_{seed:03d}"
    control_pred = source_seed_dir / CONTROL_ARM / "exports" / f"{CONTROL_ARM}_predictions.jsonl"
    m5_pred = source_seed_dir / TARGET_ARM / "exports" / f"{TARGET_ARM}_predictions.jsonl"
    control_eval_dir = target_seed_dir / CONTROL_ARM / "eval"
    m5_eval_dir = target_seed_dir / TARGET_ARM / "eval"
    comparison_dir = target_seed_dir / "comparison"

    run_m3_formal_eval(
        manifest_path=manifest_path,
        predictions_path=control_pred,
        output_dir=control_eval_dir,
        threshold=0.5,
        command="m5b metric re-eval: control arm from frozen prediction export",
    )
    write_binding(eval_dir=control_eval_dir, seed=seed, arm_name=CONTROL_ARM)

    run_m3_formal_eval(
        manifest_path=manifest_path,
        predictions_path=m5_pred,
        output_dir=m5_eval_dir,
        threshold=0.5,
        command="m5b metric re-eval: m5 arm from frozen prediction export",
    )
    write_binding(eval_dir=m5_eval_dir, seed=seed, arm_name=TARGET_ARM)

    pair_summary = build_m5b_pair_summary(
        run_id=run_id,
        seed=seed,
        manifest_path=manifest_path,
        split_metadata_path=split_metadata_path,
        control_eval_dir=control_eval_dir,
        m5_eval_dir=m5_eval_dir,
        historical_reference_eval_dirs=historical_reference_eval_dirs,
    )
    pair_artifacts = write_m5b_pair_artifacts(pair_summary, comparison_dir)
    historical_reference_arms = pair_summary.get("historical_reference_arms", {})
    seed_runs.append(
        {
            "seed": seed,
            "status": "success",
            "seed_dir": str(target_seed_dir.resolve()),
            "evaluation_scope": pair_summary.get("evaluation_scope"),
            "arms": pair_summary["arms"],
            "comparison": {
                "summary_path": str(pair_artifacts.comparison_summary_path),
                "report_path": str(pair_artifacts.comparison_report_path),
                "csv_path": str(pair_artifacts.comparison_csv_path),
            },
        }
    )

aggregate_summary = build_m5b_aggregate_summary(
    run_id=run_id,
    manifest_path=manifest_path,
    split_metadata_path=split_metadata_path,
    seed_runs=seed_runs,
    historical_reference_arms=historical_reference_arms or {},
)
write_m5b_aggregate_artifacts(aggregate_summary, reeval_root / "aggregate")
print(f"Re-eval complete: {reeval_root}")
PY
```

### Quick artifact check

Purpose:
- 确认每个 seed 的 control / m5 eval 和 aggregate comparison 都已经写出

```bash
find "$REEVAL_ROOT" -maxdepth 4 \
  \( -name 'overall_metrics.json' -o -name 'paper_table_summary.md' -o -name 'comparison_summary.json' \) \
  | sort
```

## Notes

- 这条链路只重算指标和报告，不重训，不改 checkpoint，不改原始 prediction export。
- 如果想只重评某个 seed，把 `SEEDS` 改成单个值，例如 `SEEDS="46"`。
- 如果想保留不同版本的重评结果，不要复用 `REEVAL_ROOT`，每次都新建带时间戳的新目录。
