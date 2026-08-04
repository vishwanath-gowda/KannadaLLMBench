# Phase 1: External Kannada benchmarks

KannadaLLMBench treats established benchmarks as **external reference tracks**. We do not rename them, redistribute their data, or claim authorship. The integration pins upstream revisions, runs/extracts only the Kannada slice, and stores results in a common local schema.

## MILU (Kannada)

- Upstream: `AI4Bharat/MILU`
- Pinned revision: `7d8e6c9102bf44ae9f9ee84cfabefb4cb8fa2e88`
- Upstream task: `milu_Kannada`
- Kannada size reported upstream: 6,234 questions, including 1,522 translated questions
- Scope: multiple-choice language understanding across 8 domains / 41 subjects
- Dataset license: CC BY 4.0
- Important setup constraint: the upstream README currently requires requesting access to the Hugging Face MILU dataset and setting an `HF_TOKEN`.

The wrapper preserves upstream `lm-eval-harness` behavior and defaults to 5-shot evaluation, matching the upstream example.

## IndicIFEval (Kannada)

- Upstream: `AI4Bharat/IndicIFEval`
- Pinned revision: `94fca1c013dcb7624cc3d6993c31ab2f9b160f0d`
- Upstream tasks: `indicifeval_ground_kn`, `indicifeval_trans_kn`
- Scope: verifiable instruction following with rule-based constraints
- Dataset license: CC BY 4.0

The wrapper points `lm_eval` at the upstream `custom_configs` directory rather than copying those configs into this repository.

## IndicGenBench (Kannada)

- Upstream: `google-research-datasets/indic-gen-bench`
- Pinned revision: `c96a10d90ed9b38cc2108cac6f515a1b8bfdc230`
- Upstream repository was archived on 2026-04-19; the pin makes our integration reproducible.
- Kannada tracks integrated: CrossSum-IN, Flores-IN in both directions, XQuAD-IN, and XorQA-IN.

IndicGenBench contains a benchmark canary stating that benchmark data should not appear in training corpora. `prepare_indicgenbench.py` carries the canary into locally generated inference JSONL and `data/external/` is Git-ignored.

### Licenses are track-specific

- XQuAD-IN: CC BY-SA 4.0
- Flores-IN: CC BY-SA 4.0
- XorQA-IN: MIT
- CrossSum-IN: CC BY-NC-SA 4.0

This matters especially for commercial use of CrossSum-IN.

## Reproducibility and contamination rules

1. External benchmark examples are evaluation-only and must never be added to Kannada model training data.
2. Do not commit `.external/`, `data/external/`, raw prompts, references, or model sample logs containing benchmark text.
3. Every published result must record the model revision, benchmark revision, inference backend, chat template, few-shot count, and generation parameters.
4. MILU/IndicIFEval scores should come from their upstream evaluator/configuration unless a deviation is explicitly documented.
5. IndicGenBench model inference is deliberately backend-agnostic: prepare JSONL, fill `prediction`, then score. This supports MLX on Apple Silicon as well as Transformers/vLLM/API backends without changing the benchmark contract.
