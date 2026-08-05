# RomanBench annotation and data strategy

This document is the working research-methodology record for RomanBench. It is intentionally more detailed than normal project documentation so that benchmark construction decisions, alternatives, and limitations are preserved for an eventual paper.

## 1. Research objective

RomanBench measures how reliably language models process Kannada written in Latin/English letters under the spelling variation used by Kannada speakers.

The benchmark should answer questions such as:

- Does a model preserve meaning when Kannada is written in Roman script?
- How large is the performance gap between Kannada-script input and Romanized Kannada input?
- Which Roman spelling variations cause the largest failures?
- Does performance degrade on variants that Kannada speakers consider plausible to type?
- Can models remain robust across multiple spellings of the same semantic content?

RomanBench is **not** intended to collapse Romanization, colloquialness, and Kannada-English code mixing into one phenomenon. Those dimensions must remain separately measurable.

## 2. Operational definitions

### 2.1 Romanization / English-letter typing

Representing Kannada linguistic content using Latin/English letters.

Examples:

- `ನಾನು ಮನೆಗೆ ಹೋಗಬೇಕು` -> `nanu manege hogbeku`
- `ನಾನು ಮನೆಗೆ ಹೋಗಬೇಕು` -> `naanu manege hogabeku`

RomanBench focuses on the variability of this representation.

### 2.2 Romanization typing plausibility

The annotator-facing concept is:

> **Would you type Kannada this way using English letters?**

This asks whether the shown Roman spelling is a plausible form the annotator could use when messaging in Kannada with a Latin keyboard.

It does **not** ask whether the underlying Kannada sentence is colloquial, formal, literary, grammatical, culturally natural, or code-mixed.

The paper may refer to this dimension as *Romanization typing plausibility*, *Roman-form plausibility*, or another explicitly defined term. Avoid using the bare word *naturalness* because it is ambiguous.

### 2.3 Colloquialness

A property of the underlying Kannada expression/register.

For example:

- `ನಾನು ಇಂದು ಮನೆಗೆ ಹೋಗಬೇಕು` is comparatively standard/formal.
- `ನಾನ್ ಇವತ್ತು ಮನೆಗೆ ಹೋಗ್ಬೇಕು` is more spoken/colloquial.

Either sentence can independently have plausible or implausible Roman spellings. Colloquialness belongs in ColloquialBench or as a separately annotated RomanBench metadata dimension; it must not be conflated with Roman typing plausibility.

### 2.4 Code mixing

The use of lexical/syntactic material from another language, especially English, within Kannada discourse. This is primarily covered by KanMixBench. RomanBench may contain naturally code-mixed examples, but code mixing should be tagged and analyzed separately.

## 3. Core annotation questions

For each Kannada/Roman candidate pair, an annotator sees both forms and answers only two binary questions.

### Q1 — semantic preservation

> **Does the Roman text have the same meaning as the Kannada sentence?**
>
> Yes / No

This detects transliteration errors, lexical substitutions, dropped content, hallucinated content, and other meaning-changing transformations.

### Q2 — Roman typing plausibility

> **Would you type Kannada this way using English letters?**
>
> Yes / No

Annotator instruction immediately clarifies:

> Judge only the English-letter spelling/style. Do not judge whether the Kannada sentence itself is formal or colloquial.

Annotators can skip an item when they do not understand the Kannada sentence well enough to judge it. Skipping is preferred to guessing.

## 4. Why validation-first annotation

Asking annotators to author Romanized text for every item has high interaction cost and makes large-scale collection difficult, especially when contributors are volunteers known to the project.

RomanBench therefore uses a **candidate generation + low-friction human validation** strategy for most data:

1. obtain a Kannada/Roman candidate pair;
2. show exactly one pair at a time;
3. ask two binary questions;
4. collect independent judgments;
5. retain the raw vote counts and provenance;
6. apply a versioned aggregation policy when freezing a release.

This should permit hundreds of judgments per annotator without requiring extensive typing.

## 5. Data-source strata

RomanBench should preserve a `source_stratum` or equivalent provenance field so results can be analyzed by construction method.

### Stratum A — existing human/natural Roman pairs

Preferred where licensing and provenance are clean.

