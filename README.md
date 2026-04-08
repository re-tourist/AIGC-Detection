# AIGC-Detection

Local evaluation utilities for staged AIGC detection experiments.

## Environment

Use a clean Python `3.10` or `3.11` environment for the M2/M3 strong-baseline
path. The Community-Forensics dependency stack is not maintained for older
Python 3.8 environments.

Install the repository environment before running M2/M3 scripts:

```bash
pip install -r requirements.txt
```

If you are reusing an older environment and hit array / image import issues,
upgrade the core array and image stack explicitly before running the
Community-Forensics export path:

```bash
pip install --upgrade "numpy>=1.24,<2.0" "Pillow>=10,<13"
```

The root `requirements.txt` includes the repo-local dependencies and the
frozen `external/Community-Forensics/requirements.txt` stack used by the
strong-baseline export path.
