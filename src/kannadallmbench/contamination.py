from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from .pipelines.dedup import stable_text_hash


@dataclass(frozen=True)
class OverlapReport:
    training_records: int
    benchmark_records: int
    exact_overlaps: int


def exact_overlap_count(
    training: Iterable[dict[str, Any]],
    benchmark: Iterable[dict[str, Any]],
    *,
    training_field: str,
    benchmark_field: str,
) -> OverlapReport:
    train_hashes: set[str] = set()
    train_count = 0
    for row in training:
        value = row.get(training_field)
        if isinstance(value, str) and value.strip():
            train_count += 1
            train_hashes.add(stable_text_hash(value))
    benchmark_count = 0
    overlaps = 0
    for row in benchmark:
        value = row.get(benchmark_field)
        if isinstance(value, str) and value.strip():
            benchmark_count += 1
            overlaps += stable_text_hash(value) in train_hashes
    return OverlapReport(train_count, benchmark_count, overlaps)
