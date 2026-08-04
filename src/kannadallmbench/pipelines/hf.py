from __future__ import annotations

from collections.abc import Iterable
from typing import Any


def stream_hf_dataset(
    dataset_id: str,
    *,
    config_name: str | None = None,
    split: str = "train",
    revision: str | None = None,
    data_dir: str | None = None,
    token: str | bool | None = None,
) -> Iterable[dict[str, Any]]:
    """Stream a Hugging Face dataset without downloading the full corpus."""
    try:
        from datasets import load_dataset
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("Install project data dependencies: pip install -e '.[data]'") from exc

    kwargs: dict[str, Any] = {"path": dataset_id, "split": split, "streaming": True}
    if config_name:
        kwargs["name"] = config_name
    if revision:
        kwargs["revision"] = revision
    if data_dir:
        kwargs["data_dir"] = data_dir
    if token is not None:
        kwargs["token"] = token
    return load_dataset(**kwargs)
