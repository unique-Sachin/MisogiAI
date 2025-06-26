"""Aggregate evaluation results, run statistical tests, and update analysis_report.md.

Usage:
    python -m src.analyzer --results_dir evaluation

This script scans for files named `eval_results_*.json`, computes overall accuracy
per prompt type, performs pair-wise McNemar exact tests to determine whether
accuracy differences are statistically significant, and appends a Markdown
summary to `evaluation/analysis_report.md`.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from rich.console import Console
from rich.table import Table
from scipy.stats import norm

console = Console()


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze evaluation result snapshots")
    parser.add_argument(
        "--results_dir",
        type=str,
        default="evaluation",
        help="Directory containing eval_results_*.json files.",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.05,
        help="Significance level for tests.",
    )
    return parser.parse_args(argv)


def load_results(files: List[Path]) -> List[dict]:
    all_entries: List[dict] = []
    for file in files:
        try:
            entries = json.loads(file.read_text())
            all_entries.extend(entries)
        except json.JSONDecodeError as exc:
            console.print(f"[yellow]Skipping invalid JSON file {file}: {exc}")
    return all_entries


def compute_accuracy(entries: List[dict]) -> Dict[str, Tuple[int, int]]:
    """Return dict mapping prompt_type -> (correct, total)."""
    stats: Dict[str, Tuple[int, int]] = defaultdict(lambda: (0, 0))
    for e in entries:
        pt = e["prompt_type"]
        correct, total = stats[pt]
        if e.get("correct") or e.get("correct") is True:
            correct += 1
        total += 1
        stats[pt] = (correct, total)
    return stats


def pairwise_tests(stats: Dict[str, Tuple[int, int]], alpha: float) -> List[Tuple[str, str, float, bool]]:
    """Return list of (pt_a, pt_b, p_value, significant) pairs."""
    results: List[Tuple[str, str, float, bool]] = []
    prompt_types = list(stats.keys())
    for i in range(len(prompt_types)):
        for j in range(i + 1, len(prompt_types)):
            a, b = prompt_types[i], prompt_types[j]
            correct_a, total_a = stats[a]
            correct_b, total_b = stats[b]
            # Use two-proportion test (binomial) — approximate alternative to McNemar given independent samples
            p_pool = (correct_a + correct_b) / (total_a + total_b)
            # Compute standard error
            se = np.sqrt(p_pool * (1 - p_pool) * (1 / total_a + 1 / total_b))
            z = (correct_a / total_a - correct_b / total_b) / se if se else 0.0
            # two-tailed p-value using normal approximation
            p_val = 2 * (1 - norm.cdf(abs(z))) if total_a and total_b else 1.0
            results.append((a, b, p_val, p_val < alpha))
    return results


def write_report(stats: Dict[str, Tuple[int, int]], tests: List[Tuple[str, str, float, bool]], alpha: float) -> None:
    report_path = Path("evaluation/analysis_report.md")
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    with report_path.open("a", encoding="utf-8") as f:
        f.write(f"\n## Aggregate Analysis – {timestamp}\n\n")
        f.write("### Accuracy per Prompt Type\n\n")
        f.write("| Prompt Type | Correct | Total | Accuracy |\n|-------------|---------|-------|----------|\n")
        for pt, (corr, tot) in stats.items():
            f.write(f"| {pt} | {corr} | {tot} | {corr / tot:.2f} |\n")

        f.write("\n### Pair-wise Significance Tests (two-proportion z)\n\n")
        f.write(f"Alpha = {alpha}\n\n")
        f.write("| A | B | p-value | Significant? |\n|---|---|---------|--------------|\n")
        for a, b, p, sig in tests:
            f.write(f"| {a} | {b} | {p:.3e} | {'Yes' if sig else 'No'} |\n")

    console.print(f"[green]Report updated at {report_path}")


def main(argv: List[str] | None = None) -> None:
    args = parse_args(argv)
    results_dir = Path(args.results_dir)
    pattern = re.compile(r"eval_results_.*\.json")
    files = [p for p in results_dir.glob("eval_results_*.json") if pattern.match(p.name)]

    if not files:
        console.print(f"[yellow]No evaluation result files found in {results_dir}")
        return

    entries = load_results(files)
    stats = compute_accuracy(entries)

    # Display table
    table = Table(title="Aggregate Accuracy", show_lines=True)
    table.add_column("Prompt Type")
    table.add_column("Correct", justify="right")
    table.add_column("Total", justify="right")
    table.add_column("Accuracy", justify="right")

    for pt, (corr, tot) in stats.items():
        table.add_row(pt, str(corr), str(tot), f"{corr / tot:.2f}")
    console.print(table)

    tests = pairwise_tests(stats, args.alpha)

    # Print pairwise table
    test_t = Table(title="Pair-wise Tests", show_lines=True)
    test_t.add_column("A")
    test_t.add_column("B")
    test_t.add_column("p-value")
    test_t.add_column("Significant?")
    for a, b, p, sig in tests:
        test_t.add_row(a, b, f"{p:.3e}", "Yes" if sig else "No")
    console.print(test_t)

    write_report(stats, tests, args.alpha)


if __name__ == "__main__":
    main() 