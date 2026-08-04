#!/usr/bin/env python3
"""Generate predictions for backend-neutral JSONL benchmark prompts using MLX on Apple Silicon."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def run_mlx(model_id: str, input_path: Path, output_path: Path, max_tokens: int) -> None:
    try:
        from mlx_lm import generate, load
    except ImportError as exc:
        raise SystemExit("MLX backend requires: pip install -e '.[mlx]'") from exc

    model, tokenizer = load(model_id)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with input_path.open("r", encoding="utf-8") as source, output_path.open("w", encoding="utf-8") as target:
        for line_number, line in enumerate(source, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            prompt = row.get("prompt")
            if not isinstance(prompt, str):
                raise ValueError(f"{input_path}:{line_number} has no string 'prompt' field")
            rendered = prompt
            if getattr(tokenizer, "chat_template", None) is not None:
                rendered = tokenizer.apply_chat_template(
                    [{"role": "user", "content": prompt}],
                    add_generation_prompt=True,
                    tokenize=False,
                )
            prediction = generate(model, tokenizer, prompt=rendered, max_tokens=max_tokens, verbose=False)
            row["prediction"] = prediction
            target.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", choices=["mlx"], default="mlx")
    parser.add_argument("--model", required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-tokens", type=int, default=1024)
    args = parser.parse_args()
    if args.backend == "mlx":
        run_mlx(args.model, args.input, args.output, args.max_tokens)


if __name__ == "__main__":
    main()
