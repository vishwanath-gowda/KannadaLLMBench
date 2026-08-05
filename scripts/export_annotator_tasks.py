#!/usr/bin/env python3
"""Export Kannada/Roman pairs into the Google Sheet Tasks schema."""
from __future__ import annotations

import argparse
from pathlib import Path

from kannadallmbench.annotation_tasks import (
    pair_to_task,
    read_jsonl,
    romanbench_candidate_to_task,
    write_tasks_csv,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--mode", choices=("romanbench", "pairs"), default="romanbench")
    parser.add_argument("--batch", default="pilot")
    parser.add_argument("--target-votes", type=int, default=2)
    parser.add_argument("--task-id-field", default="id")
    parser.add_argument("--family-id-field", default="semantic_family_id")
    parser.add_argument("--kannada-field", default="kannada")
    parser.add_argument("--roman-field", default="roman")
    parser.add_argument("--variant-type", default="existing_pair")
    parser.add_argument("--source-id", default="")
    args = parser.parse_args()

    source_rows = read_jsonl(args.input)
    if args.mode == "romanbench":
        tasks = (
            romanbench_candidate_to_task(row, batch_id=args.batch, target_votes=args.target_votes)
            for row in source_rows
        )
    else:
        tasks = (
            pair_to_task(
                row,
                task_id_field=args.task_id_field,
                family_id_field=args.family_id_field,
                kannada_field=args.kannada_field,
                roman_field=args.roman_field,
                batch_id=args.batch,
                target_votes=args.target_votes,
                variant_type=args.variant_type,
                source_id=args.source_id,
            )
            for row in source_rows
        )

    count = write_tasks_csv(tasks, args.output)
    print(f"tasks={count} output={args.output}")


if __name__ == "__main__":
    main()
