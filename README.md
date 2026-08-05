# KannadaLLMBench

**KannadaLLMBench** is a Kannada-first LLM evaluation and data-engineering project. Its goal is to answer a practical question that broad multilingual leaderboards do not answer well: **how good is a model at real Kannada?**

The project combines established external Kannada benchmarks with new Kannada-native tracks for Romanized Kannada, colloquial/spoken Kannada, Kannada-English code mixing, Karnataka-specific context, and conversational naturalness. It also provides reproducible, license-aware data pipelines for training and fine-tuning Kannada models without contaminating evaluation sets.

> **Status:** Foundation + external reference integrations are implemented. RomanBench v0.1 candidate construction and a free GitHub Pages + Google Sheets human-validation platform are implemented; pilot annotation is the next data step.

## Principles

- **Kannada first.** Measure capabilities that matter to Kannada speakers, not only translated English tests.
- **Reuse before reinventing.** MILU, IndicIFEval, and IndicGenBench stay first-class external reference tracks.
- **Provenance before volume.** Default data pipelines accept only sources explicitly approved for license and lineage.
- **Prefer permissive data.** CC0, Apache-2.0, MIT/BSD, then clearly attributable CC BY.
- **No benchmark leakage.** Evaluation data is never training data.
- **Reproducible results.** Pin dataset/model revisions and emit manifests/hashes.
- **Backend independent.** MLX on Apple Silicon, Transformers, vLLM, or APIs can feed the same evaluation contracts.
- **Synthetic is labeled synthetic.** Generated Romanization variants are construction candidates, not natural-language gold.
- **Separate linguistic dimensions.** Romanization typing plausibility is not colloquialness or code mixing.

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
| RomanBench | Romanized Kannada and spelling variation | construction + validation tooling implemented |
| ColloquialBench | natural spoken-style Kannada | planned |
| KanMixBench | Kannada-English code/script mixing | separate project; integration contract defined |
| CultureBench | Karnataka-specific cultural/context understanding | planned |
| ConversationBench | naturalness and human preference | planned |

See [`docs/benchmark-taxonomy.md`](docs/benchmark-taxonomy.md).

## Requirements

- Python **3.12+**
- `git` for pinned external benchmark checkout
- optional Hugging Face token for gated upstream resources
- Node.js only when running the optional static annotator syntax check locally

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,metrics,data,romanbench]'
make check
```

Or:

```bash
make install-dev
```

## Project layout

```text
KannadaLLMBench/
├── annotator/                  # GitHub Pages UI + Google Apps Script backend source
├── config/
│   └── data_sources.yaml       # source license/provenance registry
├── data/                       # local/generated; ignored by default
├── docs/                       # methodology, governance, architecture, roadmap
├── external/                   # pinned external benchmark registry
├── schemas/                    # stable benchmark/data contracts
├── scripts/                    # CLI entrypoints and project operations
├── src/kannadallmbench/
│   ├── pipelines/              # reusable data transforms + RomanBench construction
│   ├── annotation_tasks.py     # Sheet task export contract
│   ├── contamination.py
│   ├── data_registry.py
│   ├── registry.py
│   └── results.py
├── tests/
└── .github/                    # CI, Pages deployment, and community templates
```

## Data source policy

`config/data_sources.yaml` is the gatekeeper. Sources are `approved`, `review_required`, or `blocked`.

The first approved default corpus is **AI4Bharat IndicCorpV2 Kannada**, pinned to a specific revision and recorded as CC0. Candidate sources such as Aya, English-Kannada cleaned pairs, and Aksharantar remain review-gated until the exact subsets' provenance/licensing is acceptable.

```bash
make data-sources
make registry-validate
```

Read [`docs/data-governance.md`](docs/data-governance.md) and [`docs/source-audit.md`](docs/source-audit.md) before approving a new source.

## Construct RomanBench candidate data

RomanBench v0.1 currently starts with a controlled transliteration/normalization track. It streams approved Kannada text, extracts clean sentence candidates, assigns stable semantic-family IDs, and generates multiple explicitly synthetic Roman variants:

- scholarly IAST baseline;
- ASCII phonemic form that preserves vowel length with doubled vowels;
- a deterministic relaxed ASCII form that removes selected vowel-length distinctions when that produces a distinct variant.

Build 2,000 candidate families:

```bash
make romanbench-candidates FAMILIES=2000
```

Build a small development sample:

```bash
make romanbench-sample
```

Outputs go under `data/interim/romanbench/` and remain Git-ignored. Each row carries source ID, pinned revision, license basis, source-record location, `review_status=pending`, and `split=candidate`. A sidecar manifest records construction parameters, counts, SHA-256, and the actual variant distribution.

Synthetic variants remain labeled synthetic after validation. They are not automatically treated as human-origin Roman Kannada.

See [`docs/romanbench-data-construction.md`](docs/romanbench-data-construction.md) and [`docs/romanbench-v0.1.md`](docs/romanbench-v0.1.md).

## Human validation platform

RomanBench includes a free annotation system designed for Kannada speakers known to the project:

- static mobile-first frontend on GitHub Pages;
- Google Apps Script backend;
- private Google Sheet storage;
- pseudonymous annotator IDs + random access tokens;
- no typing required for normal validation.

Each item asks exactly:

1. **Does the Roman text have the same meaning as the Kannada sentence?**
2. **Would you type Kannada this way using English letters?**

The second question explicitly refers to the Roman/English-letter spelling style. It does **not** ask whether the underlying Kannada sentence is formal or colloquial.

The site runs in demo mode automatically until an Apps Script endpoint is configured in `annotator/config.js`.

Export generated candidates into the Sheet task schema:

```bash
make annotator-tasks \
  ANNOTATOR_INPUT=data/interim/romanbench/candidates.jsonl \
  ANNOTATOR_OUTPUT=data/interim/romanbench/annotator_tasks.csv \
  ANNOTATOR_BATCH=pilot \
  ANNOTATOR_VOTES=2
