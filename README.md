# KannadaLLMBench

**KannadaLLMBench** is a Kannada-first LLM evaluation and data-engineering project. Its goal is to answer a practical question that broad multilingual leaderboards do not answer well: **how good is a model at real Kannada?**

The project combines established external Kannada benchmarks with new Kannada-native tracks for Romanized Kannada, colloquial/spoken Kannada, Kannada-English code mixing, Karnataka-specific context, and conversational naturalness. It also provides reproducible, license-aware data pipelines for training and fine-tuning Kannada models without contaminating evaluation sets.

> **Status:** Foundation + external reference integrations are implemented. The first original Kannada-native benchmark and public leaderboard are next.

## Principles

- **Kannada first.** Measure capabilities that matter to Kannada speakers, not only translated English tests.
- **Reuse before reinventing.** MILU, IndicIFEval, and IndicGenBench stay first-class external reference tracks.
- **Provenance before volume.** Default data pipelines accept only sources explicitly approved for license and lineage.
- **Prefer permissive data.** CC0, Apache-2.0, MIT/BSD, then clearly attributable CC BY.
- **No benchmark leakage.** Evaluation data is never training data.
- **Reproducible results.** Pin dataset/model revisions and emit manifests/hashes.
- **Backend independent.** MLX on Apple Silicon, Transformers, vLLM, or APIs can feed the same evaluation contracts.

## Benchmark map

### External reference tracks

| Benchmark | Kannada track | Capability |
|---|---|---|
| MILU | `milu_Kannada` | India-centric knowledge and reasoning |
| IndicIFEval | `indicifeval_ground_kn`, `indicifeval_trans_kn` | Verifiable instruction following |
| IndicGenBench | CrossSum, Flores, XQuAD, XorQA | Summarization, translation, QA |

### Kannada-native tracks

| Track | Focus | Status |
|---|---|---|
| RomanBench | informal Romanized Kannada and spelling variation | v0.1 design complete |
| ColloquialBench | natural spoken-style Kannada | planned |
| KanMixBench | Kannada-English code/script mixing | separate project; integration contract defined |
| CultureBench | Karnataka-specific cultural/context understanding | planned |
| ConversationBench | naturalness and human preference | planned |

See [`docs/benchmark-taxonomy.md`](docs/benchmark-taxonomy.md).

## Requirements

- Python **3.12+**
- `git` for pinned external benchmark checkout
- optional Hugging Face token for gated upstream resources

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,metrics,data]'
make check
```

Or:

```bash
make install-dev
```

## Project layout

```text
KannadaLLMBench/
├── config/
│   └── data_sources.yaml       # source license/provenance registry
├── data/                       # local/generated; ignored by default
├── docs/                       # methodology, governance, architecture, roadmap
├── external/                   # pinned external benchmark registry
├── schemas/                    # stable benchmark/data contracts
├── scripts/                    # CLI entrypoints and project operations
├── src/kannadallmbench/
│   ├── pipelines/              # reusable data transforms
│   ├── contamination.py
│   ├── data_registry.py
│   ├── registry.py
│   └── results.py
├── tests/
└── .github/                    # CI and community templates
```

## Data source policy

`config/data_sources.yaml` is the gatekeeper. Sources are `approved`, `review_required`, or `blocked`.

The first approved default training corpus is **AI4Bharat IndicCorpV2 Kannada**, pinned to a specific revision and recorded as CC0. Candidate sources such as Aya, English-Kannada cleaned pairs, and Aksharantar remain review-gated until the exact subsets' provenance/licensing is acceptable.

```bash
make data-sources
make registry-validate
```

Read [`docs/data-governance.md`](docs/data-governance.md) before approving a new source.

## Slice a Hugging Face dataset without downloading all of it

By records:

```bash
python scripts/slice_dataset.py ai4bharat/IndicCorpV2 \
  --config indiccorp_v2 \
  --split kan_Knda \
  --revision 984b75b20ce408f9ba27c6558e9279e8e1b6edfd \
  --records 10000 \
  --output data/samples/indiccorp-kn-10k.jsonl
```

By encoded JSONL size:

```bash
python scripts/slice_dataset.py ai4bharat/IndicCorpV2 \
  --config indiccorp_v2 \
  --split kan_Knda \
  --mb 5 \
  --output data/samples/indiccorp-kn-5mb.jsonl
```

The implementation streams from Hugging Face, so a 5 MiB development sample does not require downloading a multi-GB corpus.

## Build from an approved source

For reproducible training artifacts, use the registry-aware pipeline:

```bash
python scripts/build_dataset.py indiccorp_v2_kannada \
  --output data/processed/indiccorp-kn-10k.jsonl \
  --text-field text \
  --dedup-field text \
  --records 10000
```

A sidecar manifest records source revision/license, record count, size, SHA-256, and pipeline version.

Convenience targets:

```bash
make data-build-records RECORDS=10000
make data-build-mb MB=5
```

## Transform local JSONL

```bash
python scripts/transform_dataset.py input.jsonl output.jsonl \
  --text-field text \
  --dedup-field text
```

Transforms are intentionally conservative: NFC normalization, whitespace normalization, and exact normalized deduplication. Meaning-changing cleanup should be a separate reviewed pipeline.

## Contamination check

```bash
python scripts/check_contamination.py \
  --training data/processed/train.jsonl \
  --training-field text \
  --benchmark benchmark.jsonl \
  --benchmark-field prompt \
  --fail-on-overlap
```

See [`docs/contamination-policy.md`](docs/contamination-policy.md).

## External benchmark setup

```bash
make bootstrap-external
```

### MILU Kannada

```bash
python scripts/run_external.py milu \
  --model google/gemma-3-4b-it \
  --backend hf \
  --output results/gemma-3-4b-it/milu
```

### IndicIFEval Kannada

```bash
python scripts/run_external.py indicifeval \
  --model google/gemma-3-4b-it \
  --backend hf \
  --output results/gemma-3-4b-it/indicifeval
```

### IndicGenBench Kannada

```bash
make indicgenbench-dev
```

IndicGenBench preparation produces backend-neutral JSONL. Fill the `prediction` field using MLX/Transformers/vLLM/API inference, then run `scripts/score_indicgenbench.py`.

See [`docs/external-benchmarks.md`](docs/external-benchmarks.md).

## Make targets

Run `make help`. Important targets include:

- `make install-dev`
- `make check`
- `make data-sources`
- `make registry-validate`
- `make data-build-records`
- `make data-build-mb`
- `make bootstrap-external`
- `make milu`
- `make indicifeval`
- `make indicgenbench-dev`

## Documentation

- [Architecture](docs/architecture.md)
- [Benchmark taxonomy](docs/benchmark-taxonomy.md)
- [Data governance](docs/data-governance.md)
- [Contamination policy](docs/contamination-policy.md)
- [External benchmarks](docs/external-benchmarks.md)
- [RomanBench v0.1 design](docs/romanbench-v0.1.md)
- [KanMixBench integration](docs/kanmixbench-integration.md)
- [Reproducibility](docs/reproducibility.md)
- [Development](docs/development.md)
- [Roadmap](docs/roadmap.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Data contributions are held to a higher bar than code contributions because license/provenance mistakes can invalidate downstream models and benchmark releases.

## License

KannadaLLMBench **code** is Apache-2.0. External benchmark data/code and training datasets retain their own upstream licenses. A source appearing in the registry does not relicense it under Apache-2.0.
