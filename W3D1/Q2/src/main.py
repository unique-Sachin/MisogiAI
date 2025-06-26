"""Main entry point for running the pipeline from the command line.

Usage:
    python -m src.main --task_file path/to/tasks/math_word_problems.json
"""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

from .utils import LLMClient, evaluate_solution_quality
from .tot_engine import ToTEngine
from .self_consistency import SelfConsistency
from .prompt_optimizer import PromptOptimizer

logger = logging.getLogger(__name__)


def load_tasks(task_file: Path) -> List[Dict[str, Any]]:
    with open(task_file, "r", encoding="utf-8") as fp:
        tasks: List[Dict[str, Any]] = json.load(fp)
    return tasks


def run_pipeline(task_file: Path, output_path: Path | None = None) -> None:
    llm = LLMClient()
    tot = ToTEngine(llm_client=llm)
    sc = SelfConsistency(llm_client=llm)

    tasks = load_tasks(task_file)
    # Ensure logs directories exist
    from pathlib import Path as _P
    for sub in ["logs", "logs/reasoning_trees", "logs/optimization_history", "logs/performance_logs"]:
        _P(sub).mkdir(parents=True, exist_ok=True)

    results: Dict[str, Dict[str, Any]] = {}

    for idx, task in enumerate(tasks):
        problem = task["problem"]
        ground_truth = task.get("answer", "")
        logger.info(f"\n===== Task {idx+1}/{len(tasks)} =====")
        logger.info(f"Problem: {problem}")

        # 1. ToT search
        tot_paths = tot.search_tree(problem, strategy="bfs")
        # 2. Self-Consistency over ToT final answers
        sc_paths = sc.generate_multiple_solutions(problem)
        aggregated_answer, consistency_score = sc.aggregate_answers(sc_paths)

        # 3. Evaluation
        accuracy, base_metrics = evaluate_solution_quality(
            aggregated_answer, ground_truth, [" → ".join(p.steps) for p in sc_paths]
        )
        metrics_detail: Dict[str, Any] = dict(base_metrics)
        metrics_detail.update({
            "consistency_score": consistency_score,
            "aggregated_answer": aggregated_answer,
            "ground_truth": ground_truth,
        })
        results[f"task_{idx}"] = metrics_detail
        logger.info(f"Result: accuracy={accuracy}, consistency={consistency_score:.2f}")

    if output_path is None:
        output_path = Path("evaluation") / "test_results.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fp:
        json.dump(results, fp, indent=2)
    logger.info(f"Saved evaluation results to {output_path}")

    # ------------------------------------------------------------------
    # Prompt Optimizer feedback loop
    # ------------------------------------------------------------------
    evaluation_metrics = {"accuracy_threshold": 0.8}
    optimizer = PromptOptimizer(llm_client=llm, evaluation_metrics=evaluation_metrics)
    failures = optimizer.detect_failures(results)
    if failures:
        base_prompt_path = Path("prompts/base_prompts/tot_system_prompt.txt")
        optimized_prompt = optimizer.generate_optimized_prompt(failures, base_prompt_path)
        if optimized_prompt:
            optimizer.track_improvements(base_prompt_path, optimized_prompt, {"num_failures": len(failures)})
    else:
        logger.info("No failures detected above threshold; skipping prompt optimization.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the advanced prompt engineering pipeline.")
    parser.add_argument("--task_file", type=Path, required=True, help="Path to JSON file containing tasks.")
    parser.add_argument("--output", type=Path, help="Optional path to save results JSON.")
    args = parser.parse_args()

    run_pipeline(args.task_file, args.output) 