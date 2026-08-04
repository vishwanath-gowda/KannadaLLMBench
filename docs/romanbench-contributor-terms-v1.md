# RomanBench contributor terms v1

Identifier: `romanbench-contributor-v1`

These terms apply to original Kannada controls and human Romanizations contributed through the RomanBench human-collection workflow.

By entering `yes` for `terms_accepted`, a contributor confirms that:

1. the submitted text is their own contribution and they have the right to contribute it;
2. they are not copying a sentence or Romanization from a book, website, dataset, private conversation, or other third-party source;
3. the submission does not intentionally contain private personal information, credentials, account identifiers, or other sensitive information;
4. they dedicate their contribution under **CC0 1.0 Universal** (`CC0-1.0`), including CC0's fallback license where a public-domain dedication is not effective;
5. the contribution may be redistributed, modified, used in benchmarks, and used to train or evaluate machine-learning systems, including commercial systems;
6. the project may reject, edit, normalize, or exclude the submission and is not required to publish it.

## Original Kannada authoring

Authors should write new, self-contained Kannada sentences from their own imagination or everyday knowledge. Avoid quotations, lyrics, recognizable passages, confidential workplace text, and copied social-media messages.

Use a pseudonymous `author_id`. The collection files should not request or store names, email addresses, phone numbers, or account IDs merely to attribute a benchmark row.

## Independent Romanization

Romanizers should write how they would naturally type the supplied Kannada sentence using Latin/Roman script. They should not consult the generated IAST/ASCII controls or another contributor's Romanization while producing their answer.

Entering `yes` for `independent_confirmation` means the Romanizer created the spelling independently from the Kannada control supplied for the task.

## Review metadata

`pii_reviewed=yes` records the contributor/reviewer assertion that the text does not contain unnecessary personal information. It is a data-quality field, not a guarantee that automated or human privacy review can never miss something.

## Versioning

These terms are versioned. A future change to the contribution terms must use a new identifier rather than silently changing the meaning of `romanbench-contributor-v1` for already collected rows.

CC0 reference: https://creativecommons.org/publicdomain/zero/1.0/
