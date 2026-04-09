# M6 Protocol Alignment

## 2026-04-09 16:30 CST

Purpose:
- validate the additive M6 protocol/reporting alignment code path
- confirm legacy artifacts stay compatible while new paper-style artifacts are emitted

Environment:
- local Windows workspace
- lightweight code-path and unit/integration validation only

Output root:
- temp directories created by the test suite

### Module compile smoke

```powershell
python -m py_compile src\aigc_detection\metrics\core.py src\aigc_detection\eval\protocol_alignment.py src\aigc_detection\eval\m3_runner.py src\aigc_detection\eval\__init__.py scripts\run_m3_formal_eval.py
```

### Focused and compatibility unit tests

```powershell
python -m unittest tests.test_metric_core tests.test_protocol_alignment tests.test_m3_formal_eval tests.test_minimal_eval_runner tests.test_m5_compare
```

### Focused and compatibility unit tests (PowerShell path fix)

```powershell
$env:PYTHONPATH='src'; python -m unittest discover -s tests -p "test_*.py"
```

### Fixture-backed paper-style artifact export

```powershell
$env:PYTHONPATH='src'; @'
import json
import shutil
import tempfile
from pathlib import Path

from PIL import Image

from aigc_detection.data import load_manifest
from aigc_detection.data.br_gen_formal import prepare_br_gen_formal_manifests
from aigc_detection.eval import run_m3_formal_eval


def write_rgb_image(path: Path, color: tuple[int, int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (10, 10), color=color).save(path)


def write_mask(path: Path, active_pixels: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("L", (10, 10), color=0)
    for index in range(active_pixels):
        x = index % 10
        y = index // 10
        image.putpixel((x, y), 255)
    image.save(path)


repo_root = Path.cwd()
output_root = repo_root / "docs" / "handoff" / "m6_protocol_alignment_fixture"
if output_root.exists():
    shutil.rmtree(output_root)

with tempfile.TemporaryDirectory() as tmp_dir:
    root = Path(tmp_dir)
    source_root = root / "BR-Gen"

    for sample_id, color in (
        ("000000000001", (12, 34, 56)),
        ("000000000002", (22, 44, 66)),
        ("000000000003", (32, 54, 76)),
    ):
        write_rgb_image(source_root / "Real" / "COCO" / f"{sample_id}.jpg", color)

    write_rgb_image(
        source_root / "Forged" / "BrushNet" / "Background" / "COCO" / "000000000001_background.png",
        (200, 10, 10),
    )
    write_mask(
        source_root / "Mask" / "Background" / "COCO" / "000000000001_background.png",
        active_pixels=4,
    )
    write_rgb_image(
        source_root / "Forged" / "LaMa" / "Stuff" / "COCO" / "000000000002_stuff.png",
        (10, 200, 10),
    )
    write_mask(
        source_root / "Mask" / "Stuff" / "COCO" / "000000000002_stuff.png",
        active_pixels=10,
    )
    write_rgb_image(
        source_root / "Forged" / "BrushNet" / "Background" / "COCO" / "000000000003_background.png",
        (10, 10, 200),
    )
    write_mask(
        source_root / "Mask" / "Background" / "COCO" / "000000000003_background.png",
        active_pixels=25,
    )

    subset_root = root / "mirrored" / "br_gen" / "subsets" / "formal"
    artifacts = prepare_br_gen_formal_manifests(
        source_root,
        subset_root,
        allowed_sources=("COCO",),
    )
    samples = load_manifest(artifacts.formal_manifest_path)

    fake_base_scores = {
        "fake__brushnet__background__coco__000000000001_background": 0.40,
        "fake__lama__stuff__coco__000000000002_stuff": 0.70,
        "fake__brushnet__background__coco__000000000003_background": 0.95,
    }
    fake_degradation_offsets = {
        "clean": 0.0,
        "jpeg": -0.10,
        "resize": -0.05,
        "blur": -0.15,
        "crop": -0.20,
    }
    real_degradation_scores = {
        "clean": 0.05,
        "jpeg": 0.10,
        "resize": 0.08,
        "blur": 0.12,
        "crop": 0.15,
    }

    predictions_path = root / "predictions.jsonl"
    with predictions_path.open("w", encoding="utf-8") as handle:
        for sample in samples:
            base_sample_id = sample.meta["base_sample_id"]
            if sample.label == 1:
                score = fake_base_scores[base_sample_id] + fake_degradation_offsets[sample.degradation or "clean"]
            else:
                score = real_degradation_scores[sample.degradation or "clean"]
            handle.write(json.dumps({"sample_id": sample.sample_id, "score": score}) + "\n")

    run_m3_formal_eval(
        manifest_path=artifacts.formal_manifest_path,
        predictions_path=predictions_path,
        output_dir=output_root,
        threshold=0.5,
        command="fixture export for M6 protocol alignment docs",
    )
'@ | python -
```
