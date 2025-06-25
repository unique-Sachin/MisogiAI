"""Evaluation pipeline for EdTech Math Tutor.

Example:
    python -m src.evaluator --input evaluation/input_queries.json --prompt_types zero-shot few-shot cot meta
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import List

from rich.console import Console
from rich.table import Table

from .utils import build_prompt, query_model, append_log, InteractionLog

console = Console()


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Automated evaluation of prompt strategies")
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to JSON file containing evaluation questions with expected answers.",
    )
    parser.add_argument(
        "--prompt_types",
        nargs="*",
        default=["zero-shot", "few-shot", "cot", "meta"],
        choices=["zero-shot", "few-shot", "cot", "meta"],
        help="Subset of prompt types to evaluate.",
    )
    parser.add_argument("--temperature", type=float, default=None)
    return parser.parse_args(argv)


def evaluate_questions(questions: list[dict], prompt_type: str, temperature: float | None) -> dict:
    """Run evaluation for a single prompt type and return metrics."""
    total = len(questions)
    correct = 0
    details: list[dict] = []

    for item in questions:
        q_text = item["question"]
        expected = str(item["expected_answer"]).lower()

        prompt = build_prompt(prompt_type, q_text)
        response, latency_ms = query_model(prompt, temperature=temperature)
        response_lower = response.lower()
        is_correct = expected in response_lower
        if is_correct:
            correct += 1

        details.append(
            {
                "prompt_type": prompt_type,
                "question": q_text,
                "expected": expected,
                "response": response,
                "correct": is_correct,
            }
        )

        # Append to unified interaction log for traceability
        append_log(
            InteractionLog(
                timestamp=datetime.utcnow().isoformat(),
                prompt_type=prompt_type,
                question=q_text,
                response=response,
                latency_ms=latency_ms,
            )
        )

    accuracy = correct / total if total else 0.0
    return {"prompt_type": prompt_type, "accuracy": accuracy, "details": details}


def main(argv: List[str] | None = None) -> None:
    args = parse_args(argv)
    input_path = Path(args.input)
    if not input_path.exists():
        console.print(f"[red]Input file does not exist:[/red] {input_path}")
        return

    questions = json.loads(input_path.read_text())

    summary_table = Table(title="Evaluation Results", show_lines=True)
    summary_table.add_column("Prompt Type")
    summary_table.add_column("Accuracy", justify="right")

    all_details: list[dict] = []
    accuracy_map: dict[str, float] = {}

    for pt in args.prompt_types:
        result = evaluate_questions(questions, pt, args.temperature)
        summary_table.add_row(pt, f"{result['accuracy']:.2f}")
        all_details.extend(result["details"])
        accuracy_map[pt] = result["accuracy"]

    console.print(summary_table)

    # Write detailed results to a timestamped file
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    result_file = input_path.parent / f"eval_results_{timestamp}.json"
    result_file.write_text(json.dumps(all_details, indent=2))
    console.print(f"[green]Detailed results saved to {result_file}")

    # Update analysis report summary line (append)
    report_path = input_path.parent / "analysis_report.md"
    with report_path.open("a", encoding="utf-8") as f:
        f.write(f"\n### Run {timestamp}\n\n| Prompt Type | Accuracy |\n|-------------|----------|\n")
        for pt in args.prompt_types:
            f.write(f"| {pt} | {accuracy_map[pt]:.2f} |\n")

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main() 