# RomanBench v0.1 design

RomanBench evaluates Kannada written in Latin script, especially informal spellings common in messaging and social contexts but poorly represented by formal transliteration systems.

## v0.1 scope

A first release should target 1,000–2,000 evaluation items across:

- transliteration/normalization into Kannada script
- semantic understanding invariant to Roman spelling
- intent/QA pairs with Romanized prompts
- spelling-variation robustness
- Kannada words mixed with ordinary English lexical items

## Data strategy

Prefer original human-authored or clearly permissive data. Aksharantar is a candidate research source, but it remains `review_required` because its subsets have different licensing histories. RomanBench must not simply repackage a transliteration corpus.

A high-value construction pattern is to start from a clean Kannada semantic item, collect multiple independent Romanized renderings from Kannada speakers, and evaluate whether model meaning/answers remain stable across variants.

## v0.1 fields

- `id`
- `semantic_family_id`
- `task`
- `kannada_control`
- `roman_input`
- `reference_answer`
- `romanization_source`
- `author_type`
- `license_basis`
- `split`

## Metrics

- exact/normalized task accuracy where applicable
- semantic-family consistency
- Kannada-script control vs Romanized performance gap
- worst-variant accuracy
- transliteration character/word error rate for normalization tasks

## Leakage rule

All variants in the same semantic family remain in one split. Test-family prompts and variants are never used for fine-tuning.
