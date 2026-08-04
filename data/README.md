# Local data layout

Data is generated locally and is not committed by default.

```text
data/
├── raw/          # source snapshots when explicitly downloaded
├── samples/      # small local slices for development
├── processed/    # transformed training artifacts + manifests
├── external/     # external benchmark material (evaluation only)
└── releases/     # reviewed release candidates only
```

Use `scripts/slice_dataset.py` for lightweight Hub samples and `scripts/build_dataset.py` for registry-controlled builds. Any file proposed for `releases/` requires a separate license/provenance review.
