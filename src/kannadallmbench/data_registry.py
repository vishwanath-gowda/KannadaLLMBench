from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


APPROVED_STATUSES = {"approved"}


@dataclass(frozen=True)
class DataSource:
    key: str
    name: str
    dataset_id: str
    license: str
    status: str
    revision: str | None = None
    config_name: str | None = None
    split: str | None = None
    data_dir: str | None = None
    language: str = "kn"
    provenance_url: str | None = None
    citation_url: str | None = None
    notes: str | None = None
    tags: tuple[str, ...] = field(default_factory=tuple)
    field_map: dict[str, str] = field(default_factory=dict)

    @property
    def approved(self) -> bool:
        return self.status in APPROVED_STATUSES


def load_data_sources(path: str | Path) -> dict[str, DataSource]:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    sources = raw.get("sources", {})
    parsed: dict[str, DataSource] = {}
    for key, value in sources.items():
        value = dict(value)
        value["tags"] = tuple(value.get("tags", []))
        parsed[key] = DataSource(key=key, **value)
    return parsed


def require_approved(source: DataSource, allow_unreviewed: bool = False) -> None:
    if source.approved or allow_unreviewed:
        return
    raise PermissionError(
        f"Data source '{source.key}' is '{source.status}', not approved. "
        "Review provenance/license first or pass --allow-unreviewed explicitly."
    )


def validate_registry(path: str | Path) -> list[str]:
    errors: list[str] = []
    sources = load_data_sources(path)
    if not sources:
        errors.append("registry has no sources")
        return errors
    for key, source in sources.items():
        if source.key != key:
            errors.append(f"{key}: key mismatch")
        if not source.dataset_id:
            errors.append(f"{key}: dataset_id is required")
        if not source.license:
            errors.append(f"{key}: license is required")
        if source.status not in {"approved", "review_required", "blocked"}:
            errors.append(f"{key}: unsupported status {source.status!r}")
        if source.approved and not source.provenance_url:
            errors.append(f"{key}: approved sources must have provenance_url")
        if source.approved and not source.revision:
            errors.append(f"{key}: approved sources must pin a revision")
    return errors
