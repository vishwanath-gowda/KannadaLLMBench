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

The approval gate is enforced inside the reusable Python construction pipeline as well as the CLI. A `review_required` or `blocked` source raises an error before any RomanBench family is created.

## Construction stages

1. **Stream source records** from the pinned Hugging Face revision.
2. **Segment candidate sentences** conservatively, including newline-delimited records without terminal punctuation.
3. **Filter** for Kannada character ratio, length, word count, URLs/emails, excessive digits, and obvious repeated-character noise.
4. **Deduplicate** normalized Kannada sentences.
5. **Create semantic-family IDs** from source dataset ID, pinned revision, and normalized Kannada control.
6. **Generate controlled Roman variants**:
   - `iast`: scholarly transliteration baseline produced by the MIT-licensed `indic-transliteration` package.
   - `ascii_phonemic`: deterministic ASCII rendering retaining long-vowel distinctions where practical (`aa`, `ii`, `uu`).
   - `ascii_relaxed`: deterministic spelling perturbation that removes selected vowel-length distinctions when that creates a distinct string.
7. **Write candidate JSONL** plus a manifest containing source revision, construction parameters, counts, actual variant distribution, and SHA-256.
8. **Export family-level review CSV** for Kannada speakers.
9. **Validate review decisions** before any later promotion step.

### IAST is a control, not the target behavior

ISO 15919 is the formal international romanization standard for Indic scripts. RomanBench v0.1 currently uses the `indic-transliteration` package's IAST scheme as a reproducible scholarly control because the benchmark's actual target is informal Roman Kannada, not standards compliance. We do not describe the generated IAST column as ISO 15919.

## Candidate vs benchmark gold

Generated records are written with `review_status: pending` and `split: candidate`. They are construction artifacts, not benchmark items. Promotion to `dev`, `test`, or `private_test` requires a separate human-review step.

A candidate family should eventually receive at least one independent human Romanization. The controlled synthetic variants remain useful because they isolate spelling-system effects, but they remain labeled `synthetic_controlled` even after the family is reviewed.

## Human-review workflow

Export one CSV row per semantic family:

```bash
make romanbench-review-export
```

The review sheet contains:

- Kannada control;
- generated IAST / ASCII variants;
- two empty human-Romanization columns;
- review decision (`accept`, `reject`, or `hold`);
- reviewer and notes;
- source key, revision, and license basis.

After reviewers fill the sheet:

```bash
make romanbench-review-validate
```

An accepted family requires a reviewer and at least one human Romanization. Human Romanization fields may not contain Kannada-script characters. Two supplied human variants must not be identical.

## Source-license note on Aksharantar

Aksharantar is useful for research and validation because its current dataset card records source-dependent licensing: manually collected data is CC BY, while mined data from Samanantar/IndicCorp and existing sources is described as CC0. The card also states that AI4Bharat does not own the underlying text from which mined data was extracted. KannadaLLMBench therefore keeps Aksharantar `review_required` rather than making it a default construction dependency.

If used later, an integration must pin an exact revision, preserve the row-level `source` field, explicitly whitelist reviewed source classes, and record that subset definition in the output manifest.

## Reproducible commands

Build 2,000 semantic families from the approved source:

```bash
make romanbench-candidates FAMILIES=2000
```

Build a smaller development sample:

```bash
make romanbench-sample
```

Export for review:

```bash
make romanbench-review-export
```

The output directory is Git-ignored by default. Candidate data should be reviewed locally before any curated release artifact is committed or published.

## Promotion checklist

Before a family enters a benchmark release:

- Kannada control is grammatical and self-contained.
- Source/license metadata is intact.
- Synthetic Romanizations are semantically equivalent to the Kannada control.
- At least one Kannada speaker reviews the family.
- At least one natural Roman variant is human-authored for accepted families.
- Synthetic and human-authored variants remain distinguishable in metadata.
- The entire semantic family is assigned to one split.
- Training-data overlap checks are run before freezing test/private-test data.
