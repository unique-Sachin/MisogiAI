"""Tree-of-Thought (ToT) reasoning engine.

Based on Yao et al. (2023) *Tree of Thoughts* (arXiv:2305.10601).
"""
from __future__ import annotations

import logging
from collections import deque
from typing import List, Dict, Any, Tuple

import networkx as nx

# Local utilities
from .utils import LLMClient, ReasoningPath

# Module-level logger
logger = logging.getLogger(__name__)

__all__ = ["ToTEngine"]


class ToTEngine:
    """Engine that explores a tree of reasoning paths using breadth-first or depth-first search."""

    def __init__(
        self,
        llm_client: LLMClient,
        max_depth: int = 3,
        branch_factor: int = 3,
        pruning_threshold: float = 0.3,
    ) -> None:
        """Initialise the ToT engine.

        Args:
            llm_client: Wrapper around LLM API.
            max_depth: Maximum depth to explore.
            branch_factor: Number of thoughts to expand per node.
            pruning_threshold: Minimum score to keep a branch.
        """
        self.llm = llm_client
        self.max_depth = max_depth
        self.branch_factor = branch_factor
        self.pruning_threshold = pruning_threshold

        # Graph representation of thought tree for introspection / visualisation.
        self.graph: nx.DiGraph = nx.DiGraph()
        self.root_id: int | None = None

        # Store successful reasoning paths.
        self._solution_paths: List[ReasoningPath] = []

        logger.info(
            f"ToTEngine initialised (max_depth={max_depth}, branch_factor={branch_factor}, pruning_threshold={pruning_threshold})"
        )

    # ---------------------------------------------------------------------
    # Core API
    # ---------------------------------------------------------------------

    def search_tree(self, problem: str, strategy: str = "bfs") -> List[ReasoningPath]:
        """Explore reasoning space and return valid solution paths.

        Args:
            problem: Original problem statement.
            strategy: Either "bfs" (breadth-first) or "dfs" (depth-first).
        Returns:
            List of successful `ReasoningPath` objects.
        """
        logger.info(f"Starting ToT {strategy.upper()} search")
        self._solution_paths.clear()

        self.graph.clear()
        thought_counter: int = 0
        self.root_id = thought_counter
        self.graph.add_node(self.root_id, text=problem, depth=0)

        # Frontier queue / stack
        frontier: deque[Tuple[int, List[str]]] = deque()
        frontier.append((self.root_id, []))

        while frontier:
            current_id, path_so_far = (
                frontier.popleft() if strategy == "bfs" else frontier.pop()
            )
            current_depth = self.graph.nodes[current_id]["depth"]
            current_text = (
                self.graph.nodes[current_id]["text"]
                if current_depth > 0
                else problem
            )

            if current_depth >= self.max_depth:
                continue

            # Generate candidate thoughts
            thoughts: List[str] = self.generate_thoughts(problem, current_text)
            scores: List[float] = self.evaluate_thoughts(thoughts, problem)

            for thought, score in zip(thoughts, scores):
                if score < self.pruning_threshold:
                    continue  # prune low-quality

                thought_counter += 1
                child_id: int = thought_counter
                self.graph.add_node(child_id, text=thought, depth=current_depth + 1, score=score)
                self.graph.add_edge(current_id, child_id)

                new_path_steps = path_so_far + [thought]

                # If depth limit reached or answer found (simple heuristic)
                if (
                    current_depth + 1 == self.max_depth
                    or self._is_potential_answer(thought)
                ):
                    self._solution_paths.append(
                        ReasoningPath(
                            steps=new_path_steps,
                            confidence_score=score,
                            final_answer=thought,
                        )
                    )
                else:
                    # Add to frontier for further expansion
                    put = frontier.append if strategy == "bfs" else frontier.append
                    put((child_id, new_path_steps))

        logger.info(f"ToT search complete. Solutions found: {len(self._solution_paths)}")
        return self._solution_paths

    def get_solution_paths(self) -> List[ReasoningPath]:
        """Return solution paths from the last search."""
        return self._solution_paths

    # ------------------------------------------------------------------
    # Thought generation / evaluation
    # ------------------------------------------------------------------

    def generate_thoughts(self, problem: str, current_state: str) -> List[str]:
        """Generate candidate next thoughts from current state using the LLM.

        This is a simple placeholder that asks the LLM for bullet-point thoughts.
        """
        prompt = (
            f"Problem: {problem}\n"
            f"Current reasoning: {current_state}\n"
            f"You are an expert reasoner. List {self.branch_factor} coherent next thoughts, one per line."
        )
        response = self.llm.generate(prompt)
        if response is None:
            return []
        thoughts = [line.strip("- •") for line in response.splitlines() if line.strip()]
        # Truncate or pad to exact branch factor
        return thoughts[: self.branch_factor]

    def evaluate_thoughts(self, thoughts: List[str], problem_context: str) -> List[float]:
        """Evaluate candidate thoughts. Placeholder uses LLM self-critique scoring 0-1."""
        joined_thoughts = "\n".join(f"Thought: {t}" for t in thoughts)
        prompt = (
            f"You are evaluating candidate reasoning steps for the following problem:\n{problem_context}\n"
            "For each thought below, provide a score between 0 and 1 reflecting how useful and coherent it is, in the same order, one score per line:"\
            f"\n{joined_thoughts}"
        )
        response = self.llm.generate(prompt)
        if response is None:
            return [0.0] * len(thoughts)
        try:
            scores = [float(x.strip()) for x in response.splitlines() if x.strip()]
        except ValueError:
            logger.warning("Failed to parse scores, defaulting to 0.5")
            scores = [0.5] * len(thoughts)
        # Ensure list lengths align
        if len(scores) < len(thoughts):
            scores.extend([0.5] * (len(thoughts) - len(scores)))
        return scores[: len(thoughts)]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_potential_answer(thought: str) -> bool:
        """Heuristic: crude check for answer-like sentence (contains numeric or yes/no)."""
        return any(char.isdigit() for char in thought) or thought.lower().startswith(("yes", "no")) 