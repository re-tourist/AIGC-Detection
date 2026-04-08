from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
from PIL import Image

from aigc_detection.data import load_manifest


_EXPORT_MODULE = None


def _load_export_module():
    global _EXPORT_MODULE
    if _EXPORT_MODULE is not None:
        return _EXPORT_MODULE

    script_path = Path(__file__).resolve().parents[1] / "scripts" / "export_community_forensics_predictions.py"
    spec = importlib.util.spec_from_file_location("test_export_community_forensics_predictions", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load script module from {script_path}")

    fake_models = types.ModuleType("models")

    class _FakeViTClassifier:
        @classmethod
        def from_pretrained(cls, *args, **kwargs):
            raise AssertionError("Model loading is outside the scope of this unit test.")

    fake_models.ViTClassifier = _FakeViTClassifier

    module = importlib.util.module_from_spec(spec)
    with patch.dict(
        sys.modules,
        {
            "models": fake_models,
            spec.name: module,
        },
    ):
        spec.loader.exec_module(module)
    _EXPORT_MODULE = module
    return module


class CommunityForensicsExportTests(unittest.TestCase):
    def test_build_parser_exposes_local_module_flags(self) -> None:
        export_module = _load_export_module()

        args = export_module.build_parser().parse_args(
            [
                "--manifest",
                "manifest.jsonl",
                "--output",
                "predictions.jsonl",
                "--use-local-module",
                "--local-module-config",
                "configs/model/local_module.yaml",
                "--progress-every",
                "25",
            ]
        )

        self.assertTrue(args.use_local_module)
        self.assertEqual(args.local_module_config, "configs/model/local_module.yaml")
        self.assertEqual(args.progress_every, 25)

    def test_manifest_image_dataset_applies_optional_perturbation(self) -> None:
        export_module = _load_export_module()

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            image_path = root / "sample.png"
            Image.new("RGB", (16, 16), color=(120, 80, 40)).save(image_path)

            manifest_path = root / "manifest.jsonl"
            manifest_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "sample_id": "clean_sample",
                                "task_type": "localized_edit",
                                "split": "pilot",
                                "image_path": str(image_path),
                                "label": 1,
                                "mask_path": str(image_path),
                                "degradation": "clean",
                                "meta": {"evaluation_scope": "restricted_pilot"},
                            }
                        ),
                        json.dumps(
                            {
                                "sample_id": "jpeg_sample",
                                "task_type": "localized_edit",
                                "split": "pilot",
                                "image_path": str(image_path),
                                "label": 1,
                                "mask_path": str(image_path),
                                "degradation": "jpeg",
                                "meta": {
                                    "evaluation_scope": "restricted_pilot",
                                    "perturbation": {
                                        "kind": "jpeg",
                                        "quality": 85,
                                    }
                                },
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            samples = load_manifest(manifest_path)
            dataset = export_module.ManifestImageDataset(samples, transform=lambda image: np.asarray(image))

            clean_item = dataset[0]
            jpeg_item = dataset[1]

            self.assertEqual(clean_item[1], "clean_sample")
            self.assertEqual(clean_item[7], "clean")
            self.assertEqual(clean_item[8], "")

            self.assertEqual(jpeg_item[1], "jpeg_sample")
            self.assertEqual(jpeg_item[7], "jpeg")
            self.assertEqual(json.loads(jpeg_item[8]), {"kind": "jpeg", "quality": 85})

            self.assertTrue(np.array_equal(clean_item[0], np.asarray(Image.open(image_path).convert("RGB"))))
            self.assertFalse(np.array_equal(clean_item[0], jpeg_item[0]))

    def test_load_model_forwards_local_module_config_only_when_enabled(self) -> None:
        export_module = _load_export_module()

        calls = []

        class _DummyLoadedModel:
            def __init__(self) -> None:
                self.to_calls = []
                self.eval_called = False

            def to(self, device):
                self.to_calls.append(device)
                return self

            def eval(self):
                self.eval_called = True
                return self

        class _FakeViTClassifier:
            @classmethod
            def from_pretrained(cls, *args, **kwargs):
                calls.append(kwargs.copy())
                return _DummyLoadedModel()

        fake_models = types.ModuleType("models")
        fake_models.ViTClassifier = _FakeViTClassifier

        with patch.dict(sys.modules, {"models": fake_models}):
            baseline_model = export_module._load_model(
                hf_model_repo="repo-a",
                model_size="small",
                input_size=384,
                patch_size=16,
                device="cpu",
                use_local_module=False,
                local_module_config=None,
            )
            local_model = export_module._load_model(
                hf_model_repo="repo-b",
                model_size="small",
                input_size=384,
                patch_size=16,
                device="cpu",
                use_local_module=True,
                local_module_config={"type": "topk", "k": 8},
            )

        self.assertIsInstance(baseline_model, _DummyLoadedModel)
        self.assertIsInstance(local_model, _DummyLoadedModel)
        self.assertEqual(calls[0]["use_local_module"], False)
        self.assertIsNone(calls[0]["local_module_config"])
        self.assertEqual(calls[1]["use_local_module"], True)
        self.assertEqual(calls[1]["local_module_config"], {"type": "topk", "k": 8})
        self.assertEqual(baseline_model.to_calls, ["cpu"])
        self.assertTrue(baseline_model.eval_called)
        self.assertEqual(local_model.to_calls, ["cpu"])
        self.assertTrue(local_model.eval_called)


if __name__ == "__main__":
    unittest.main()
