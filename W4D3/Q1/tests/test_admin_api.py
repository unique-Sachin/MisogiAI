import pytest


@pytest.mark.asyncio
async def test_admin_api_key_lifecycle(client, admin_key):
    headers = {"X-API-Key": admin_key}

    # Create new write key
    resp = await client.post("/admin/api-keys", json={"role": "write"}, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    new_key_id = data["id"]
    assert data["role"] == "write"
    assert "secret" in data

    # List keys should include new key
    resp = await client.get("/admin/api-keys", headers=headers)
    assert resp.status_code == 200
    keys = resp.json()
    assert any(k["id"] == new_key_id for k in keys)

    # Revoke key
    resp = await client.delete(f"/admin/api-keys/{new_key_id}", headers=headers)
    assert resp.status_code == 204 