# KanMixBench integration

KanMixBench remains an independent project with a narrower research identity: controlled Kannada-English code mixing, script variation, Romanization, and morphology. KannadaLLMBench will consume a versioned KanMixBench release as one native benchmark track rather than duplicating its data or governance.

Integration requirements:

1. pin an immutable KanMixBench release/tag
2. import only its public evaluation interface, not private/raw collection data
3. preserve KanMixBench metrics and attribution
4. map its summary metrics into the KannadaLLMBench result envelope
5. never use its test semantic families in Kannada model training

Until KanMixBench publishes a stable release, KannadaLLMBench documents the interface but does not vendor benchmark content.
