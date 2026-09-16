#!/usr/bin/env python3
"""Analyze exported RomanBench pilot annotations."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from kannadallmbench.pilot import analyze_annotations, disagreement_rows, read_annotations_csv


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("annotations", type=Path)
    parser.add_argument("--output", type=Path, default=Path("data/interim/romanbench/pilot-analysis.json"))
    parser.add_argument(
        "--disagreements-output",
        type=Path,
        default=Path("data/interim/romanbench/pilot-disagreements.csv"),
    )
    args = parser.parse_args()

    rows = read_annotations_csv(args.annotations)
    summary = analyze_annotations(rows)
    disagreements = disagreement_rows(rows)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    args.disagreements_output.parent.mkdir(parents=True, exist_ok=True)
    fields = ("task_id", "semantic_family_id", "dimension", "labels", "annotators")
    with args.disagreements_output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(disagreements)

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"disagreements={len(disagreements)} output={args.disagreements_output}")


if __name__ == "__main__":
    main()
