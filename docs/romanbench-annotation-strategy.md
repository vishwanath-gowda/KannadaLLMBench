# RomanBench annotation and data strategy

This document is the working research-methodology record for RomanBench. It is intentionally more detailed than normal project documentation so benchmark-construction decisions, alternatives, assumptions, and limitations are preserved for an eventual paper.

## 1. Research objective

RomanBench measures how reliably language models process Kannada written in Latin/English letters under the spelling variation used by Kannada speakers.

The benchmark should answer questions such as:

- Does a model preserve task performance when Kannada is written in Roman script?
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

The paper may refer to this dimension as *Romanization typing plausibility* or *Roman-form plausibility*. Avoid the bare word *naturalness* because it is ambiguous.

### 2.3 Colloquialness

A property of the underlying Kannada expression/register.

For example:

- `ನಾನು ಇಂದು ಮನೆಗೆ ಹೋಗಬೇಕು` is comparatively standard/formal.
- `ನಾನ್ ಇವತ್ತು ಮನೆಗೆ ಹೋಗ್ಬೇಕು` is more spoken/colloquial.

Either sentence can independently have plausible or implausible Roman spellings. Colloquialness belongs in ColloquialBench or as a separately annotated metadata dimension; it must not be conflated with Roman typing plausibility.

### 2.4 Code mixing

The use of lexical/syntactic material from another language, especially English, within Kannada discourse. This is primarily covered by KanMixBench. RomanBench may contain naturally code-mixed examples, but code mixing should be tagged and analyzed separately.

## 3. Core annotation protocol

For each Kannada/Roman candidate pair, the annotator first answers one mandatory semantic question. A second typing-plausibility question is asked only when the candidate preserves the source meaning.

### Q1 — semantic preservation

> **Does the Roman text have the same meaning as the Kannada sentence?**
>
> Yes / No

This detects transliteration errors, lexical substitutions, dropped content, hallucinated content, number/time changes, and other meaning-changing transformations.

If Q1 = **No**, the item is submitted immediately. Q2 is not shown and the typing label is stored as N/A/blank.

### Q2 — Roman typing plausibility

Q2 is shown only if Q1 = **Yes**:

> **Would you type Kannada this way using English letters?**
>
> Yes / No

The interface immediately clarifies:

> Judge only the English-letter spelling/style. Do not judge whether the Kannada sentence itself is formal or colloquial.

### Skip

Annotators can skip when they do not understand the Kannada sentence well enough to judge it. Skipping is preferred to guessing. A skip produces no Q1 or Q2 label.

### Why Q2 is conditional

Typing plausibility is meaningful only for a Roman candidate that represents the target Kannada content. Asking whether an incorrect sentence is a plausible way to type the target sentence creates an ill-defined label and contaminates agreement statistics.

The protocol therefore has three substantive completed outcomes rather than a four-cell Q1×Q2 matrix:

| Meaning preserved | Typing label | Interpretation |
|---|---|---|
| Yes | Yes | semantically valid + plausible Roman Kannada candidate |
| Yes | No | semantically valid but implausible/unusual Roman typing; useful controlled negative |
| No | N/A | semantic mismatch; reject for matched Roman evaluation |

This conditional structure should be described explicitly in the paper and evaluation code.

## 4. Why validation-first annotation

Asking annotators to author Romanized text for every item has high interaction cost and makes large-scale collection difficult, especially when contributors are volunteers known to the project.

RomanBench therefore uses a **candidate generation + low-friction human validation** strategy for most data:

1. obtain a Kannada/Roman candidate pair;
2. show exactly one pair at a time;
3. collect a semantic-preservation judgment;
4. only for semantic positives, collect a Roman-typing plausibility judgment;
5. retain independent raw judgments and provenance;
6. apply a versioned aggregation policy when freezing a release.

A smaller human-authored Roman sample remains important for checking whether candidate generation covers real typing behavior.

## 5. Data-source strata

RomanBench should preserve a `source_stratum` or equivalent provenance field so results can be analyzed by construction method.

### Stratum A — existing human/natural Roman pairs

Preferred where licensing and provenance are clean.

Potential sources include Kannada transliteration/Romanization datasets with permissive licenses and identifiable source partitions. Each source must pass the KannadaLLMBench source audit before inclusion.

Existing pairs are **re-annotated** using RomanBench's task-specific protocol even if their original dataset labels already consider them valid transliterations. A formally correct transliteration can preserve meaning while still being implausible as ordinary Kannada typing.

Advantages:

- observed spelling variation rather than generator-invented variation;
- low annotation burden;
- empirical distribution for calibrating synthetic generation.

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

Main risk: **generator-support bias**. A benchmark built only from generated variants may measure robustness to the spelling space the generator already knows rather than the broader distribution humans use.

### Stratum C — fresh human-origin content

Fresh content is the preferred basis for a contamination-resistant private leaderboard test set.

The strongest workflow has two independent stages:

1. a Kannada speaker authors a new Kannada control sentence;
2. different Kannada speakers produce or validate Roman forms without seeing other contributors' answers.

