#!/usr/bin/env python3
"""Create a blank CSV for original Kannada RomanBench semantic-family authoring."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

from kannadallmbench.pipelines.romanbench_human import authoring_template_row

DEFAULT_OUTPUT = Path("data/interim/romanbench/human_authoring.csv")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=250)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.rows <= 0:
        raise SystemExit("--rows must be > 0")

    rows = [authoring_template_row(index) for index in range(1, args.rows + 1)]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"rows={len(rows)} output={args.output}")


if __name__ == "__main__":
    main()
