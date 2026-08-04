#!/usr/bin/env python3
"""Score IndicGenBench prediction JSONL files."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import unicodedata


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).strip().lower()
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return " ".join(text.split())


def exact_match(pred: str, refs: list[str]) -> float:
    p = normalize(pred)
    return float(any(p == normalize(r) for r in refs))


def token_f1(pred: str, refs: list[str]) -> float:
    p = normalize(pred).split()
    best = 0.0
    for ref in refs:
        r = normalize(ref).split()
        if not p and not r:
            best = max(best, 1.0)
            continue
        common = Counter(p) & Counter(r)
        n = sum(common.values())
        if n == 0:
            continue
        precision = n / len(p)
        recall = n / len(r)
        best = max(best, 2 * precision * recall / (precision + recall))
    return best


def rouge_l_f1(pred: str, ref: str) -> float:
    a, b = normalize(pred).split(), normalize(ref).split()
    if not a or not b:
        return float(a == b)
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0]
        for j, y in enumerate(b, 1):
            cur.append(prev[j - 1] + 1 if x == y else max(prev[j], cur[-1]))
        prev = cur
    lcs = prev[-1]
    p, r = lcs / len(a), lcs / len(b)
    return 0.0 if p + r == 0 else 2 * p * r / (p + r)


def score(path: Path, task: str) -> dict:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows:
        raise SystemExit("Prediction file is empty")
    for row in rows:
        if "prediction" not in row or "references" not in row:
            raise SystemExit("Every row needs prediction and references")
    if task in {"xquad", "xorqa"}:
        em = sum(exact_match(r["prediction"], r["references"]) for r in rows) / len(rows)
        f1 = sum(token_f1(r["prediction"], r["references"]) for r in rows) / len(rows)
        return {"exact_match": em, "token_f1": f1, "num_examples": len(rows)}
    if task == "crosssum":
        rouge = sum(max(rouge_l_f1(r["prediction"], ref) for ref in r["references"]) for r in rows) / len(rows)
        return {"rouge_l_f1": rouge, "num_examples": len(rows)}
    if task.startswith("flores_"):
        try:
            import sacrebleu  # type: ignore
        except ImportError as exc:
            raise SystemExit("Translation scoring requires: pip install -e '.[metrics]'") from exc
        preds = [r["prediction"] for r in rows]
        refs = [[r["references"][0] for r in rows]]
        return {"sacrebleu": sacrebleu.corpus_bleu(preds, refs).score, "chrf": sacrebleu.corpus_chrf(preds, refs).score, "num_examples": len(rows)}
    raise ValueError(task)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True, choices=["crosssum", "flores_en_kn", "flores_kn_en", "xquad", "xorqa"])
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = score(args.predictions, args.task)
    text = json.dumps({"benchmark": "IndicGenBench", "track": args.task, **result}, indent=2, ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
