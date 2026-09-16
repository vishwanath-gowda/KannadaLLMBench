#!/usr/bin/env python3
"""Build a deterministic one-candidate-per-family RomanBench pilot task CSV."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kannadallmbench.annotation_tasks import read_jsonl, write_tasks_csv
from kannadallmbench.pilot import DEFAULT_VARIANT_ORDER, select_pilot_tasks, variant_counts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--families", type=int, default=30)
    parser.add_argument("--batch", default="pilot-v1")
    parser.add_argument("--target-votes", type=int, default=2)
    parser.add_argument("--seed", default="romanbench-pilot-v1")
    parser.add_argument(
        "--variant-order",
        default=",".join(DEFAULT_VARIANT_ORDER),
        help="Comma-separated controlled variant preference cycle",
    )
    args = parser.parse_args()

    variant_order = tuple(value.strip() for value in args.variant_order.split(",") if value.strip())
    tasks = select_pilot_tasks(
        read_jsonl(args.input),
        families=args.families,
        batch_id=args.batch,
        target_votes=args.target_votes,
        seed=args.seed,
        variant_order=variant_order,
    )
    count = write_tasks_csv(tasks, args.output)

    manifest = {
        "pilot_version": "romanbench-pilot-v1",
        "input": str(args.input),
        "output": str(args.output),
        "families": count,
        "batch_id": args.batch,
        "target_votes": args.target_votes,
        "seed": args.seed,
        "variant_order": list(variant_order),
        "variant_counts": variant_counts(tasks),
    }
    manifest_path = args.output.with_suffix(args.output.suffix + ".manifest.json")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
