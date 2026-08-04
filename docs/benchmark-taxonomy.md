# Benchmark taxonomy

KannadaLLMBench has two layers.

## External reference tracks

These establish comparability with prior work and keep their original names and evaluation contracts:

- MILU Kannada — knowledge/reasoning
- IndicIFEval Kannada — verifiable instruction following
- IndicGenBench Kannada — translation, QA, summarization

## Kannada-native tracks

These target gaps that broad multilingual suites do not measure well:

| Track | Primary question |
|---|---|
| RomanBench | Can the model understand naturally Romanized Kannada despite spelling variation? |
| ColloquialBench | Can it understand and produce natural spoken-style Kannada? |
| KanMixBench | Is behavior robust to Kannada-English language/script mixing? |
| CultureBench | Does it understand Karnataka-specific cultural and contextual knowledge? |
| ConversationBench | Are responses natural, useful, and preferred by Kannada speakers? |

Every native track must define task contract, source/provenance policy, human review protocol, split policy, metrics, contamination controls, and a versioned schema before test data is frozen.
