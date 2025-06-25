"""Entry point for the EdTech Math Tutor CLI application.

Usage examples
--------------
$ python -m src.main --prompt_type zero-shot --question "Solve 2x + 3 = 11"
$ python -m src.main --prompt_type few-shot --input_file evaluation/input_queries.json

Run `python -m src.main --help` for full CLI reference.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from rich.console import Console

from .utils import InteractionLog, append_log, build_prompt, query_model

console = Console()


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="CLI math tutor using deepseek model via LM Studio",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--prompt_type",
        choices=["zero-shot", "few-shot", "cot", "meta"],
        required=True,
        help="Prompt strategy to use.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--question", type=str, help="Single question to ask the tutor.")
    group.add_argument(
        "--input_file",
        type=str,
        help="Path to JSON file with a list of questions to batch-evaluate.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=None,
        help="Sampling temperature override (defaults vary by prompt).",
    )
    return parser.parse_args(argv)


def process_question(prompt_type: str, question: str, temperature: float | None = None) -> str:
    """Build prompt, query model, log and return response."""
    prompt = build_prompt(prompt_type, question)
    response, latency_ms = query_model(prompt, temperature=temperature)

    # Log interaction
    log_entry = InteractionLog(
        timestamp=datetime.utcnow().isoformat(),
        prompt_type=prompt_type,
        question=question,
        response=response,
        latency_ms=latency_ms,
    )
    append_log(log_entry)
    return response


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)

    if args.question:
        console.print("[bold blue]Question:[/bold blue]", args.question)
        answer = process_question(args.prompt_type, args.question, args.temperature)
        console.print("\n[bold green]Answer:[/bold green]", answer)
    else:
        # Batch mode
        input_path = Path(args.input_file)
        if not input_path.exists():
            console.print(f"[red]Input file not found:[/red] {input_path}")
            sys.exit(1)
        try:
            questions = json.loads(input_path.read_text())
        except json.JSONDecodeError as exc:
            console.print(f"[red]Invalid JSON:[/red] {exc}")
            sys.exit(1)

        for q in questions:
            q_text = q.get("question") or q
            if not isinstance(q_text, str):
                console.print(f"[yellow]Skipping invalid item:[/yellow] {q}")
                continue
            console.rule(f"[bold cyan]{q_text}")
            answer = process_question(args.prompt_type, q_text, args.temperature)
            console.print("[green]Tutor:[/green]", answer)


if __name__ == "__main__":  # pragma: no cover
    main() 