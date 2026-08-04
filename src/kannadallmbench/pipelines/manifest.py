from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class DataManifest:
    source_key: str
    dataset_id: str
    source_revision: str | None
    source_license: str
    output_file: str
    records: int
    bytes: int
    sha256: str
    pipeline_version: str
    created_at: str


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def make_manifest(
    *,
    source_key: str,
    dataset_id: str,
    revision: str | None,
    license_name: str,
    output_file: str | Path,
    records: int,
    bytes_written: int,
    pipeline_version: str = "1",
) -> DataManifest:
    path = Path(output_file)
    return DataManifest(
        source_key=source_key,
        dataset_id=dataset_id,
        source_revision=revision,
        source_license=license_name,
        output_file=str(path),
        records=records,
        bytes=bytes_written,
        sha256=sha256_file(path),
        pipeline_version=pipeline_version,
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def write_manifest(manifest: DataManifest, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(asdict(manifest), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
