"""Utility to analyse evaluation/test_results.json and pretty-print aggregate metrics."""
from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import Dict, Any

from rich.console import Console
from rich.table import Table

console = Console()


def load_results(results_path: Path) -> Dict[str, Any]:
    with open(results_path, "r", encoding="utf-8") as fp:
        return json.load(fp)


def summarise_metrics(results: Dict[str, Any]) -> None:
    accuracies = [v.get("accuracy", 0.0) for v in results.values()]
    coherence = [v.get("reasoning_coherence", 0.0) for v in results.values()]
    consistency = [v.get("consistency_score", 0.0) for v in results.values()]

    table = Table(title="Evaluation Summary")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Mean", justify="right")
    table.add_column("Std", justify="right")

    def add_row(name: str, data: list[float]):
        mean = statistics.mean(data) if data else 0.0
        std = statistics.stdev(data) if len(data) > 1 else 0.0
        table.add_row(name, f"{mean:.3f}", f"{std:.3f}")

    add_row("Accuracy", accuracies)
    add_row("Reasoning Coherence", coherence)
    add_row("Consistency Score", consistency)

    console.print(table)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Analyse evaluation metrics JSON.")
    parser.add_argument("results", type=Path, default=Path("evaluation/test_results.json"), nargs="?", help="Path to results JSON file.")
    args = parser.parse_args()

    res = load_results(args.results)
    summarise_metrics(res) 