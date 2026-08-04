from __future__ import annotations

import json
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Any


def jsonl_bytes(record: dict[str, Any]) -> bytes:
    return (json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")


def read_jsonl(path: str | Path) -> Iterator[dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSONL at {path}:{line_number}: {exc}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"expected JSON object at {path}:{line_number}")
            yield value


def write_jsonl(records: Iterable[dict[str, Any]], path: str | Path) -> tuple[int, int]:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    size = 0
    with target.open("wb") as handle:
        for record in records:
            payload = jsonl_bytes(record)
            handle.write(payload)
            count += 1
            size += len(payload)
    return count, size
