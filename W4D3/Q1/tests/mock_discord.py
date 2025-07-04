from datetime import datetime


class MockDiscordClient:
    """Mock version of DiscordClient for unit tests."""

    def __init__(self, token: str):
        self.token = token

    async def close(self):
        """No-op close."""
        return None

    async def send_message(self, channel_id: int, content: str):
        return {
            "id": 1,
            "channel_id": channel_id,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def get_messages(self, channel_id: int, limit: int = 50):
        return [
            {"id": i, "channel_id": channel_id, "content": f"msg{i}"} for i in range(limit)
        ]

    async def get_channel_info(self, channel_id: int):
        return {
            "id": channel_id,
            "name": "general",
            "type": 0,
            "guild_id": 123,
        }

    async def delete_message(self, channel_id: int, message_id: int):
        return None

    async def search_messages_keyword(
        self, channel_id: int, keyword: str, limit: int = 100
    ):
        return [
            {
                "id": 99,
                "channel_id": channel_id,
                "content": f"{keyword} found",
            }
        ] 