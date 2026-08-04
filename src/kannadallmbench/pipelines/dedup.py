from __future__ import annotations

import hashlib
from collections.abc import Iterable, Iterator
from typing import Any

from .transforms import normalize_text


def stable_text_hash(text: str) -> str:
    return hashlib.sha256(normalize_text(text).encode("utf-8")).hexdigest()


def deduplicate_records(records: Iterable[dict[str, Any]], text_field: str) -> Iterator[dict[str, Any]]:
    seen: set[str] = set()
    for record in records:
        value = record.get(text_field)
        if not isinstance(value, str):
            continue
        digest = stable_text_hash(value)
        if digest in seen:
            continue
        seen.add(digest)
        yield record
