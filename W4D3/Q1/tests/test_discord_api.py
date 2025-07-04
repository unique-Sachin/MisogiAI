import pytest

from tests.mock_discord import MockDiscordClient
import app.api.discord as discord_api_module


@pytest.fixture(autouse=True)
def patch_discord_client(monkeypatch):
    async def _mock_get_client(_token):
        return MockDiscordClient(_token)

    monkeypatch.setattr(discord_api_module, "_get_client", _mock_get_client)


@pytest.mark.asyncio
async def test_discord_endpoints(client, admin_key):
    headers = {"X-API-Key": admin_key}

    # send message
    resp = await client.post(
        "/discord/send_message",
        json={"channel_id": 123, "content": "hello"},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["content"] == "hello"
    assert data["channel_id"] == 123

    # get messages
    resp = await client.get("/discord/messages", params={"channel_id": 123}, headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()["messages"]) > 0

    # channel info
    resp = await client.get("/discord/channel_info", params={"channel_id": 123}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == 123

    # delete message
    resp = await client.request(
        "DELETE",
        "/discord/delete_message",
        json={"channel_id": 123, "message_id": 1},
        headers=headers,
    )
    assert resp.status_code == 204

    # search messages
    resp = await client.post(
        "/discord/search_messages",
        json={"channel_id": 123, "keyword": "hello"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert len(resp.json()["messages"]) >= 1 