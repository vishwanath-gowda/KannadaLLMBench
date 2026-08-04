# RomanBench v0.1 design

RomanBench evaluates Kannada written in Latin script, especially informal spellings common in messaging and social contexts but poorly represented by formal transliteration systems.

> Status: the controlled transliteration/normalization candidate pipeline is implemented. Human review, human-authored Roman variants, and semantic-understanding/QA task construction remain before v0.1 can be frozen.

## v0.1 scope

A first release should target 1,000–2,000 evaluation items across:

- transliteration/normalization into Kannada script
- semantic understanding invariant to Roman spelling
- intent/QA pairs with Romanized prompts
- spelling-variation robustness
- Kannada words mixed with ordinary English lexical items

The first implemented construction stage focuses only on transliteration/normalization families. Later task types should reuse accepted semantic families where possible rather than creating unrelated prompts.

## Data strategy

Prefer original human-authored or clearly permissive data. The default controlled construction path uses pinned CC0 IndicCorpV2 Kannada. Aksharantar remains `review_required`; RomanBench must not simply repackage a transliteration corpus.

The implemented construction pattern is:

1. select a clean Kannada control sentence from an approved source;
2. produce reproducible scholarly/ASCII control Romanizations;
3. group all variants under a stable semantic-family ID;
4. export the family for Kannada-speaker review;
5. collect at least one independent human Romanization before accepting the family into a future benchmark release.

This separates **controlled spelling perturbations** from **natural Roman Kannada** instead of conflating them.

## Candidate fields

Construction candidates include:

- `id`
- `semantic_family_id`
- `track`
- `task`
- `kannada_control`
- `roman_input`
- `reference_answer`
- `variant_type`
- `romanization_source`
- `author_type`
- `review_status`
- `split=candidate`
- structured `provenance`

See `schemas/romanbench-candidate.schema.json`.

## Metrics

- exact/normalized task accuracy where applicable
- semantic-family consistency
- Kannada-script control vs Romanized performance gap
- worst-variant accuracy
- transliteration character/word error rate for normalization tasks

## Human review requirement

A generated synthetic variant can support controlled analysis, but it is not evidence that a spelling is naturally used by Kannada speakers. Accepted v0.1 families should include at least one human-authored Roman form and reviewer identity/decision metadata.

The review workflow is described in [`romanbench-data-construction.md`](romanbench-data-construction.md).

## Leakage rule

All variants in the same semantic family remain in one split. Test-family prompts and variants are never used for fine-tuning. Training overlap is checked before a test/private-test release is frozen.
