"""Self-Consistency aggregator.

Implements Wang et al. (2022) *Self-Consistency Improves Chain of Thought Reasoning in Language Models* (arXiv:2203.11171).
"""
from __future__ import annotations

import logging
from collections import Counter
from typing import List, Dict, Tuple

from .utils import LLMClient, ReasoningPath, evaluate_solution_quality

logger = logging.getLogger(__name__)


class SelfConsistency:
    """Generate multiple reasoning paths and aggregate via majority vote or consensus."""

    def __init__(self, llm_client: LLMClient, num_paths: int = 5) -> None:
        self.llm = llm_client
        self.num_paths = max(1, num_paths)

        logger.info(f"SelfConsistency initialised (num_paths={self.num_paths})")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_multiple_solutions(
        self, problem: str, prompt_template: str | None = None
    ) -> List[ReasoningPath]:
        """Generate diverse reasoning paths.

        Args:
            problem: Problem statement.
            prompt_template: Optional template with a placeholder `{problem}`.
        Returns:
            List of reasoning paths.
        """
        paths: List[ReasoningPath] = []
        for _ in range(self.num_paths):
            prompt = self._build_prompt(problem, prompt_template)
            generated = self.llm.generate(prompt)
            if generated is None:
                continue
            steps = [s.strip() for s in generated.split('\n') if s.strip()]
            final_answer = steps[-1] if steps else ""
            # Confidence placeholder: uniform
            path = ReasoningPath(steps=steps, confidence_score=1.0 / self.num_paths, final_answer=final_answer)
            paths.append(path)
        logger.info(f"Generated {len(paths)}/{self.num_paths} reasoning paths for problem.")
        return paths

    def aggregate_answers(self, solutions: List[ReasoningPath]) -> Tuple[str, float]:
        """Aggregate final answers via majority vote.

        Returns:
            Tuple of (aggregated_answer, consistency_score).
        """
        answers = [s.final_answer for s in solutions if s.final_answer]
        if not answers:
            logger.warning("No valid answers to aggregate.")
            return "", 0.0
        counts = Counter(answers)
        aggregated_answer, freq = counts.most_common(1)[0]
        consistency_score = freq / len(answers)
        logger.debug(f"Aggregated answer '{aggregated_answer}' with consistency {consistency_score:.2f}")
        return aggregated_answer, consistency_score

    def calculate_consistency_score(self, solutions: List[ReasoningPath]) -> float:
        """Return agreement percentage across multiple runs."""
        _, score = self.aggregate_answers(solutions)
        return score

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_prompt(self, problem: str, template: str | None) -> str:
        if template is None:
            return (
                "You are an expert problem solver. Think step-by-step and provide a chain of thought reasoning "
                "ending with your final answer on a new line prefixed by 'Answer:'.\n\nProblem: "
                + problem
            )
        return template.format(problem=problem) 