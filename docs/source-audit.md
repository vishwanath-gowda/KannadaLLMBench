# Initial Kannada data-source audit

This file records why candidate sources are approved or review-gated. The machine-readable status lives in `config/data_sources.yaml`.

## IndicCorpV2 Kannada — approved

- Dataset: `ai4bharat/IndicCorpV2`
- Pinned metadata revision: `984b75b20ce408f9ba27c6558e9279e8e1b6edfd`
- Kannada split: `kan_Knda`
- Pinned file mapping: `data/kn.txt`
- Declared dataset license: CC0
- Paper: ACL 2023, *Towards Leaving No Indic Language Behind*

The pinned dataset card explicitly maps the Kannada split and states that datasets created by the work are released under CC0. This is the preferred default source for Kannada corpus experiments and the first RomanBench controlled-candidate construction pipeline.

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
- Scope: approximately 26M Indic-script/Roman transliteration pairs across 20 languages, including Kannada
- Row metadata includes a `source` field
- Current card licensing statement:
  - manually collected data: CC BY
  - mined data from Samanantar and IndicCorp: CC0
  - existing-source data: CC0

The dataset card also states that AI4Bharat does not own the underlying text from which mined data was extracted and licenses the packaging of mined data under CC0. Because the aggregate dataset mixes source classes, KannadaLLMBench does **not** approve it wholesale even though some row classes are permissively licensed.

A future Aksharantar integration must:

1. pin an immutable dataset revision;
2. preserve the row-level `source` field;
3. explicitly whitelist source classes whose license/provenance basis has been reviewed;
4. record the resulting subset definition in the manifest;
5. avoid claiming that repository-level licensing transfers ownership of upstream text.

Source reviewed: `https://huggingface.co/datasets/ai4bharat/Aksharantar`.

## Transliteration implementation dependency — approved for code use

RomanBench controlled variants use the `indic-transliteration` Python package for Kannada-script to IAST conversion. PyPI identifies the package as MIT licensed. The package is an implementation dependency, not benchmark source data; RomanBench still records the license/provenance of the underlying Kannada sentence independently.

Package: `https://pypi.org/project/indic-transliteration/`.

## Approval rule

A source moves to `approved` only through a PR that records immutable revision, exact subset, license basis, provenance, redistribution rights, and benchmark-overlap risk.