```

The same exporter supports re-annotation of existing permissively licensed Kannada↔Roman datasets using `--mode pairs`.

See:

- [`docs/annotation-platform.md`](docs/annotation-platform.md) for deployment and operations;
- [`docs/romanbench-annotation-strategy.md`](docs/romanbench-annotation-strategy.md) for the research/data strategy and future-paper methodology record.

## Fresh human-origin private-test workflow

For a contamination-resistant hidden set, the repository also supports newly authored Kannada controls and independent Romanization contributors:

```bash
make romanbench-authoring-template AUTHORING_ROWS=250
make romanbench-authoring-validate
make romanbench-human-romanization-export
make romanbench-human-romanization-validate
```

This higher-cost path is complementary to low-friction validation. The benchmark strategy intentionally combines real existing pairs, synthetic-but-human-validated variants, and a smaller fresh human-origin stratum rather than relying entirely on one construction mechanism.

See [`docs/romanbench-human-collection.md`](docs/romanbench-human-collection.md).

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
- `make annotator-check`
- `make data-sources`
- `make registry-validate`
- `make data-build-records`
- `make data-build-mb`
- `make romanbench-candidates`
- `make romanbench-sample`
- `make annotator-tasks`
- `make bootstrap-external`
- `make milu`
- `make indicifeval`
- `make indicgenbench-dev`

## Documentation

- [Architecture](docs/architecture.md)
- [Benchmark taxonomy](docs/benchmark-taxonomy.md)
- [Data governance](docs/data-governance.md)
- [Source audit](docs/source-audit.md)
- [Contamination policy](docs/contamination-policy.md)
- [External benchmarks](docs/external-benchmarks.md)
- [RomanBench v0.1 design](docs/romanbench-v0.1.md)
- [RomanBench data construction](docs/romanbench-data-construction.md)
- [RomanBench human collection](docs/romanbench-human-collection.md)
- [RomanBench annotation/paper strategy](docs/romanbench-annotation-strategy.md)
- [Annotation platform](docs/annotation-platform.md)
- [KanMixBench integration](docs/kanmixbench-integration.md)
- [Reproducibility](docs/reproducibility.md)
- [Development](docs/development.md)
- [Roadmap](docs/roadmap.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Data contributions are held to a higher bar than code contributions because license/provenance mistakes can invalidate downstream models and benchmark releases.

## License

KannadaLLMBench **code** is Apache-2.0. External benchmark data/code and training datasets retain their own upstream licenses. A source appearing in the registry does not relicense it under Apache-2.0.
