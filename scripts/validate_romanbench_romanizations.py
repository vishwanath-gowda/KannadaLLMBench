#!/usr/bin/env python3
"""Validate independent human Romanizations for RomanBench private-test candidates."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

from kannadallmbench.pipelines.romanbench_human import validate_romanization_rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("romanization_csv", type=Path)
    args = parser.parse_args()

    with args.romanization_csv.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    errors = validate_romanization_rows(rows)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(f"Romanization validation failed with {len(errors)} error(s)")
    print(f"romanization validation passed rows={len(rows)}")


if __name__ == "__main__":
    main()
