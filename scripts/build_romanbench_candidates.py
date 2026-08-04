#!/usr/bin/env python3
"""Construct RomanBench candidate families from an approved Kannada corpus source."""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from kannadallmbench.data_registry import load_data_sources, require_approved  # noqa: E402
from kannadallmbench.pipelines.hf import stream_hf_dataset  # noqa: E402
from kannadallmbench.pipelines.manifest import sha256_file  # noqa: E402
from kannadallmbench.pipelines.romanbench import (  # noqa: E402
    RomanBenchFilter,
    construct_candidate_dataset,
)

REGISTRY = ROOT / "config" / "data_sources.yaml"
DEFAULT_OUTPUT = ROOT / "data" / "interim" / "romanbench" / "candidates.jsonl"


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    bytes_written = 0
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            line = json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"
            handle.write(line)
            bytes_written += len(line.encode("utf-8"))
    return bytes_written


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-key", default="indiccorp_v2_kannada")
    parser.add_argument("--families", type=int, default=2000)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--min-chars", type=int, default=20)
    parser.add_argument("--max-chars", type=int, default=180)
    parser.add_argument("--min-words", type=int, default=4)
    parser.add_argument("--max-words", type=int, default=30)
    parser.add_argument("--min-kannada-ratio", type=float, default=0.75)
    args = parser.parse_args()

    if args.families <= 0:
        raise SystemExit("--families must be > 0")

    sources = load_data_sources(REGISTRY)
    if args.source_key not in sources:
        raise SystemExit(f"Unknown source key: {args.source_key}")
    source = sources[args.source_key]
    require_approved(source)

    text_field = source.field_map.get("text", "text")
    config = RomanBenchFilter(
        min_chars=args.min_chars,
        max_chars=args.max_chars,
        min_words=args.min_words,
        max_words=args.max_words,
        min_kannada_ratio=args.min_kannada_ratio,
    )
    dataset = stream_hf_dataset(
        source.dataset_id,
        config_name=source.config_name,
        split=source.split or "train",
        revision=source.revision,
        data_dir=source.data_dir,
    )

    rows, stats = construct_candidate_dataset(
        dataset,
        source=source,
        text_field=text_field,
        max_families=args.families,
        config=config,
    )
    if not rows:
        raise SystemExit("No candidates produced; inspect source configuration and filters")

    bytes_written = write_jsonl(args.output, rows)
    manifest_path = args.output.with_suffix(args.output.suffix + ".manifest.json")
    manifest = {
        "track": "romanbench",
        "construction_stage": "controlled_synthetic_candidates",
        "source_key": source.key,
        "dataset_id": source.dataset_id,
        "source_revision": source.revision,
        "source_license": source.license,
        "output_file": str(args.output),
        "families": stats.families,
        "records": stats.records,
        "variant_counts": stats.variant_counts,
        "source_records_scanned": stats.source_records_scanned,
        "rejected_sentences_or_records": stats.rejected_sentences_or_records,
        "bytes": bytes_written,
        "sha256": sha256_file(args.output),
        "pipeline_version": "romanbench-candidates-v1",
        "filter": asdict(config),
        "review_status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"families={stats.families} records={stats.records} output={args.output}")
    print(f"variants={stats.variant_counts}")
    print(f"manifest={manifest_path}")


if __name__ == "__main__":
    main()
