#!/usr/bin/env python3
"""Check exact normalized text overlap between training and benchmark JSONL files."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from kannadallmbench.contamination import exact_overlap_count  # noqa: E402
from kannadallmbench.pipelines.io import read_jsonl  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training", type=Path, required=True)
    parser.add_argument("--benchmark", type=Path, required=True)
    parser.add_argument("--training-field", required=True)
    parser.add_argument("--benchmark-field", required=True)
    parser.add_argument("--fail-on-overlap", action="store_true")
    args = parser.parse_args()
    report = exact_overlap_count(
        read_jsonl(args.training),
        read_jsonl(args.benchmark),
        training_field=args.training_field,
        benchmark_field=args.benchmark_field,
    )
    print(
        f"training={report.training_records} benchmark={report.benchmark_records} "
        f"exact_overlaps={report.exact_overlaps}"
    )
    if args.fail_on_overlap and report.exact_overlaps:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
