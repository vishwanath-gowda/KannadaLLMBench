# Initial Kannada data-source audit

This file records why candidate sources are approved or review-gated. The machine-readable status lives in `config/data_sources.yaml`.

## IndicCorpV2 Kannada — approved

- Dataset: `ai4bharat/IndicCorpV2`
- Pinned metadata revision: `984b75b20ce408f9ba27c6558e9279e8e1b6edfd`
- Kannada split: `kan_Knda`
- Pinned file mapping: `data/kn.txt`
- Declared dataset license: CC0
- Paper: ACL 2023, *Towards Leaving No Indic Language Behind*

The pinned dataset card explicitly maps the Kannada split and states that datasets created by the work are released under CC0. This is the preferred default source for Kannada corpus experiments.

## Aya Collection — review required

- Dataset: `CohereLabs/aya_collection`
- Hub license: Apache-2.0
- Scope: multilingual instruction collection assembled from many underlying datasets and templated/transformed sources

The top-level license is permissive, but provenance is composite. Approve a specific Kannada subcollection only after tracing the exact upstream dataset(s) represented in that slice.

## English-Kannada Cleaned — review required

- Dataset: `ramachandrajoshi/english-kannada-cleaned`
- Hub license: Apache-2.0
- Scope: cleaned English-Kannada parallel pairs

The card describes the cleaned data and license but does not provide a sufficiently strong upstream-source chain for default inclusion. Keep review-gated until original sentence-pair provenance is established.

## Aksharantar — review required / partition before use

- Dataset: `ai4bharat/Aksharantar`
- Scope: Indic transliteration pairs, including Kannada
- Licensing: source-dependent; the dataset card distinguishes manually collected CC-BY data from mined/existing CC0 data

Do not ingest the repository wholesale. A future RomanBench pipeline may select only a clearly licensed source partition after validating current files/metadata against the paper and retaining the row-level source field.

## Approval rule

A source moves to `approved` only through a PR that records immutable revision, exact subset, license basis, provenance, redistribution rights, and benchmark-overlap risk.
