from __future__ import annotations

import re
import unicodedata
from typing import Any

_WHITESPACE = re.compile(r"\s+")
_KANNADA_RE = re.compile(r"[\u0C80-\u0CFF]")


def normalize_text(value: str) -> str:
    """Apply conservative, meaning-preserving Unicode/whitespace normalization."""
    value = unicodedata.normalize("NFC", value)
    return _WHITESPACE.sub(" ", value).strip()


def normalize_record(record: dict[str, Any], text_fields: tuple[str, ...]) -> dict[str, Any]:
    result = dict(record)
    for field in text_fields:
        value = result.get(field)
        if isinstance(value, str):
            result[field] = normalize_text(value)
    return result


def kannada_character_ratio(text: str) -> float:
    letters = [ch for ch in text if ch.isalpha()]
    if not letters:
        return 0.0
    return sum(bool(_KANNADA_RE.search(ch)) for ch in letters) / len(letters)


def record_has_min_text(record: dict[str, Any], field: str, min_chars: int) -> bool:
    value = record.get(field)
    return isinstance(value, str) and len(value.strip()) >= min_chars
