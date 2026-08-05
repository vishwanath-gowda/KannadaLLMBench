# RomanBench validation annotation terms v1

Identifier: `romanbench-validation-v1`

These terms apply to the low-friction Yes/No/Skip judgments collected through the RomanBench annotation website. They are separate from `romanbench-contributor-v1`, which covers newly authored Kannada sentences and independently typed Romanizations.

By choosing **Start annotating** after these terms are shown, a contributor confirms that:

1. their answers reflect their own Kannada-language judgment;
2. they will not use a transliteration service, LLM, search engine, another person's answer, or other external aid while judging an item;
3. they understand that the project may store their responses under a pseudonymous annotator ID;
4. they dedicate their annotation labels and related non-identifying contribution metadata under **CC0 1.0 Universal** (`CC0-1.0`), including CC0's fallback license where a public-domain dedication is not effective;
5. their judgments may be redistributed, analyzed, included in benchmark releases and papers, and used to train or evaluate machine-learning systems, including commercial systems;
6. participation is voluntary, and they may stop annotating at any time;
7. the project may exclude or adjudicate annotations and is not required to publish any individual response.

## Data minimization

The normal validation workflow does not request a name, email address, phone number, demographic profile, or free-text response. A random/pseudonymous annotator ID is sufficient for independence and agreement analysis.

The website may receive ordinary network metadata from GitHub Pages and Google Apps Script as part of serving HTTP requests. KannadaLLMBench does not intentionally copy browser user-agent, IP-address, location, or similar device/network metadata into its annotation table.

## Versioning

The frontend records this identifier with each submitted annotation. Any substantive change to the contributor terms must use a new identifier rather than silently changing the terms associated with existing judgments.

CC0 reference: https://creativecommons.org/publicdomain/zero/1.0/
