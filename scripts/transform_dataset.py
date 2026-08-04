#!/usr/bin/env python3
"""Apply conservative text normalization and optional exact deduplication to JSONL."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from kannadallmbench.pipelines.dedup import deduplicate_records  # noqa: E402
from kannadallmbench.pipelines.io import read_jsonl, write_jsonl  # noqa: E402
from kannadallmbench.pipelines.transforms import normalize_record  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--text-field", action="append", required=True, dest="text_fields")
    parser.add_argument("--dedup-field")
    args = parser.parse_args()
    records = (normalize_record(row, tuple(args.text_fields)) for row in read_jsonl(args.input))
    if args.dedup_field:
        records = deduplicate_records(records, args.dedup_field)
    count, size = write_jsonl(records, args.output)
    print(f"wrote {count:,} records / {size / 1024 / 1024:.2f} MiB -> {args.output}")


if __name__ == "__main__":
    main()
