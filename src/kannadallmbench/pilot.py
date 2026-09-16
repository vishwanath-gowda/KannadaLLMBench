from __future__ import annotations

import csv
import hashlib
from collections import Counter, defaultdict
from collections.abc import Iterable, Sequence
from itertools import combinations
from pathlib import Path
from typing import Any

from kannadallmbench.annotation_tasks import romanbench_candidate_to_task

DEFAULT_VARIANT_ORDER = ("ascii_phonemic", "ascii_relaxed", "iast")


def _stable_key(seed: str, value: str) -> str:
    return hashlib.sha256(f"{seed}|{value}".encode("utf-8")).hexdigest()


def select_pilot_tasks(
    rows: Iterable[dict[str, Any]],
    *,
    families: int = 30,
    batch_id: str = "pilot-v1",
    target_votes: int = 2,
    seed: str = "romanbench-pilot-v1",
    variant_order: Sequence[str] = DEFAULT_VARIANT_ORDER,
) -> list[dict[str, Any]]:
    """Select one deterministic Roman candidate from each semantic family.

    Families are ranked by a seeded stable hash rather than corpus order. The selected
    candidate cycles through available controlled variant types to give the pilot a
    useful mix of Romanization styles while never showing multiple variants from the
    same semantic family in the task sheet.
    """
    if families < 1:
        raise ValueError("families must be >= 1")
    if target_votes < 1:
        raise ValueError("target_votes must be >= 1")
    if not variant_order:
        raise ValueError("variant_order must not be empty")

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        family_id = str(row.get("semantic_family_id") or "").strip()
        if not family_id:
            raise ValueError("candidate row is missing semantic_family_id")
        grouped[family_id].append(row)

    if len(grouped) < families:
        raise ValueError(f"requested {families} families but only {len(grouped)} are available")

    family_ids = sorted(grouped, key=lambda family_id: _stable_key(seed, family_id))[:families]
    tasks: list[dict[str, Any]] = []

    for index, family_id in enumerate(family_ids):
        candidates = grouped[family_id]
        desired_variant = variant_order[index % len(variant_order)]
        matching = [row for row in candidates if str(row.get("variant_type") or "") == desired_variant]
        pool = matching or candidates
        chosen = min(
            pool,
            key=lambda row: (
                _stable_key(seed, str(row.get("id") or "")),
                str(row.get("variant_type") or ""),
            ),
        )
        tasks.append(
            romanbench_candidate_to_task(
                chosen,
                batch_id=batch_id,
                target_votes=target_votes,
            )
        )

    return tasks


def variant_counts(tasks: Iterable[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(str(task.get("variant_type") or "unknown") for task in tasks)
    return dict(sorted(counts.items()))


def read_annotations_csv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _truthy(value: Any) -> bool:
    return str(value or "").strip().lower() in {"true", "yes", "1", "y"}


def _clean_label(value: Any) -> str:
    value = str(value or "").strip().lower()
    return value if value in {"yes", "no"} else ""


def _pairwise_agreement(groups: dict[str, list[str]]) -> tuple[int, int, float | None]:
    agreements = 0
    pairs = 0
    for labels in groups.values():
        for left, right in combinations(labels, 2):
            pairs += 1
            agreements += int(left == right)
    return agreements, pairs, (agreements / pairs if pairs else None)


def analyze_annotations(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Compute pilot annotation quality metrics.

    Roman-typing labels are defined only when the annotator marked meaning=Yes.
    Meaning=No rows therefore never contribute to typing agreement.
    """
    rows = list(rows)
    skipped_rows = [row for row in rows if _truthy(row.get("skipped"))]
    completed_rows = [row for row in rows if not _truthy(row.get("skipped"))]

    meaning_groups: dict[str, list[str]] = defaultdict(list)
    typing_groups: dict[str, list[str]] = defaultdict(list)
    meaning_yes_typing_no = 0
    meaning_yes_count = 0

    for row in completed_rows:
        task_id = str(row.get("task_id") or "").strip()
        meaning = _clean_label(row.get("meaning_correct"))
        typing = _clean_label(row.get("typeable_romanization"))
        if task_id and meaning:
            meaning_groups[task_id].append(meaning)
        if meaning == "yes":
            meaning_yes_count += 1
            if task_id and typing:
                typing_groups[task_id].append(typing)
            if typing == "no":
                meaning_yes_typing_no += 1

    meaning_agreements, meaning_pairs, meaning_rate = _pairwise_agreement(meaning_groups)
    typing_agreements, typing_pairs, typing_rate = _pairwise_agreement(typing_groups)

    unique_tasks = {str(row.get("task_id") or "").strip() for row in rows if str(row.get("task_id") or "").strip()}
    unique_families = {
        str(row.get("semantic_family_id") or "").strip()
        for row in rows
        if str(row.get("semantic_family_id") or "").strip()
    }

    return {
        "annotations": len(rows),
        "completed_annotations": len(completed_rows),
        "skipped_annotations": len(skipped_rows),
        "skip_rate": (len(skipped_rows) / len(rows) if rows else 0.0),
        "unique_tasks": len(unique_tasks),
        "unique_semantic_families": len(unique_families),
        "meaning": {
            "pair_agreements": meaning_agreements,
            "pair_comparisons": meaning_pairs,
            "pairwise_agreement": meaning_rate,
        },
        "roman_typing": {
            "pair_agreements": typing_agreements,
            "pair_comparisons": typing_pairs,
            "pairwise_agreement": typing_rate,
            "eligible_judgments": meaning_yes_count,
        },
        "meaning_yes_typing_no": {
            "count": meaning_yes_typing_no,
            "rate_among_meaning_yes": (
                meaning_yes_typing_no / meaning_yes_count if meaning_yes_count else 0.0
            ),
        },
    }


def disagreement_rows(rows: Iterable[dict[str, Any]]) -> list[dict[str, str]]:
    """Return task-level meaning/typing disagreements for manual inspection."""
    by_task: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        task_id = str(row.get("task_id") or "").strip()
        if task_id and not _truthy(row.get("skipped")):
            by_task[task_id].append(row)

    output: list[dict[str, str]] = []
    for task_id, task_rows in sorted(by_task.items()):
        family_id = str(task_rows[0].get("semantic_family_id") or "").strip()
        meaning = [_clean_label(row.get("meaning_correct")) for row in task_rows]
        meaning = [label for label in meaning if label]
        if len(set(meaning)) > 1:
            output.append(
                {
                    "task_id": task_id,
                    "semantic_family_id": family_id,
                    "dimension": "meaning",
                    "labels": "|".join(meaning),
                    "annotators": "|".join(str(row.get("annotator_id") or "") for row in task_rows),
                }
            )

        typing_rows = [row for row in task_rows if _clean_label(row.get("meaning_correct")) == "yes"]
        typing = [_clean_label(row.get("typeable_romanization")) for row in typing_rows]
        typing = [label for label in typing if label]
        if len(set(typing)) > 1:
            output.append(
                {
                    "task_id": task_id,
                    "semantic_family_id": family_id,
                    "dimension": "roman_typing",
                    "labels": "|".join(typing),
                    "annotators": "|".join(str(row.get("annotator_id") or "") for row in typing_rows),
                }
            )

    return output
