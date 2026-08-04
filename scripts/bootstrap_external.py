#!/usr/bin/env python3
"""Clone pinned upstream benchmark repositories into .external/."""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from kannadallmbench.registry import load_registry  # noqa: E402


def run(cmd: list[str], cwd: Path | None = None) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True)


def clone_one(key: str, destination: Path, force: bool) -> None:
    registry = load_registry(ROOT / "external" / "registry.json")
    b = registry[key]
    target = destination / key
    if target.exists():
        if not force:
            print(f"{key}: already present at {target}; use --force to refresh")
            return
        shutil.rmtree(target)
    destination.mkdir(parents=True, exist_ok=True)
    run(["git", "clone", "--filter=blob:none", b.repository, str(target)])
    run(["git", "checkout", b.revision], cwd=target)
    print(f"{key}: pinned to {b.revision}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("benchmarks", nargs="*", choices=["milu", "indicifeval", "indicgenbench"])
    parser.add_argument("--destination", type=Path, default=ROOT / ".external")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    keys = args.benchmarks or ["milu", "indicifeval", "indicgenbench"]
    for key in keys:
        clone_one(key, args.destination, args.force)


if __name__ == "__main__":
    main()
