# KannadaLLMBench

**KannadaLLMBench** is a Kannada-first LLM evaluation suite and leaderboard project. It combines established external Kannada benchmarks with new Kannada-native tracks that target capabilities underrepresented in multilingual evaluation, including colloquial Kannada, Romanized Kannada, Kannada-English code mixing, and natural conversational quality.

> Status: Phase 1 external-reference integration is implemented. Novel Kannada-native tracks and the public leaderboard are upcoming.

## Phase 1: external reference benchmarks

The first release integrates three established suites without redistributing or renaming their benchmark data:

| Benchmark | Kannada track | Capability |
|---|---|---|
| MILU | `milu_Kannada` | India-centric knowledge and reasoning |
| IndicIFEval | `indicifeval_ground_kn`, `indicifeval_trans_kn` | Verifiable instruction following |
| IndicGenBench | CrossSum, Flores, XQuAD, XorQA | Generation, translation and QA |

See [`docs/external-benchmarks.md`](docs/external-benchmarks.md) for pinned revisions, licenses, contamination policy and upstream requirements.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,metrics]'
make bootstrap-external
```

MILU's upstream dataset currently requires Hugging Face access and an `HF_TOKEN`. Install the upstream MILU fork before running MILU:

```bash
pip install -e .external/milu
```

For IndicIFEval, install a compatible `lm-evaluation-harness` plus its small extra dependency set:

```bash
pip install 'lm-eval[ifeval]'
pip install -r .external/indicifeval/lm-evaluation-harness/requirements.txt
```

## Run MILU Kannada

```bash
python scripts/run_external.py milu \
  --model google/gemma-3-4b-it \
  --backend hf \
  --output results/gemma-3-4b-it/milu
```

Use `--dry-run` to print the exact `lm_eval` command without executing it.

## Run IndicIFEval Kannada

```bash
python scripts/run_external.py indicifeval \
  --model google/gemma-3-4b-it \
  --backend hf \
  --output results/gemma-3-4b-it/indicifeval
```

## Prepare IndicGenBench Kannada

IndicGenBench is separated into an inference contract and a scorer so any backend—including MLX on a Mac—can generate predictions.

```bash
python scripts/prepare_indicgenbench.py --task xquad --split dev
```

This writes a Git-ignored JSONL file under `data/external/indicgenbench/`. Add a `prediction` field to each row using your inference backend, then score it:

```bash
python scripts/score_indicgenbench.py \
  --task xquad \
  --predictions path/to/predictions.jsonl
```

Supported tasks: `crosssum`, `flores_en_kn`, `flores_kn_en`, `xquad`, `xorqa`.

## Common result schema

`normalize_lm_eval.py` converts upstream `lm_eval` result JSON into a stable KannadaLLMBench envelope. This keeps leaderboard ingestion independent of upstream output formatting.

```bash
python scripts/normalize_lm_eval.py \
  --benchmark MILU \
  --model google/gemma-3-4b-it \
  --input path/to/lm-eval-results.json \
  --output results/gemma-3-4b-it/milu.normalized.json
```

## Project direction

Planned Kannada-native tracks include:

- Romanized Kannada
- colloquial / spoken-style Kannada
- Kannada-English code mixing (via the separate KanMixBench project)
- Karnataka cultural/contextual understanding
- conversational naturalness and human preference

The external benchmarks provide independent reference scores; they are not presented as original KannadaLLMBench datasets.

## Data policy

Benchmark evaluation data is never training data. External content is fetched locally at pinned revisions and is excluded from Git. Each external benchmark retains its upstream license and citation requirements.

## License

KannadaLLMBench code is Apache-2.0. External benchmark data and code remain governed by their respective upstream licenses.
