#!/usr/bin/env python3
"""Validate original Kannada controls before independent Romanization."""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

from kannadallmbench.pipelines.romanbench_human import is_unused_authoring_row, validate_authoring_row


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("authoring_csv", type=Path)
    args = parser.parse_args()

    errors: list[str] = []
    decisions: Counter[str] = Counter()
    with args.authoring_csv.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for line_number, row in enumerate(reader, start=2):
            if is_unused_authoring_row(row):
                continue
            errors.extend(validate_authoring_row(row, line_number))
            decisions[row.get("review_decision", "").strip().lower() or "pending"] += 1

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(f"Authoring validation failed with {len(errors)} error(s)")

    print("authoring validation passed")
    print(" ".join(f"{key}={value}" for key, value in sorted(decisions.items())))


if __name__ == "__main__":
    main()
