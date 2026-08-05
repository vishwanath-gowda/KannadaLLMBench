from __future__ import annotations

import csv
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

TASK_FIELDS = (
    "task_id",
    "semantic_family_id",
    "kannada",
    "roman",
    "variant_type",
    "source_type",
    "source_id",
    "source_author_id",
    "batch_id",
    "target_votes",
    "active",
)


def romanbench_candidate_to_task(
    row: dict[str, Any], *, batch_id: str, target_votes: int = 2
) -> dict[str, Any]:
    if target_votes < 1:
        raise ValueError("target_votes must be >= 1")
    provenance = row.get("provenance") or {}
    task_id = str(row.get("id") or "").strip()
    family_id = str(row.get("semantic_family_id") or "").strip()
    kannada = str(row.get("kannada_control") or row.get("reference_answer") or "").strip()
    roman = str(row.get("roman_input") or "").strip()
    if not task_id or not family_id or not kannada or not roman:
        raise ValueError("candidate row requires id, semantic_family_id, Kannada control, and roman_input")
    return {
        "task_id": task_id,
        "semantic_family_id": family_id,
        "kannada": kannada,
        "roman": roman,
        "variant_type": str(row.get("variant_type") or "unknown"),
        "source_type": str(provenance.get("source_type") or row.get("romanization_source") or "unknown"),
        "source_id": str(provenance.get("source_id") or ""),
        "source_author_id": str(provenance.get("source_author_id") or ""),
        "batch_id": batch_id,
        "target_votes": target_votes,
        "active": True,
    }


def pair_to_task(
    row: dict[str, Any],
    *,
    task_id_field: str,
    family_id_field: str,
    kannada_field: str,
    roman_field: str,
    batch_id: str,
    target_votes: int = 2,
    variant_type: str = "existing_pair",
    source_id: str = "",
) -> dict[str, Any]:
    if target_votes < 1:
        raise ValueError("target_votes must be >= 1")
    task_id = str(row.get(task_id_field) or "").strip()
    family_id = str(row.get(family_id_field) or task_id).strip()
    kannada = str(row.get(kannada_field) or "").strip()
    roman = str(row.get(roman_field) or "").strip()
    if not task_id or not family_id or not kannada or not roman:
        raise ValueError("pair row is missing required task/family/Kannada/Roman content")
    return {
        "task_id": task_id,
        "semantic_family_id": family_id,
        "kannada": kannada,
        "roman": roman,
        "variant_type": variant_type,
        "source_type": "existing_pair",
        "source_id": source_id,
        "source_author_id": str(row.get("source_author_id") or ""),
        "batch_id": batch_id,
        "target_votes": target_votes,
        "active": True,
    }


def read_jsonl(path: str | Path) -> Iterable[dict[str, Any]]:
    with Path(path).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_number}: {exc}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"Line {line_number} is not a JSON object")
            yield value


def write_tasks_csv(rows: Iterable[dict[str, Any]], output: str | Path) -> int:
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=TASK_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in TASK_FIELDS})
            count += 1
    return count
