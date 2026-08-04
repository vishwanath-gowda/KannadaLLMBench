#!/usr/bin/env python3
"""Export accepted original Kannada controls for independent human Romanization."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

from kannadallmbench.pipelines.romanbench_human import (
    is_unused_authoring_row,
    romanization_task_rows,
    validate_authoring_row,
)

DEFAULT_OUTPUT = Path("data/interim/romanbench/human_romanization_tasks.csv")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("authoring_csv", type=Path)
    parser.add_argument("--copies", type=int, default=2)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    accepted: list[dict[str, str]] = []
    errors: list[str] = []
    with args.authoring_csv.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for line_number, row in enumerate(reader, start=2):
            if is_unused_authoring_row(row):
                continue
            row_errors = validate_authoring_row(row, line_number)
            errors.extend(row_errors)
            if not row_errors and row.get("review_decision", "").strip().lower() == "accept":
                accepted.append(row)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit("Fix authoring validation errors before exporting Romanization tasks")
    if not accepted:
        raise SystemExit("No accepted authoring rows found")

    tasks = romanization_task_rows(accepted, copies=args.copies)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(tasks[0]))
        writer.writeheader()
        writer.writerows(tasks)
    print(f"families={len(accepted)} tasks={len(tasks)} output={args.output}")


if __name__ == "__main__":
    main()