A smaller independently typed sample should be retained even if the production workflow is mostly validation-first. It is an empirical check on generator coverage.

Advantages:

- reduced direct public-benchmark/pretraining contamination;
- new linguistic content;
- independent evidence of real Roman spelling behavior.

Cost:

- highest contributor burden;
- requires careful contribution terms and data handling.

## 6. Recommended v0.1 composition

Exact percentages should be finalized after the pilot and recorded before freezing the benchmark. A reasonable starting target is:

- **30–40%** re-annotated existing permissive human/natural Roman pairs;
- **40–50%** synthetic variants whose generation rules are calibrated from observed Roman Kannada;
- **10–20%** fresh independently human-produced Roman forms used for calibration, generator-coverage analysis, and/or contamination-resistant evaluation.

The final private leaderboard subset should place greater weight on fresh content than the public development set.

These are design targets, not fixed claims. The released dataset manifest must contain actual counts.

## 7. Annotation unit and independence

The annotation unit is one `(semantic_family_id, roman_variant)` pair.

A semantic family groups variants derived from the same Kannada semantic control.

Rules:

- an annotator should see at most one variant from a semantic family within a batch;
- an annotator must not judge a family they authored;
- annotators never see other annotators' votes;
- annotators never see synthetic/formal reference suggestions beyond the candidate being judged;
- task assignment should balance vote counts across candidates;
- presentation order should not encode candidate quality or generator type;
- progress and vote counts are scoped by annotation batch.

The one-family-per-annotator rule reduces anchoring between spelling variants of the same content.

## 8. First pilot design

The first pilot is a process-calibration study, not automatic benchmark gold.

Configuration:

- approximately 30 semantic families;
- one Roman candidate per family;
- `target_votes = 2`;
- 4–5 Kannada-speaking annotators;
- deterministic family selection from a larger candidate pool;
- a controlled mixture of available Romanization variant types;
- versioned instruction identifier `romanbench-annotation-v2`.

Thirty tasks × two votes = approximately 60 completed judgments.

The pilot should verify:

- annotators understand the distinction between meaning and typing plausibility;
- semantic-negative examples are recognized;
- Q2 rejection occurs independently of colloquialness;
- skip rate is reasonable;
- assignment and backend behavior are reliable;
- disagreement is analyzable before production thresholds are frozen.

Synthetic/public-corpus pilot items are calibration material. They are not promoted to a private leaderboard merely because annotators approve them.

## 9. Votes and aggregation

Raw judgments must always be retained. A release should derive aggregate labels from a documented, versioned rule rather than overwriting individual votes.

### Pilot

Use at least two independent votes per candidate.

### Production

Three votes per candidate are preferable for ambiguous forms if volunteer capacity permits. A dynamic policy can request an additional vote only when the first two annotators disagree.

### Provisional acceptance policy

This is a candidate policy to test during the pilot, not yet a frozen benchmark rule:

- semantic validity: require strong/unanimous Q1 agreement among completed votes;
- Roman typing positive: majority `Yes` among Q1=`Yes` votes;
- Roman typing controlled negative: majority `No` while semantic validity remains accepted;
- semantic disagreement: adjudicate or exclude;
- excessive Q2 disagreement: retain as an ambiguity set or exclude from the primary score.

Thresholds should be frozen before examining private-test model leaderboard results.

## 10. Quality-control analysis

The eventual paper should report annotation quality rather than only stating that humans reviewed the data.

Pilot metrics implemented in the repository include:

- annotation count;
- skip count/rate;
- unique tasks and semantic families observed;
- pairwise Q1 agreement;
- pairwise Q2 agreement **only among Q1=`Yes` judgments**;
- count/rate of `Meaning=Yes, Typing=No` judgments;
- task-level Q1 disagreement list;
- task-level Q2 disagreement list.

With two annotators, pairwise agreement is the fraction of doubly annotated items where labels match. The implementation generalizes to more annotators by comparing all within-task label pairs.

For a larger paper dataset, also consider:

- Cohen's kappa for appropriate two-annotator subsets;
- Fleiss' kappa or Krippendorff's alpha for multi-annotator subsets;
- disagreement by source stratum;
- disagreement by variation type;
- percentage of synthetic candidates rejected for semantic mismatch;
- percentage of semantically correct candidates rejected for typing implausibility.

Do not report one aggregate agreement value as if Q1 and Q2 measured the same construct.

## 11. Generator calibration using existing permissive data

A major methodological goal is to avoid evaluating only the spelling space invented by the synthetic generator.

For each audited real Kannada/Roman source:

1. normalize without erasing meaningful spelling distinctions;
2. map Kannada/Roman pairs to semantic families;
3. measure character/morpheme correspondence patterns;
4. identify recurring Roman variants;
5. estimate transformation frequency where data volume permits;
6. use observed transformations to define generator rules;
7. reserve at least one independent source or held-out partition to compare generator output against real Roman text.

Possible diagnostics include:

