# Benchmark contamination policy

KannadaLLMBench separates **training corpora** from **evaluation data**. Benchmark scores are only useful if the evaluated examples were not used to tune the model.

## Rules

1. External benchmark content under MILU, IndicIFEval, IndicGenBench, and future benchmark tracks is evaluation-only.
2. Public benchmark test examples, answer keys, generated paraphrases of test items, and hidden-test exports must not enter training mixtures.
3. Derived training data must retain source manifests so overlap investigations are reproducible.
4. When a training source and benchmark originate from the same upstream corpus, split at the strongest available identity boundary (document/article/conversation/semantic family), not only at individual rows.
5. Before a model is promoted on the leaderboard, run exact normalized overlap checks where text access permits and document any known upstream contamination risk.

## Automated check

```bash
python scripts/check_contamination.py \
  --training data/processed/train.jsonl \
  --training-field text \
  --benchmark data/private/benchmark.jsonl \
  --benchmark-field prompt \
  --fail-on-overlap
```

The initial checker detects exact overlap after NFC and whitespace normalization. Near-duplicate, semantic, and source-document overlap checks are planned as later hardening; exact overlap is the minimum gate, not proof of zero contamination.
