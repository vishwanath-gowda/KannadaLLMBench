# Architecture

```text
config/data_sources.yaml
        |
        v
scripts/build_dataset.py
        |
        v
kannadallmbench.pipelines
  hf -> normalize -> dedup -> slice -> JSONL + manifest
        |
        +-------------------> training / model experiments

.external/ pinned repos ----> external evaluators ----> normalized results
native benchmark tracks ----> common benchmark schema -> normalized results
                                                   |
                                                   v
                                             future leaderboard
```

## Design principles

- Streaming-first: large Hub datasets should not require full local downloads for sampling or smoke tests.
- Reproducible: source revision and derived SHA-256 are recorded.
- License-gated: only `approved` registry sources build by default.
- Backend-independent evaluation: scoring contracts do not depend on MLX, Transformers, vLLM, or APIs.
- Small scripts, reusable package: CLI orchestration lives in `scripts/`; transformation logic lives in `src/kannadallmbench/pipelines/` and is unit tested.
