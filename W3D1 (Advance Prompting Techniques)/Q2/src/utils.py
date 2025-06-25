"""Utility functions, data structures, and helpers for the Advanced Prompt Engineering Pipeline."""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np

from openai import OpenAI, OpenAIError
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Flexible logger: prefer Loguru if available, else fall back to stdlib logger
# ---------------------------------------------------------------------------

try:
    from loguru import logger  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    logger = logging.getLogger("pipeline")
    logger.setLevel(logging.INFO)

# ---------------------------------------------------------------------------
# Environment setup
# ---------------------------------------------------------------------------
load_dotenv()
OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")


class LLMClient:
    """Thin wrapper around OpenAI Python client with sane defaults and error handling."""

    def __init__(self, model: str = "gpt-3.5-turbo-0125", temperature: float = 0.7):
        if not OPENAI_API_KEY:
            raise EnvironmentError("OPENAI_API_KEY not set. Please add it to your environment variables or .env file.")
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = model
        self.temperature = temperature

    def generate(self, prompt: str, max_tokens: int = 1024) -> str | None:
        """Generate a completion from the LLM.

        Args:
            prompt: Prompt string to send to the model.
            max_tokens: Maximum tokens to generate.

        Returns:
            The generated text or ``None`` if generation failed.
        """
        try:
            logger.debug(f"Sending prompt to LLM (len={len(prompt)} chars)")
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            content = response.choices[0].message.content
            if content is None or len(content.strip()) == 0:
                raise ValueError("Empty response from LLM")
            return content
        except OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            return None
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"LLM generation failed: {e}")
            return None


@dataclass
class ReasoningPath:
    """Container for a reasoning path in Tree-of-Thought and Self-Consistency."""

    steps: List[str]
    confidence_score: float
    final_answer: str


# ---------------------------------------------------------------------------
# Evaluation helpers
# ---------------------------------------------------------------------------

def evaluate_solution_quality(
    solution: str,
    ground_truth: str,
    reasoning_steps: List[str],
) -> Tuple[float, Dict[str, float]]:
    """Evaluate solution quality against ground truth.

    Args:
        solution: Generated solution.
        ground_truth: Verified correct answer.
        reasoning_steps: List of reasoning steps taken.

    Returns:
        Tuple of (accuracy_score, detailed_metrics).
    """
    accuracy_score: float = float(solution.strip() == ground_truth.strip())

    # Basic reasoning coherence metric: length-normalised similarity (placeholder).
    coherence_scores = np.clip(
        [len(step.split()) / max(len(ground_truth.split()), 1) for step in reasoning_steps],
        0.0,
        1.0,
    )
    coherence_mean: float = float(np.mean(coherence_scores))

    detailed_metrics: Dict[str, float] = {
        "accuracy": accuracy_score,
        "reasoning_coherence": coherence_mean,
    }
    return accuracy_score, detailed_metrics 