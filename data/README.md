# Local data layout

Data is generated locally and is not committed by default.

```text
data/
├── raw/          # source snapshots when explicitly downloaded
├── samples/      # small local slices for development
├── interim/      # construction artifacts awaiting review (for example RomanBench candidates/review CSV)
├── processed/    # transformed training artifacts + manifests
├── external/     # external benchmark material (evaluation only)
└── releases/     # reviewed release candidates only
```

Use `scripts/slice_dataset.py` for lightweight Hub samples and `scripts/build_dataset.py` for registry-controlled builds.

RomanBench controlled candidates live under `data/interim/romanbench/` until Kannada-speaker review. Synthetic candidate JSONL and review CSV files must not be moved to `releases/` merely because the construction pipeline succeeded.

Any file proposed for `releases/` requires a separate license/provenance review, benchmark contamination check, and track-specific quality review.
