#!/usr/bin/env python3
"""Build a reproducible local JSONL artifact from an approved registry source."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from kannadallmbench.data_registry import load_data_sources  # noqa: E402
from kannadallmbench.pipelines.build import BuildConfig, build_jsonl_from_hf  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="key from config/data_sources.yaml")
    parser.add_argument("--registry", type=Path, default=ROOT / "config" / "data_sources.yaml")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--text-field", action="append", required=True, dest="text_fields")
    parser.add_argument("--dedup-field")
    parser.add_argument("--records", type=int)
    parser.add_argument("--mb", type=float)
    parser.add_argument("--allow-unreviewed", action="store_true")
    args = parser.parse_args()
    sources = load_data_sources(args.registry)
    if args.source not in sources:
        raise SystemExit(f"unknown source {args.source!r}; run make data-sources")
    config = BuildConfig(
        output=args.output,
        text_fields=tuple(args.text_fields),
        dedup_field=args.dedup_field,
        max_records=args.records,
        max_bytes=None if args.mb is None else int(args.mb * 1024 * 1024),
        allow_unreviewed=args.allow_unreviewed,
    )
    count, size = build_jsonl_from_hf(sources[args.source], config)
    print(f"built {count:,} records / {size / 1024 / 1024:.2f} MiB -> {args.output}")


if __name__ == "__main__":
    main()
