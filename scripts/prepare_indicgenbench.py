#!/usr/bin/env python3
"""Prepare Kannada IndicGenBench examples as a stable JSONL inference contract."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / ".external" / "indicgenbench"

TASK_FILES = {
    "crosssum": "crosssum_in/crosssum_english-kn_{split}.json",
    "flores_en_kn": "flores_in/flores_en_kn_{split}.json",
    "flores_kn_en": "flores_in/flores_kn_en_{split}.json",
    "xquad": "xquad_in/xquad_kn_{split}.json",
    "xorqa": "xorqa_in/xorqa_kn_{split}.json",
}


def prompt_for(task: str, ex: dict) -> tuple[str, list[str]]:
    if task == "crosssum":
        return ("ಕೆಳಗಿನ ಇಂಗ್ಲಿಷ್ ಲೇಖನವನ್ನು ಸಂಕ್ಷಿಪ್ತವಾಗಿ ಕನ್ನಡದಲ್ಲಿ ಸಾರಾಂಶ ಮಾಡಿ.\n\n" + ex["text"], [ex["summary"]])
    if task.startswith("flores_"):
        instruction = "ಈ ಇಂಗ್ಲಿಷ್ ವಾಕ್ಯವನ್ನು ಕನ್ನಡಕ್ಕೆ ಅನುವಾದಿಸಿ." if task == "flores_en_kn" else "ಈ ಕನ್ನಡ ವಾಕ್ಯವನ್ನು ಇಂಗ್ಲಿಷ್‌ಗೆ ಅನುವಾದಿಸಿ."
        return f"{instruction}\n\n{ex['source']}", [ex["target"]]
    if task == "xquad":
        refs = [a["text"] for a in ex["answers"]]
        return f"ಸಂದರ್ಭ:\n{ex['context']}\n\nಪ್ರಶ್ನೆ: {ex['question']}\nಉತ್ತರ:", refs
    if task == "xorqa":
        refs = [a["text"] for a in ex.get("translated_answers", [])] + [a["text"] for a in ex["answers"]]
        return f"Context:\n{ex['context']}\n\nಪ್ರಶ್ನೆ: {ex['question']}\nಉತ್ತರ:", refs
    raise ValueError(task)


def prepare(task: str, split: str, output: Path) -> None:
    source = UPSTREAM / TASK_FILES[task].format(split=split)
    if not source.exists():
        raise SystemExit(f"Missing {source}. Run: make bootstrap-external")
    payload = json.loads(source.read_text(encoding="utf-8"))
    canary = payload.get("canary")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as f:
        for i, ex in enumerate(payload["examples"]):
            prompt, refs = prompt_for(task, ex)
            row = {
                "id": ex.get("id", f"{task}-{split}-{i}"),
                "benchmark": "IndicGenBench",
                "track": task,
                "language": "kn",
                "split": split,
                "prompt": prompt,
                "references": refs,
                "canary": canary,
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"Wrote {output}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", choices=TASK_FILES, required=True)
    parser.add_argument("--split", default="dev")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or ROOT / "data" / "external" / "indicgenbench" / f"{args.task}-{args.split}.jsonl"
    prepare(args.task, args.split, output)


if __name__ == "__main__":
    main()
