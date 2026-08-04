#!/usr/bin/env python3
"""Export RomanBench candidate families into a Kannada-speaker review CSV."""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

DEFAULT_INPUT = Path("data/interim/romanbench/candidates.jsonl")
DEFAULT_OUTPUT = Path("data/interim/romanbench/review.csv")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise SystemExit(f"Invalid JSON at {path}:{line_number}: {exc}") from exc
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in read_jsonl(args.input):
        grouped[row["semantic_family_id"]].append(row)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "semantic_family_id",
        "kannada_control",
        "iast",
        "ascii_phonemic",
        "ascii_relaxed",
        "human_roman_1",
        "human_roman_2",
        "review_decision",
        "reviewer",
        "notes",
        "source_key",
        "source_revision",
        "license_basis",
    ]
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for family_id in sorted(grouped):
            family = grouped[family_id]
            first = family[0]
            variants = {row["variant_type"]: row["roman_input"] for row in family}
            provenance = first["provenance"]
            writer.writerow(
                {
                    "semantic_family_id": family_id,
                    "kannada_control": first["kannada_control"],
                    "iast": variants.get("iast", ""),
                    "ascii_phonemic": variants.get("ascii_phonemic", ""),
                    "ascii_relaxed": variants.get("ascii_relaxed", ""),
                    "human_roman_1": "",
                    "human_roman_2": "",
                    "review_decision": "",
                    "reviewer": "",
                    "notes": "",
                    "source_key": provenance["source_key"],
                    "source_revision": provenance["source_revision"] or "",
                    "license_basis": provenance["license_basis"],
                }
            )

    print(f"families={len(grouped)} review_csv={args.output}")


if __name__ == "__main__":
    main()
