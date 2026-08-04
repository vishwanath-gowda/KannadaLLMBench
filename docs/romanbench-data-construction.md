# RomanBench data construction

This document defines the executable construction path for RomanBench v0.1 candidate data.

## Goal

Create a reproducible, provenance-preserving candidate pool of Kannada semantic families with controlled Romanized variants. The first construction stage is deliberately synthetic and **must not be described as natural Roman Kannada**. Naturalness requires independent Kannada-speaker review or human-authored variants before promotion into a frozen benchmark release.

## Approved source path

The default source is `indiccorp_v2_kannada` from `config/data_sources.yaml`:

- dataset: `ai4bharat/IndicCorpV2`
- pinned revision: `984b75b20ce408f9ba27c6558e9279e8e1b6edfd`
- Kannada split: `kan_Knda`
- project status: `approved`
- license basis recorded by the project: CC0-1.0

No benchmark candidate may be constructed from a `review_required` or `blocked` source through the default pipeline.

## Construction stages

1. **Stream source records** from the pinned Hugging Face revision.
2. **Segment candidate sentences** conservatively.
3. **Filter** for Kannada character ratio, length, word count, URLs/emails, and obvious noisy records.
4. **Deduplicate** normalized Kannada sentences.
5. **Create semantic-family IDs** from the normalized Kannada control plus source identity.
6. **Generate controlled Roman variants**:
   - `iast`: reversible scholarly transliteration baseline.
   - `ascii_phonemic`: ASCII rendering retaining long-vowel distinctions where practical (`aa`, `ii`, `uu`).
   - `ascii_relaxed`: deterministic spelling perturbation that removes selected length/diacritic distinctions to simulate a harder, non-standardized Roman input.
7. **Write candidate JSONL** plus a manifest containing source revision, construction parameters, counts, and SHA-256.
8. **Human review** is required before any candidate becomes public benchmark gold.

## Candidate vs benchmark gold

Generated records are written with `review_status: pending` and `split: candidate`. They are construction artifacts, not benchmark items. Promotion to `dev`, `test`, or `private_test` requires a separate human-review step.

A candidate family should eventually receive at least one independent human Romanization. The controlled synthetic variants remain useful because they isolate spelling-system effects, but they must remain labeled as synthetic.

## Source-license note on Aksharantar

Aksharantar is useful for research and validation because its dataset card records source-dependent licensing: manually collected data is CC BY, while mined data from Samanantar/IndicCorp and existing sources is described as CC0. However, its aggregate repository combines source types and notes that AI4Bharat does not own the underlying text used for mined pairs. KannadaLLMBench therefore keeps Aksharantar `review_required` rather than making it a default construction dependency. If used later, rows must be selected by source/provenance and that decision must be documented explicitly.

## Reproducible commands

Build 2,000 semantic families from the approved source:

```bash
make romanbench-candidates FAMILIES=2000
```

Build a smaller development sample:

```bash
make romanbench-sample FAMILIES=100
```

The output directory is Git-ignored by default. Candidate data should be reviewed locally before any curated release artifact is committed or published.

## Promotion checklist

Before a family enters a benchmark release:

- Kannada control is grammatical and self-contained.
- Source/license metadata is intact.
- Synthetic Romanizations are semantically equivalent to the Kannada control.
- At least one Kannada speaker reviews the family.
- Natural Roman variants are either human-authored or explicitly marked synthetic.
- The entire semantic family is assigned to one split.
- Training-data overlap checks are run before freezing test/private-test data.
