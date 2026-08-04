# RomanBench human-authored collection

This workflow is the preferred source path for a future contamination-resistant RomanBench private test set. It is intentionally separate from the public-corpus controlled-candidate pipeline.

## Why two stages

A private benchmark should not quietly inherit semantic content from a widely available pretraining corpus. RomanBench therefore separates:

1. **original Kannada authoring** — contributors create new self-contained Kannada controls; and
2. **independent Romanization** — different Kannada speakers naturally Romanize accepted controls without seeing synthetic suggestions.

This provides new semantic content plus natural spelling variation while keeping contributor provenance auditable.

## Privacy model

Use pseudonymous contributor IDs such as `author-017` or `romanizer-042`. Do not collect names, email addresses, phone numbers, account identifiers, or other unnecessary personal data in benchmark rows.

Every contributor uses the versioned [`romanbench-contributor-v1`](romanbench-contributor-terms-v1.md) terms and contributes under CC0-1.0.

## Stage 1 — author new Kannada controls

Create a local authoring sheet:

```bash
make romanbench-authoring-template AUTHORING_ROWS=250
```

For each used row, fill:

- `kannada_control`: newly authored Kannada sentence;
- `domain`: `daily_life`, `workplace`, `commerce`, `travel`, `education`, `public_services`, `culture`, or `other`;
- `author_id`: pseudonymous contributor ID;
- `terms_accepted=yes`;
- `original_work_confirmation=yes`;
- `pii_reviewed=yes`.

A separate reviewer can set `review_decision` to `accept`, `reject`, or `hold` and record a pseudonymous `reviewer_id`.

Validate:

```bash
make romanbench-authoring-validate
```

Unused preallocated rows are ignored. Partially completed rows fail validation.

## Stage 2 — independent natural Romanization

Export two Romanization slots for every accepted Kannada control:

```bash
make romanbench-human-romanization-export
```

Do **not** include generated IAST/ASCII suggestions in this task sheet. A Romanizer sees the Kannada control and writes the Latin-script spelling they would naturally use.

For each task, fill:

- `romanizer_id`: pseudonymous ID different from the Kannada author;
- `romanization`;
- `terms_accepted=yes`;
- `independent_confirmation=yes`;
- `pii_reviewed=yes`.

Validate:

```bash
make romanbench-human-romanization-validate
```

By default each family needs two completed Romanizations from two distinct Romanizers. Duplicate spellings are flagged for re-authoring because the collection goal is independent variation rather than repeated copying.

## Stable family identity

Human-authored semantic-family IDs are deterministic hashes of normalized Kannada controls under the namespace `romanbench-human-v1`. The ID does not contain contributor identity.

## Private-test eligibility

Passing these CSV validators is **necessary but not sufficient** for private-test release. Before freezing a family:

- perform human naturalness/semantic-equivalence review;
- deduplicate against other authored families;
- run available overlap checks against training corpora and public benchmark material;
- group the complete semantic family into one split;
- keep answer-bearing private-test files out of the public repository;
- record the final versioned release manifest.

Public-corpus-derived controlled candidates from IndicCorpV2 remain valuable for development and spelling-robustness analysis, but this human-authored path is preferred for hidden leaderboard evaluation.
