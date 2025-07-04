from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Request

from app.core.config import settings
from app.core.rate_limit import limiter
from app.dependencies import require_role
from app.models import RoleEnum
from app.services.discord_api import DiscordClient, DiscordAPIError
from app.schemas import (
    SendMessageRequest,
    SendMessageResponse,
    GetMessagesResponse,
    ChannelInfoResponse,
    DeleteMessageRequest,
    SearchMessagesRequest,
)

endpoint_limit = f"{settings.rate_limit_per_endpoint}/minute"

router = APIRouter(prefix="/discord", tags=["Discord"])


# Helper to create client per request (short-lived). In a production system, clients could be pooled.
async def _get_client(bot_token: str) -> DiscordClient:
    return DiscordClient(bot_token)


# ---------------- Helpers ----------------


def _handle_discord_error(err: DiscordAPIError):  # pragma: no cover
    """Convert DiscordAPIError to HTTPException so FastAPI returns proper status.

    If Discord returns a 4xx error (e.g. 401 Unauthorized, 403 Forbidden, 404 Not
    Found), we propagate that status code and message to the caller. For 5xx or
    unknown errors, we return a 502 Bad Gateway indicating an upstream failure.
    """
    status_code = err.status_code
    # Pass through common client errors, otherwise treat as upstream failure
    if 400 <= status_code < 500:
        raise HTTPException(status_code=status_code, detail=err.error)
    # Anything else – treat as Bad Gateway
    raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Upstream Discord API error")


# ---------------- Send Message ----------------


@router.post("/send_message", response_model=SendMessageResponse)
@limiter.limit(endpoint_limit)
async def send_message(
    request: Request,
    payload: SendMessageRequest,
    auth=Depends(require_role(RoleEnum.write)),
):
    client = await _get_client(auth.tenant.discord_bot_token)
    try:
        resp = await client.send_message(payload.channel_id, payload.content)
    except DiscordAPIError as err:
        await client.close()
        _handle_discord_error(err)
    finally:
        # Ensure the client is closed even on success
        await client.close()

    return SendMessageResponse(
        id=int(resp["id"]),
        channel_id=int(resp["channel_id"]),
        content=resp["content"],
        timestamp=resp["timestamp"],
    )


# ---------------- Get Recent Messages ----------------


@router.get("/messages", response_model=GetMessagesResponse)
@limiter.limit(endpoint_limit)
async def get_messages(
    request: Request,
    channel_id: int,
    limit: int = 50,
    auth=Depends(require_role(RoleEnum.read)),
):
    client = await _get_client(auth.tenant.discord_bot_token)
    try:
        messages = await client.get_messages(channel_id, limit=limit)
    except DiscordAPIError as err:
        await client.close()
        _handle_discord_error(err)
    finally:
        await client.close()

    return GetMessagesResponse(messages=messages)


# ---------------- Channel Info ----------------


@router.get("/channel_info", response_model=ChannelInfoResponse)
@limiter.limit(endpoint_limit)
async def channel_info(
    request: Request,
    channel_id: int,
    auth=Depends(require_role(RoleEnum.read)),
):
    client = await _get_client(auth.tenant.discord_bot_token)
    try:
        info = await client.get_channel_info(channel_id)
    except DiscordAPIError as err:
        await client.close()
        _handle_discord_error(err)
    finally:
        await client.close()

    return info


# ---------------- Delete Message ----------------


@router.delete("/delete_message", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(endpoint_limit)
async def delete_message(
    request: Request,
    payload: DeleteMessageRequest,
    auth=Depends(require_role(RoleEnum.write)),
):
    client = await _get_client(auth.tenant.discord_bot_token)
    try:
        await client.delete_message(payload.channel_id, payload.message_id)
    except DiscordAPIError as err:
        await client.close()
        _handle_discord_error(err)
    finally:
        await client.close()

    return None


# ---------------- Search Messages (Keyword Filter) ----------------


@router.post("/search_messages", response_model=GetMessagesResponse)
@limiter.limit(endpoint_limit)
async def search_messages(
    request: Request,
    payload: SearchMessagesRequest,
    auth=Depends(require_role(RoleEnum.read)),
):
    client = await _get_client(auth.tenant.discord_bot_token)
    try:
        messages = await client.search_messages_keyword(payload.channel_id, payload.keyword, payload.limit)
    except DiscordAPIError as err:
        await client.close()
        _handle_discord_error(err)
    finally:
        await client.close()

    return GetMessagesResponse(messages=messages) 