# Benchmark contamination policy

KannadaLLMBench separates **training corpora** from **evaluation data**. Benchmark scores are only useful if evaluated examples were not used to tune the model or trivially recoverable from a widely reused source corpus.

## Rules

1. External benchmark content under MILU, IndicIFEval, IndicGenBench, and future benchmark tracks is evaluation-only.
2. Public benchmark test examples, answer keys, generated paraphrases of test items, and hidden-test exports must not enter training mixtures.
3. Derived training data must retain source manifests so overlap investigations are reproducible.
4. When a training source and benchmark originate from the same upstream corpus, split at the strongest available identity boundary (document/article/conversation/semantic family), not only at individual rows.
5. Before a model is promoted on the leaderboard, run exact normalized overlap checks where text access permits and document any known upstream contamination risk.
6. **Public pretraining corpora are not the preferred source for a new hidden leaderboard test set.** Even when a derived prompt is transformed, the semantic/source text may already be present in model pretraining.
7. RomanBench public-corpus-derived controlled candidates are development/control material by default. The preferred private-test path uses newly human-authored Kannada controls followed by independent human Romanizations.
8. All variants in one semantic family stay in one split.
9. Hidden/private-test answer-bearing material is not committed to the public repository.

## RomanBench private-test construction

RomanBench uses two independent human stages for private-test candidates:

- a Kannada author creates a new control sentence under versioned contributor terms;
- different Kannada speakers independently Romanize that control without seeing synthetic IAST/ASCII suggestions.

This does not prove that no model has ever seen a similar sentence, but it materially reduces direct source-corpus contamination compared with deriving the entire hidden set from a known public pretraining corpus.

See [`romanbench-human-collection.md`](romanbench-human-collection.md).

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
