"""OPRO-style automated prompt optimizer.

Generates improved prompts based on failure analysis and tracks versions.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple

from .utils import LLMClient

PROMPTS_DIR = Path("prompts")
OPTIMIZED_DIR = PROMPTS_DIR / "optimized_prompts"

logger = logging.getLogger(__name__)


class PromptOptimizer:
    """Analyse pipeline failures and auto-generate improved prompts."""

    def __init__(self, llm_client: LLMClient, evaluation_metrics: Dict[str, Any]):
        self.llm = llm_client
        self.metrics_config = evaluation_metrics
        OPTIMIZED_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def detect_failures(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Identify low-accuracy or inconsistent cases.

        Returns subset of results that should be addressed by prompt tuning.
        """
        threshold = self.metrics_config.get("accuracy_threshold", 0.8)
        failures = {
            k: v for k, v in results.items() if v.get("accuracy", 1.0) < threshold
        }
        logger.info(f"Detected {len(failures)} failure cases (threshold={threshold}).")
        return failures

    def generate_optimized_prompt(self, failure_analysis: Dict[str, Any], base_prompt_path: Path) -> str | None:
        """Generate an improved prompt via the LLM given failure examples."""
        if not failure_analysis:
            logger.info("No failures provided; skipping prompt optimization.")
            return None

        with open(base_prompt_path, "r", encoding="utf-8") as fp:
            base_prompt = fp.read()

        prompt = (
            "You are a prompt engineering assistant. Given the base prompt below and examples of where it failed, "
            "suggest a revised prompt that addresses the shortcomings while remaining concise.\n\n"
            f"Base Prompt:\n{base_prompt}\n\n"
            f"Failure Analysis (JSON):\n{json.dumps(failure_analysis, indent=2)}\n\n"
            "Return only the optimized prompt text."
        )
        optimized = self.llm.generate(prompt)
        if optimized:
            logger.info("Generated optimized prompt.")
        return optimized

    def track_improvements(self, old_prompt_path: Path, new_prompt_text: str, metrics: Dict[str, float]) -> Path:
        """Save new prompt version with metadata and return its path."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        new_path = OPTIMIZED_DIR / f"prompt_{timestamp}.txt"
        with open(new_path, "w", encoding="utf-8") as fp:
            fp.write(new_prompt_text)
        # Log metrics
        meta = {
            "created_at": timestamp,
            "source_prompt": str(old_prompt_path),
            "metrics": metrics,
        }
        meta_path = new_path.with_suffix(".json")
        with open(meta_path, "w", encoding="utf-8") as fp:
            json.dump(meta, fp, indent=2)
        logger.info(f"Saved optimized prompt to {new_path} (metadata: {meta_path}).")
        return new_path 