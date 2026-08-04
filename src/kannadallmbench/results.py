from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json


@dataclass
class BenchmarkResult:
    benchmark: str
    track: str
    model: str
    metric: str
    score: float
    num_examples: int | None = None
    source_revision: str | None = None
    details: dict[str, Any] | None = None


@dataclass
class ResultEnvelope:
    schema_version: str
    generated_at: str
    results: list[BenchmarkResult]

    @classmethod
    def create(cls, results: list[BenchmarkResult]) -> "ResultEnvelope":
        return cls(
            schema_version="1.0",
            generated_at=datetime.now(timezone.utc).isoformat(),
            results=results,
        )

    def write(self, path: Path | str) -> None:
        payload = {
            "schema_version": self.schema_version,
            "generated_at": self.generated_at,
            "results": [asdict(r) for r in self.results],
        }
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
