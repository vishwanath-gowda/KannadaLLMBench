#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from kannadallmbench.data_registry import load_data_sources  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="List registered training/data sources and review status.")
    parser.add_argument("--registry", type=Path, default=ROOT / "config" / "data_sources.yaml")
    args = parser.parse_args()
    for source in load_data_sources(args.registry).values():
        print(f"{source.key:28} {source.status:15} {source.license:16} {source.dataset_id}")


if __name__ == "__main__":
    main()
