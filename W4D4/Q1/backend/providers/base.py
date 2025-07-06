from abc import ABC, abstractmethod
from typing import List


class EmbeddingsProvider(ABC):
    """Abstract interface for embedding text into vector space."""

    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:  # noqa: D401
        """Return an embedding per input text."""
        raise NotImplementedError


class CompletionProvider(ABC):
    """Abstract interface for text completion / chat generation."""

    @abstractmethod
    def complete(self, prompt: str, max_tokens: int = 256) -> str:  # noqa: D401
        """Generate a completion based on the prompt."""
        raise NotImplementedError 