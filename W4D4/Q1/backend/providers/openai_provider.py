from typing import List

import openai

from .base import EmbeddingsProvider, CompletionProvider


class OpenAIProvider(EmbeddingsProvider, CompletionProvider):
    """OpenAI implementation for embeddings and completions (chat)."""

    def __init__(self, api_key: str, embedding_model: str, completion_model: str):
        openai.api_key = api_key
        self.embedding_model = embedding_model
        self.completion_model = completion_model

    # EmbeddingsProvider
    def embed(self, texts: List[str]) -> List[List[float]]:
        response = openai.embeddings.create(model=self.embedding_model, input=texts)
        # Preserve order of inputs
        return [r.embedding for r in sorted(response.data, key=lambda x: x.index)]

    # CompletionProvider
    def complete(self, prompt: str, max_tokens: int = 256) -> str:
        response = openai.chat.completions.create(
            model=self.completion_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0,
        )
        return response.choices[0].message.content.strip() 