# Contributing to KannadaLLMBench

Thanks for helping improve Kannada model evaluation. Contributions are welcome for benchmark design, Kannada annotation/review, evaluation infrastructure, data tooling, documentation, and reproducibility.

## Before opening a change

- Search existing issues first.
- For a new dataset/source, use the **Data source review** issue template before adding it to an approved pipeline.
- For a new benchmark track or metric, open a **Benchmark proposal** describing what capability is missing from existing benchmarks.
- Never add external benchmark examples to training data.

## Development

Python 3.12+ is required.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
make install-dev
make check
```

Keep reusable transformation logic under `src/kannadallmbench/pipelines/`; CLI wrappers belong in `scripts/`.

## Data-source standard

We prefer CC0, Apache-2.0, MIT/BSD, and clearly attributable CC BY sources with traceable provenance. A Hub license badge by itself is insufficient. Approval changes should cite the exact source revision and explain upstream lineage.

## Kannada quality

AI may generate candidates or assist tooling, but Kannada naturalness, semantic equivalence, gold labels, cultural claims, and release decisions require qualified human review.

## Pull requests

A PR should explain what changed, why, data/license implications, contamination implications, and validation performed. Keep generated/downloaded data and credentials out of Git.
