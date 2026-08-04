#!/usr/bin/env python3
"""Normalize lm-eval JSON output into KannadaLLMBench's stable result schema."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from kannadallmbench.results import BenchmarkResult, ResultEnvelope  # noqa: E402


def find_metric(metrics: dict) -> tuple[str, float]:
    preferred = ["acc,none", "prompt_level_strict_acc,none", "inst_level_strict_acc,none", "acc", "exact_match,none"]
    for key in preferred:
        if key in metrics and isinstance(metrics[key], (int, float)):
            return key, float(metrics[key])
    for key, value in metrics.items():
        if isinstance(value, (int, float)) and not key.endswith("_stderr"):
            return key, float(value)
    raise ValueError(f"No numeric metric found in {metrics}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", choices=["MILU", "IndicIFEval"], required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = json.loads(args.input.read_text(encoding="utf-8"))
    out: list[BenchmarkResult] = []
    for task, metrics in raw.get("results", {}).items():
        metric, value = find_metric(metrics)
        out.append(BenchmarkResult(args.benchmark, task, args.model, metric, value, details=metrics))
    ResultEnvelope.create(out).write(args.output)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
