#!/usr/bin/env python3
"""Validate Kannada-speaker review CSV before RomanBench candidate promotion."""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

_KANNADA_RE = re.compile(r"[\u0C80-\u0CFF]")
_ALLOWED_DECISIONS = {"accept", "reject", "hold", ""}
_REQUIRED_COLUMNS = {
    "semantic_family_id",
    "kannada_control",
    "human_roman_1",
    "human_roman_2",
    "review_decision",
    "reviewer",
    "notes",
    "source_key",
    "source_revision",
    "license_basis",
}


def validate_row(row: dict[str, str], line_number: int) -> list[str]:
    errors: list[str] = []
    family_id = row.get("semantic_family_id", "").strip()
    decision = row.get("review_decision", "").strip().lower()
    reviewer = row.get("reviewer", "").strip()
    human_variants = [row.get("human_roman_1", "").strip(), row.get("human_roman_2", "").strip()]
    human_variants = [value for value in human_variants if value]

    prefix = f"line {line_number} ({family_id or 'missing-family-id'})"
    if not family_id:
        errors.append(f"{prefix}: semantic_family_id is required")
    if decision not in _ALLOWED_DECISIONS:
        errors.append(f"{prefix}: review_decision must be accept, reject, hold, or blank")
    if decision and not reviewer:
        errors.append(f"{prefix}: reviewer is required when a decision is recorded")
    if decision == "accept" and not human_variants:
        errors.append(f"{prefix}: accepted families require at least one human Romanization")
    for value in human_variants:
        if _KANNADA_RE.search(value):
            errors.append(f"{prefix}: human Romanization must use Latin/Roman script, found Kannada characters")
    if len(human_variants) == 2 and human_variants[0] == human_variants[1]:
        errors.append(f"{prefix}: human_roman_1 and human_roman_2 should not duplicate each other")
    if not row.get("source_key", "").strip() or not row.get("license_basis", "").strip():
        errors.append(f"{prefix}: source/license provenance is required")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("review_csv", type=Path)
    args = parser.parse_args()

    errors: list[str] = []
    counts = {"accept": 0, "reject": 0, "hold": 0, "pending": 0}
    with args.review_csv.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = _REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise SystemExit(f"Missing required columns: {', '.join(sorted(missing))}")
        for line_number, row in enumerate(reader, start=2):
            errors.extend(validate_row(row, line_number))
            decision = row.get("review_decision", "").strip().lower()
            counts[decision or "pending"] += 1

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(f"Review validation failed with {len(errors)} error(s)")

    print("review validation passed")
    print(" ".join(f"{key}={value}" for key, value in counts.items()))


if __name__ == "__main__":
    main()
