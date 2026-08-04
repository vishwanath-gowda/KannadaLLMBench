# Development guide

## Python

Python **3.12+** is required. Python 3.12 is the CI baseline; newer supported CPython versions are welcome.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
make install-dev
make check
```

## Data workflows

List the registry:

```bash
make data-sources
```

Create a 10,000-record Hub slice without downloading the full dataset:

```bash
python scripts/slice_dataset.py DATASET_ID --split train --records 10000 --output data/samples/sample.jsonl
```

Or bound the encoded sample by size:

```bash
python scripts/slice_dataset.py DATASET_ID --split train --mb 5 --output data/samples/sample-5mb.jsonl
```

For approved sources, prefer `build_dataset.py` so the license gate and manifest are applied.

## Pull requests

Run `make check` before opening a PR. Data-source approval changes should include evidence for license and provenance. Do not commit benchmark data, downloaded corpora, model outputs containing protected benchmark prompts, tokens, or credentials.
