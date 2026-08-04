#!/usr/bin/env python3
"""Run Kannada slices of external benchmarks through their upstream evaluators."""
from __future__ import annotations

import argparse
from pathlib import Path
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / ".external"


def run(cmd: list[str], dry_run: bool = False) -> None:
    print("+", shlex.join(cmd))
    if not dry_run:
        subprocess.run(cmd, check=True)


def common_lm_eval(model: str, backend: str, model_args: str | None) -> list[str]:
    args = model_args or f"pretrained={model}"
    return ["lm_eval", "--model", backend, "--model_args", args]


def milu(args: argparse.Namespace) -> None:
    cmd = common_lm_eval(args.model, args.backend, args.model_args)
    cmd += [
        "--tasks", "milu_Kannada",
        "--batch_size", args.batch_size,
        "--num_fewshot", str(args.num_fewshot),
        "--apply_chat_template",
        "--log_samples",
        "--output_path", str(args.output),
    ]
    run(cmd, args.dry_run)


def indicifeval(args: argparse.Namespace) -> None:
    configs = EXTERNAL / "indicifeval" / "lm-evaluation-harness" / "custom_configs"
    if not configs.exists() and not args.dry_run:
        raise SystemExit("IndicIFEval configs not found. Run: make bootstrap-external")
    cmd = common_lm_eval(args.model, args.backend, args.model_args)
    cmd += [
        "--include_path", str(configs),
        "--tasks", "indicifeval_ground_kn,indicifeval_trans_kn",
        "--batch_size", args.batch_size,
        "--num_fewshot", "0",
        "--apply_chat_template",
        "--log_samples",
        "--output_path", str(args.output),
        "--confirm_run_unsafe_code",
    ]
    if args.gen_kwargs:
        cmd += ["--gen_kwargs", args.gen_kwargs]
    run(cmd, args.dry_run)


def add_shared(sub: argparse.ArgumentParser) -> None:
    sub.add_argument("--model", required=True)
    sub.add_argument("--backend", choices=["hf", "vllm"], default="hf")
    sub.add_argument("--model-args", help="Override lm-eval model_args")
    sub.add_argument("--batch-size", default="auto")
    sub.add_argument("--output", type=Path, required=True)
    sub.add_argument("--dry-run", action="store_true")


def main() -> None:
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers(dest="command", required=True)
    p = subs.add_parser("milu")
    add_shared(p)
    p.add_argument("--num-fewshot", type=int, default=5)
    p.set_defaults(func=milu)
    p = subs.add_parser("indicifeval")
    add_shared(p)
    p.add_argument("--gen-kwargs", default="temperature=0,max_gen_toks=4096")
    p.set_defaults(func=indicifeval)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