- character n-gram distribution distance;
- edit-operation distributions;
- vowel-deletion frequency;
- consonant/aspiration spelling alternatives;
- token-length ratios;
- lexical/morpheme contraction patterns;
- coverage of major variation patterns in held-out human Roman forms.

A held-out real-data check is important evidence against generator-support bias.

## 12. Existing data and re-annotation

Re-annotation is intentional, not redundant.

A dataset may certify that a Roman form is a transliteration without telling us whether:

- it preserves the exact benchmark sentence meaning;
- it resembles how Kannada speakers type with English letters;
- it is formal transliteration rather than everyday Roman Kannada;
- it is a source artifact or generated form.

RomanBench therefore retains original provenance and adds its own task-specific human judgments.

No top-level dataset license badge alone is sufficient to approve a source. Exact subset, upstream origin, redistribution rights, and derivative-use permissions must be documented in the source registry/audit.

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
- `public_test`: public inputs for reproducible model comparisons;
- `private_test`: hidden fresh-content evaluation for leaderboard integrity;
- `diagnostic`: curated variation categories and controlled negatives.

## 15. Benchmark evaluation metrics

Human Yes/No annotation is a **data-construction mechanism**, not the headline LLM benchmark task.

RomanBench should evaluate models on validated Roman inputs through tasks such as:

### Roman-to-Kannada normalization

Given validated Roman Kannada, recover the corresponding Kannada-script form while preserving meaning.

### Matched semantic robustness

Run the same semantic task using:

1. the Kannada-script control;
2. a validated Roman variant of the same semantic family.

Report the Kannada-script score, Roman score, and robustness gap.

### Recommended reporting

- transliteration/normalization exact or normalized accuracy;
- downstream QA/intent/instruction accuracy where labels exist;
- Kannada-script minus Roman performance gap;
- semantic-family consistency;
- worst-variant accuracy within semantic families;
- human-origin vs synthetic-validated gap;
- performance by source stratum;
- performance by typing-plausibility label;
- performance by generator/variation type;
- colloquialness/code-mix slices only when those properties are independently tagged.

An overall score can be supplied for usability, but the benchmark's research value comes from interpretable sub-scores and robustness gaps.

## 16. Annotation platform design

The annotation application is intentionally minimal:

- one Kannada sentence;
- one Roman candidate;
- Q1 Yes/No;
- if Q1=Yes, Q2 Yes/No;
- if Q1=No, immediate submit with Q2=N/A;
- Skip;
- no normal free-text response.

The interface must include the exact conceptual clarification:

> Judge only the English-letter spelling/style. Do not judge whether the Kannada sentence itself is formal or colloquial.

The platform uses pseudonymous annotator IDs. Names, email addresses, and unnecessary device/user metadata are not required for benchmark construction.

The production site can expose a local-only demo preview via `?demo=1`; demo responses remain in browser storage and are not sent to the Sheet backend.

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
- pilot/final selection seed where applicable;
- annotation instruction version;
- contribution-terms version;
- aggregation rule version;
- raw vote counts where release/privacy policy allows;
- accepted/excluded item manifest;
- semantic-family split manifest;
- hashes of release artifacts;
- model/evaluator versions for baseline results.

Changing annotation wording or interaction semantics creates a new instruction version and should not silently mix with prior judgments without analysis.

## 19. Paper-writing checklist

The eventual paper's Data/Methods section should explicitly state:

1. what RomanBench means by Romanization typing plausibility;
2. why it is distinct from colloquialness and code mixing;
3. why Q2 is conditional on semantic preservation;
4. source strata and exact counts;
5. source licenses/provenance and filtering;
6. synthetic-generation rules and how real data calibrated them;
7. exact annotator-facing questions;
8. annotator assignment and independence rules;
9. number of votes per item and aggregation thresholds;
10. Q1 and conditional-Q2 agreement/disagreement statistics;
11. skip rate and `Meaning=Yes/Typing=No` rate;
12. contamination controls and public/private split rationale;
13. distribution and generator-bias limitations;
14. benchmark task definitions and robustness-gap metrics;
15. model baselines and inference settings;
16. release/version hashes and reproducibility artifacts.

## 20. Known limitations to preserve for the paper

Do not lose these limitations during development:

- Kannada Romanization has no single universally accepted informal spelling standard.
- Individual speakers may strongly prefer different valid spellings.
- Binary typing-plausibility judgments compress a graded phenomenon.
- Volunteer annotators known to the project may not represent all Kannada-speaking regions, ages, or dialects.
- Existing public Roman datasets may have pretraining contamination.
- Synthetic generation can encode its own support bias.
- A low-friction validation protocol measures acceptance of shown candidates; it does not by itself reveal every form a speaker might spontaneously author.
- Formal Kannada, colloquial Kannada, and Kannada-English code mixing have different distributions and should not be treated as interchangeable.

These are not reasons to avoid the benchmark; they are reasons to preserve source/annotation metadata, maintain a smaller independently authored calibration sample, and report stratified results.