Potential sources include existing Kannada transliteration/Romanization datasets with permissive licenses and identifiable source partitions. Each source must pass the KannadaLLMBench source audit before inclusion.

Existing pairs are **re-annotated** using RomanBench's two questions even if their original dataset labels already consider them valid transliterations. A formally correct transliteration can preserve meaning while still being implausible as ordinary Kannada typing.

Advantages:

- observed spelling variation rather than generator-invented variation;
- low annotation burden;
- useful empirical distribution for calibrating synthetic generation.

Risks:

- public data may already be present in model pretraining;
- original data may target formal transliteration rather than messaging behavior;
- aggregate dataset licenses can conceal partition-level provenance differences.

Therefore public existing pairs should normally serve as public benchmark/development material, generator calibration data, or an external-distribution check rather than the sole hidden leaderboard set.

### Stratum B — synthetic variants derived from Kannada controls

Synthetic variants provide controlled coverage and allow the benchmark to isolate specific spelling phenomena.

Generation should evolve from rule-invented to **data-driven**. Variant probabilities/rules should be estimated from real permissive Kannada Romanization data when possible.

Candidate generation dimensions can include:

- vowel-length preservation/removal: `naanu` / `nanu`;
- vowel deletion/contraction: `hogabeku` / `hogbeku`;
- aspiration variation: `barthini` / `bartini`;
- consonant spellings: `sh`, `s`, `ch`, etc.;
- gemination variation;
- optional vowels at morpheme boundaries;
- common English-keyboard conventions;
- script-mixed/code-mixed lexical items when explicitly tagged.

Every synthetic item must remain labeled as synthetic even after human validation. Human approval changes its quality status, not its origin.

Advantages:

- scalable;
- controllable difficulty;
- supports per-phenomenon diagnostics;
- supports matched semantic-family evaluation.

Risks:

- generator-support bias: the benchmark may overrepresent patterns the generator knows;
- unrealistic combinations of individually plausible transformations;
- model-specific artifacts if an LLM is used as generator.

These risks are why Stratum A and Stratum C are necessary.

### Stratum C — fresh human-origin content

Fresh content is the preferred basis for a contamination-resistant private leaderboard test set.

The strongest workflow has two independent stages:

1. a Kannada speaker authors a new Kannada control sentence;
2. different Kannada speakers produce or validate Roman forms without seeing synthetic suggestions.

The repository already provides an independent human-authoring/Romanization workflow. If the final protocol changes to validation-first, fresh Kannada controls can still be paired with generated candidates for low-friction validation, but a smaller independently typed sample should be retained as an empirical check on generator coverage.

Advantages:

- reduced direct public-benchmark/pretraining contamination;
- new linguistic content;
- independent evidence of real Roman spelling behavior.

Cost:

- highest contributor burden;
- requires careful data handling and licensing/consent.

## 6. Recommended v0.1 composition

Exact percentages should be finalized after a pilot and recorded before freezing the benchmark. A reasonable starting target is:

- **30–40%** re-annotated existing permissive human/natural Roman pairs;
- **40–50%** synthetic variants whose generation rules are calibrated from observed Roman Kannada;
- **10–20%** fresh independently human-produced Roman forms used for calibration, generator-coverage analysis, and/or contamination-resistant evaluation.

The final private leaderboard subset should place greater weight on fresh content than the public development set.

These numbers are design targets, not fixed claims. The released dataset manifest must contain the actual counts.

## 7. Annotation unit and independence

The annotation unit is one `(semantic_family_id, roman_variant)` pair.

A semantic family groups all variants derived from the same Kannada semantic control.

Rules:

- an annotator should see at most one variant from a semantic family during the same annotation campaign;
- an annotator must not judge a family they authored;
- annotators never see other annotators' votes;
- annotators never see synthetic/formal reference suggestions beyond the candidate being judged;
- task assignment should balance vote counts across candidates;
- presentation order should not encode candidate quality or generator type.

These controls reduce anchoring, within-family dependence, and self-evaluation bias.

## 8. Annotation outcome matrix

The two binary labels create four meaningful outcomes.

