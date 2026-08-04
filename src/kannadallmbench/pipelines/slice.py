from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Any

from .io import jsonl_bytes


def slice_records(
    records: Iterable[dict[str, Any]],
    *,
    max_records: int | None = None,
    max_bytes: int | None = None,
) -> Iterator[dict[str, Any]]:
    """Yield a deterministic prefix bounded by record count and/or encoded JSONL bytes.

    The first record is emitted even if it alone exceeds ``max_bytes``. This makes
    small-MB smoke slices useful for datasets containing occasional large examples.
    """
    if max_records is not None and max_records <= 0:
        raise ValueError("max_records must be positive")
    if max_bytes is not None and max_bytes <= 0:
        raise ValueError("max_bytes must be positive")
    if max_records is None and max_bytes is None:
        raise ValueError("provide max_records and/or max_bytes")

    emitted = 0
    total_bytes = 0
    for record in records:
        if max_records is not None and emitted >= max_records:
            break
        payload_size = len(jsonl_bytes(record))
        if max_bytes is not None and emitted > 0 and total_bytes + payload_size > max_bytes:
            break
        yield record
        emitted += 1
        total_bytes += payload_size
