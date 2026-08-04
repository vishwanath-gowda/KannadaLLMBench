#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from kannadallmbench.data_registry import validate_registry  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=ROOT / "config" / "data_sources.yaml")
    args = parser.parse_args()
    errors = validate_registry(args.registry)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print(f"OK: {args.registry}")


if __name__ == "__main__":
    main()