| Same meaning | Would type this way | Interpretation |
|---|---|---|
| Yes | Yes | semantically valid + plausible Roman Kannada candidate |
| Yes | No | semantically valid but implausible/unusual typing; useful controlled negative |
| No | Yes | typing form may look plausible but the candidate does not preserve the target meaning; reject for matched evaluation |
| No | No | invalid candidate; reject |

The `Yes/No` distinction on Q2 should not be converted into a colloquialness claim.

## 9. Votes and aggregation

Raw judgments must always be retained. A release should derive aggregate labels from a documented, versioned rule rather than overwriting individual votes.

### Pilot

Use at least two independent votes per candidate to measure disagreement and task clarity.

### Production

Three votes per candidate are preferable for ambiguous forms if volunteer capacity permits. A dynamic policy can request an additional vote only when the first two annotators disagree.

### Provisional acceptance policy

This is a candidate policy to test during the pilot, not yet a frozen benchmark rule:

- semantic validity: require unanimous semantic agreement among completed votes;
- Roman typing positive: majority `Yes` among semantically valid votes;
- Roman typing controlled negative: majority `No` while semantic validity remains unanimous;
- semantic disagreement: adjudicate or exclude;
- excessive Q2 disagreement: retain as an ambiguity set or exclude from the primary score.

The final thresholds should be fixed before examining model leaderboard results on the private test set.

## 10. Quality-control analysis

The eventual paper should report annotation quality rather than only stating that humans reviewed the data.

Recommended statistics:

- raw agreement for Q1 and Q2 separately;
- Cohen's kappa for two-annotator pilot subsets where appropriate;
- Fleiss' kappa or Krippendorff's alpha for multi-annotator production subsets;
- skip rate;
- disagreement rate by source stratum;
- disagreement rate by variation type;
- median/quantile annotation time only if collected with an explicit reason and privacy policy;
- percentage of synthetic candidates rejected for semantic mismatch;
- percentage of semantically correct candidates rejected for typing implausibility.

Do not treat a single aggregate agreement value as sufficient; Q1 and Q2 measure different concepts and should be reported independently.

## 11. Generator calibration using existing permissive data

A major methodological goal is to avoid evaluating only the spelling space invented by our synthetic generator.

For each audited real Kannada/Roman source:

1. normalize without erasing meaningful spelling distinctions;
2. map Kannada/Roman pairs to semantic families;
3. measure character/morpheme correspondence patterns;
4. identify recurring Roman variants;
5. estimate the frequency of transformations where data volume permits;
6. use the observed transformations to define generator rules;
7. reserve at least one independent source or held-out partition to compare generator output against real Roman text.

Possible diagnostics include:

- character n-gram distribution distance;
- edit-operation distributions;
- vowel-deletion frequency;
- consonant/aspiration spelling alternatives;
- token-length ratios;
- lexical/morpheme contraction patterns;
- coverage: fraction of held-out human Roman forms whose major variation patterns are representable by the generator.

A held-out real-data check is important evidence against generator-support bias.

## 12. Existing data and re-annotation

Re-annotation is intentional, not redundant.

A dataset may certify that a Roman form is a transliteration without telling us whether:

- it preserves the exact benchmark sentence meaning;
- it resembles how Kannada speakers type with English letters;
- it is formal transliteration rather than everyday Roman Kannada;
- it is a source artifact or generated form.

RomanBench therefore records original provenance and adds its own task-specific human judgments.

No top-level Hugging Face license badge alone is sufficient to approve a source. Exact subset, upstream origin, redistribution rights, and derivative-use permissions must be documented in the source registry/audit.

## 13. Public vs private evaluation

### Public development/control data

Can include:

- public permissive Kannada/Roman pairs;
- public-corpus-derived Kannada controls;
- synthetic variants;
- released human labels.

These support reproducibility and error analysis but may have pretraining-contamination risk.

### Private leaderboard data

Prefer:

- newly authored semantic content;
- independently validated Roman variants;
- semantic-family-disjoint data;
- no publication of answer-bearing rows before leaderboard evaluation;
- exact and near-duplicate checks against known training/evaluation corpora where feasible.

Public-source benchmark performance and fresh private-test performance should be reported separately rather than merged into one opaque score.

