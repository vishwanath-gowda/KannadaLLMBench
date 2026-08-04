# Data governance and source approval

KannadaLLMBench optimizes for **clean provenance before volume**. A permissive license badge is not enough: a source must also make it possible to trace who assembled the data, where it came from, and which license applies to the exact subset we use.

## License preference

Default preference, strongest first:

1. **CC0 / public-domain dedication**
2. **Apache-2.0, MIT, BSD**
3. **CC BY 4.0** when attribution is straightforward
4. Share-alike or mixed-license sources only when a benchmark need cannot be met more cleanly
5. Non-commercial, no-derivatives, research-only, custom, unclear, or scraped-content-only licensing is excluded from default training pipelines

A permissive wrapper license does not automatically clear underlying content. Web crawls, repackaged corpora, and mixtures are reviewed for upstream rights separately.

## Registry statuses

`config/data_sources.yaml` uses three statuses:

- `approved`: may be used by default build targets.
- `review_required`: discoverable but blocked unless a developer passes `--allow-unreviewed` deliberately.
- `blocked`: must not be consumed by project pipelines.

Approved sources must have an immutable revision and a provenance URL.

## Current default

`indiccorp_v2_kannada` is the first approved training source because AI4Bharat explicitly releases the work's datasets under CC0 and provides an academic provenance trail. Other candidate sources stay review-gated until their exact Kannada partitions are cleared.

## Derived artifacts

Every build produces a sidecar manifest containing:

- source key and Hub dataset ID
- pinned source revision
- source license
- record count and encoded bytes
- SHA-256 of the derived JSONL
- pipeline version and timestamp

Derived artifacts live under `data/` and are ignored unless a release is explicitly reviewed for redistribution.

## Review checklist

Before changing a source to `approved`, verify repository/dataset-card license, upstream licenses, redistribution/derivative rights, provenance, sensitive-data risk, benchmark overlap, immutable revision, and required attribution/citation text. Document non-obvious decisions in the pull request that changes the registry.
