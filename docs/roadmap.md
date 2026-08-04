# Roadmap

## Milestone 0 — foundation

Completed or implemented in the repository:

- [x] KannadaLLMBench project taxonomy
- [x] external reference benchmark layer
- [x] Python 3.12+ package baseline
- [x] permissive-license/provenance data registry and approval gate
- [x] streaming Hugging Face slicing by record count or MiB
- [x] reusable `pipelines` package for normalize/dedup/slice/build/manifest
- [x] exact contamination checker
- [x] common benchmark item and dataset-manifest schemas
- [x] RomanBench v0.1 design
- [x] KanMixBench integration contract
- [x] reproducibility documentation
- [x] Makefile developer/data/evaluation targets
- [x] CI and GitHub community files

External actions that cannot be completed solely in this code repository:

- [ ] create/claim a dedicated Hugging Face organization when desired
- [ ] run full baseline models on suitable local/remote hardware and publish the first result table
- [ ] freeze the first original Kannada-native test set after human review

## Milestone 1 — first native benchmark

RomanBench pilot, human review, leakage-safe split, baseline evaluation, and HF dataset release.

## Milestone 2 — public leaderboard

Submission format, model metadata validation, results store, HF Space, and reproducible baseline suite.