## 14. Split policy

All variants in a semantic family belong to the same split. Never split Roman variants of the same Kannada control across train/dev/test.

When source document IDs exist, document-level separation is preferable to row-level separation.

Recommended conceptual splits:

- `dev`: public, answer-bearing, suitable for prompt/evaluator debugging;
- `public_test`: public inputs; potentially useful for reproducible model comparisons;
- `private_test`: hidden fresh-content evaluation for leaderboard integrity;
- `diagnostic`: curated variation categories and controlled negatives.

## 15. Benchmark metrics

RomanBench should report more than one overall accuracy number.

Recommended metrics:

### Task performance

- transliteration/normalization exact or normalized accuracy;
- QA/instruction accuracy when later tasks are added;
- semantic-family consistency;
- worst-variant accuracy within semantic families.

### Robustness gaps

- Kannada-script control score minus Roman score;
- formal transliteration vs plausible Roman-typing gap;
- human-origin vs synthetic-validated gap;
- per-variation-type accuracy.

### Coverage slices

Report separately by:

- source stratum;
- typing-plausibility label;
- colloquialness tag if later independently annotated;
- code-mix presence;
- sentence length;
- generator/variation type.

An overall score can be supplied for usability, but the benchmark's research value comes from these interpretable sub-scores.

## 16. Annotation platform design

The annotation application is intentionally minimal:

- one Kannada sentence;
- one Roman candidate;
- Q1 Yes/No;
- Q2 Yes/No;
- Skip;
- Submit and advance.

No free-text response is required for normal validation.

The interface must include the exact clarification:

> Judge only the English-letter spelling/style. Do not judge whether the Kannada sentence itself is formal or colloquial.

The platform uses pseudonymous annotator IDs. Names, email addresses, and unnecessary device/user metadata are not required for benchmark construction.

## 17. Ethics, privacy, and contribution terms

Contributors should know:

- what they are contributing;
- how annotations may be redistributed;
- which license/grant applies;
- that participation is voluntary;
- that they should not include personal/private information in newly authored content.

Do not collect demographic information unless a research question specifically requires it and appropriate review/privacy handling is established.

If a publication analyzes contributors as human subjects rather than treating annotations purely as contributed dataset labels, institutional human-subject/ethics requirements should be checked before making assumptions about exemption or review status.

## 18. Reproducibility and versioning

Each released benchmark version should freeze:

- source registry revisions;
- candidate-generation code revision;
- generation configuration;
- annotation instruction version;
- aggregation rule version;
- raw vote counts (where release/privacy policy allows);
- accepted/excluded item manifest;
- semantic-family split manifest;
- hashes of release artifacts;
- model/evaluator versions for baseline results.

Changing annotation wording creates a new instruction version and should not silently mix with prior judgments without analysis.

## 19. Paper-writing checklist

The eventual paper's Data/Methods section should explicitly state:

1. what RomanBench means by Romanization typing plausibility;
2. why that is distinct from colloquialness and code mixing;
3. source strata and exact counts;
4. source licenses/provenance and filtering;
5. synthetic-generation rules and how real data calibrated them;
6. exact annotator-facing questions;
7. annotator assignment and independence rules;
8. number of votes per item and aggregation thresholds;
9. agreement/disagreement statistics;
10. contamination controls and public/private split rationale;
11. distribution and generator-bias limitations;
12. benchmark metrics and slice definitions;
13. model baselines and inference settings;
14. release/version hashes and reproducibility artifacts.

## 20. Known limitations to preserve for the paper

Do not lose these limitations during development:

- Kannada Romanization has no single universally accepted informal spelling standard.
- Individual speakers may strongly prefer different valid spellings.
- Binary typing-plausibility judgments compress a graded phenomenon.
- Volunteer annotators known to the project may not represent all Kannada-speaking regions/ages/dialects.
- Existing public Roman datasets may have pretraining contamination.
- Synthetic generation can encode its own support bias.
- Formal Kannada, colloquial Kannada, and Kannada-English code mixing have different distributions and should not be treated as interchangeable.

These are not reasons to avoid the benchmark; they are reasons to preserve source/annotation metadata and report stratified results.
