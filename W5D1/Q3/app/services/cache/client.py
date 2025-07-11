"""Redis cache client wrapper."""
from __future__ import annotations

import hashlib
import json
import logging
from typing import Any, Dict

import redis  # type: ignore

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class CacheClient:
    """Simple Redis cache client."""

    def __init__(self) -> None:
        self.redis = redis.Redis.from_url(settings.redis_url, decode_responses=True)

    # ---------------- API ----------------- #

    def get(self, key: str) -> Any | None:  # noqa: ANN401
        try:
            value = self.redis.get(key)
            return json.loads(value) if value else None
        except Exception as exc:  # noqa: BLE001
            logger.warning("Cache get failed: %s", exc)
            return None

    def set(self, key: str, value: Any, ttl: int) -> None:  # noqa: ANN401
        try:
            self.redis.set(key, json.dumps(value), ex=ttl)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Cache set failed: %s", exc)

    # -------------- Helper --------------- #

    @staticmethod
    def build_query_key(question: str, companies: list[str] | None, time_range: str | None) -> str:
        payload = {
            "q": question,
            "companies": companies or [],
            "time_range": time_range or "",
        }
        serialized = json.dumps(payload, sort_keys=True)
        digest = hashlib.sha256(serialized.encode()).hexdigest()
        return f"query_result:{digest}"


_CACHE: CacheClient | None = None


def get_cache_client() -> CacheClient:
    global _CACHE  # noqa: PLW0603
    if _CACHE is None:
        _CACHE = CacheClient()
    return _CACHE 