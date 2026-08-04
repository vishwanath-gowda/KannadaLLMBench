from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(frozen=True)
class ExternalBenchmark:
    key: str
    name: str
    repository: str
    revision: str
    license: str
    language: str = "kn"


def load_registry(path: Path | str) -> dict[str, ExternalBenchmark]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return {
        key: ExternalBenchmark(key=key, **value)
        for key, value in raw["benchmarks"].items()
    }
