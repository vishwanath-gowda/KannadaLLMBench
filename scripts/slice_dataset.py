#!/usr/bin/env python3
"""Stream a Hugging Face dataset and save a small JSONL slice by records and/or MiB."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from kannadallmbench.pipelines.hf import stream_hf_dataset  # noqa: E402
from kannadallmbench.pipelines.io import write_jsonl  # noqa: E402
from kannadallmbench.pipelines.slice import slice_records  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", help="Hugging Face dataset id, e.g. ai4bharat/IndicCorpV2")
    parser.add_argument("--config", dest="config_name")
    parser.add_argument("--split", default="train")
    parser.add_argument("--revision")
    parser.add_argument("--data-dir")
    parser.add_argument("--records", type=int)
    parser.add_argument("--mb", type=float, help="Maximum encoded JSONL size in MiB")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.records is None and args.mb is None:
        parser.error("provide --records and/or --mb")
    max_bytes = None if args.mb is None else int(args.mb * 1024 * 1024)
    stream = stream_hf_dataset(
        args.dataset,
        config_name=args.config_name,
        split=args.split,
        revision=args.revision,
        data_dir=args.data_dir,
    )
    selected = slice_records(stream, max_records=args.records, max_bytes=max_bytes)
    count, size = write_jsonl(selected, args.output)
    print(f"wrote {count:,} records / {size / 1024 / 1024:.2f} MiB -> {args.output}")


if __name__ == "__main__":
    main()
