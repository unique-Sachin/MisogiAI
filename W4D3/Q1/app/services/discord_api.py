"""Simple wrapper around Discord REST API (v10) for bot operations."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import httpx

DISCORD_API_BASE = "https://discord.com/api/v10"
logger = logging.getLogger(__name__)


class DiscordAPIError(Exception):
    """Raised when Discord returns a non-2xx response."""

    def __init__(self, status_code: int, error: Any):
        super().__init__(f"Discord API error {status_code}: {error}")
        self.status_code = status_code
        self.error = error


class DiscordClient:
    def __init__(self, bot_token: str):
        self._headers = {"Authorization": f"Bot {bot_token}"}
        # Create a single AsyncClient instance; caller is responsible for lifespan.
        self._client = httpx.AsyncClient(headers=self._headers, base_url=DISCORD_API_BASE, timeout=10.0)

    async def close(self):
        await self._client.aclose()

    async def _request(self, method: str, url: str, **kwargs):
        resp = await self._client.request(method, url, **kwargs)
        if resp.status_code >= 400:
            logger.error("Discord API error %s %s -> %s %s", method, url, resp.status_code, resp.text)
            raise DiscordAPIError(resp.status_code, resp.text)
        return resp.json()

    # Operations
    async def send_message(self, channel_id: int, content: str) -> Dict[str, Any]:
        return await self._request("POST", f"/channels/{channel_id}/messages", json={"content": content})

    async def get_messages(self, channel_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        return await self._request("GET", f"/channels/{channel_id}/messages", params={"limit": limit})

    async def get_channel_info(self, channel_id: int) -> Dict[str, Any]:
        return await self._request("GET", f"/channels/{channel_id}")

    async def delete_message(self, channel_id: int, message_id: int) -> None:
        await self._request("DELETE", f"/channels/{channel_id}/messages/{message_id}")

    async def search_messages_keyword(self, channel_id: int, keyword: str, limit: int = 100) -> List[Dict[str, Any]]:
        # Discord does not expose channel-scoped search for bots; fallback: fetch & filter.
        msgs = await self.get_messages(channel_id, limit=limit)
        keyword_lower = keyword.lower()
        return [m for m in msgs if keyword_lower in m.get("content", "").lower()] 