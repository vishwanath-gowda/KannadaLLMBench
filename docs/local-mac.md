# Local Apple Silicon baseline workflow

The first recommended local baseline is `mlx-community/Qwen3-4B-Instruct-2507-4bit`, an MLX conversion of the Apache-2.0 `Qwen/Qwen3-4B-Instruct-2507` model.

## Install

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e '.[mlx,metrics]'
```

## Generate predictions

Prepare any backend-neutral benchmark JSONL whose rows contain a `prompt` field, then run:

```bash
python scripts/generate_predictions.py \
  --backend mlx \
  --model mlx-community/Qwen3-4B-Instruct-2507-4bit \
  --input data/external/indicgenbench/xquad-dev.jsonl \
  --output results/qwen3-4b-mlx/xquad-predictions.jsonl
```

The runner preserves every input field and appends `prediction`, allowing the existing IndicGenBench scorer to consume the output.

## Why this is a baseline, not a tuned model

Always score the untouched model before fine-tuning. Store the model ID/revision and result artifacts so later Kannada CPT/SFT/QLoRA experiments can be compared against an unchanged baseline. Never train on the external benchmark JSONL used here.
