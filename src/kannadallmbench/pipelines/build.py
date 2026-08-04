from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from kannadallmbench.data_registry import DataSource, require_approved

from .dedup import deduplicate_records
from .hf import stream_hf_dataset
from .io import write_jsonl
from .manifest import make_manifest, write_manifest
from .slice import slice_records
from .transforms import normalize_record


@dataclass(frozen=True)
class BuildConfig:
    output: Path
    text_fields: tuple[str, ...]
    dedup_field: str | None = None
    max_records: int | None = None
    max_bytes: int | None = None
    allow_unreviewed: bool = False


def build_jsonl_from_hf(source: DataSource, config: BuildConfig) -> tuple[int, int]:
    require_approved(source, allow_unreviewed=config.allow_unreviewed)
    stream = stream_hf_dataset(
        source.dataset_id,
        config_name=source.config_name,
        split=source.split or "train",
        revision=source.revision,
        data_dir=source.data_dir,
    )
    records = (normalize_record(dict(row), config.text_fields) for row in stream)
    if config.dedup_field:
        records = deduplicate_records(records, config.dedup_field)
    if config.max_records is not None or config.max_bytes is not None:
        records = slice_records(records, max_records=config.max_records, max_bytes=config.max_bytes)
    count, size = write_jsonl(records, config.output)
    manifest = make_manifest(
        source_key=source.key,
        dataset_id=source.dataset_id,
        revision=source.revision,
        license_name=source.license,
        output_file=config.output,
        records=count,
        bytes_written=size,
    )
    write_manifest(manifest, config.output.with_suffix(config.output.suffix + ".manifest.json"))
    return count, size
