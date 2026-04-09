# Run Order Index

根文档只保留索引。新的实验命令请写到 `docs/run_order/` 下对应的 phase 文档。

## Active Docs

- [Run Order README](run_order/README.md)
- [M7 Unified Training Protocol](run_order/m7_unified_training_protocol.md)
- [M7 Real-Recall Protocol Repair](run_order/m7_real_recall_protocol_repair.md)
- [M7 Matched-Control Execution Guide](run_order/m7_matched_control_execution_guide.md)
- [M7 Matched-Control Audit and Repair](run_order/m7_matched_control_audit_and_repair.md)
- [M7 Local Module Recovery](run_order/m7_local_module_recovery.md)
- [M5b Metric Re-eval](run_order/m5b_metric_reeval.md)
- [M6 Protocol Alignment](run_order/m6_protocol_alignment.md)
- [M5b Seed Ladder](run_order/m5b_seed_ladder.md)
- [M5b Recovery Smoke](run_order/m5b_recovery_smoke.md)
- [M5b Canary Rerun](run_order/m5b_canary_rerun.md)
- [M5b Validation Smoke](run_order/m5b_validation_smoke.md)

## Supporting Docs

- [M7 Unified Training Protocol Contract](contracts/m7_unified_training_protocol.md)
- [M7 Real-Recall Protocol Repair Contract](contracts/m7_real_recall_protocol_repair.md)
- [M5b Resume / State Contract](contracts/m5b_resume_and_state_contract.md)
- [M5b Troubleshooting](troubleshooting.md)

## Legacy Note

旧的单文件命令历史已经拆散到 phase 文档中。需要追溯更早的历史时，请查看 git history。

## 2026-04-09 M7 Real-Recall Protocol Repair Validation

Purpose
- verify the new imbalance-repair protocol wiring, compare-contract checks, and helper semantics before any Linux replay

Environment
- local Windows workspace

### Syntax and CLI smoke

```powershell
python -m py_compile scripts\run_m5_trainable_local_validation.py scripts\run_m7_matched_control_audit.py scripts\run_m7_unified_training_arm.py src\aigc_detection\eval\protocol_repair.py src\aigc_detection\eval\m7_matched_control.py tests\test_protocol_repair.py tests\test_m5_validation_runner.py tests\test_m7_compare.py tests\test_m7_unified_training_arm.py tests\test_m7_validation_runner.py
python scripts\run_m7_unified_training_arm.py --help
python scripts\run_m7_matched_control_audit.py --help
```

### Protocol semantic tests

```powershell
python -m unittest discover -s tests -p "test_protocol_repair.py"
python -m unittest discover -s tests -p "test_m5_validation_runner.py"
python -m unittest discover -s tests -p "test_m7_compare.py"
python -m unittest discover -s tests -p "test_m7_unified_training_arm.py"
python -m unittest discover -s tests -p "test_m7_validation_runner.py"
```
