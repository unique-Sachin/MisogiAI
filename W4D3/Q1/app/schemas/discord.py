from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class SendMessageRequest(BaseModel):
    channel_id: int = Field(..., description="Discord channel ID")
    content: str = Field(..., description="Message content")


class SendMessageResponse(BaseModel):
    id: int
    channel_id: int
    content: str
    timestamp: datetime


class GetMessagesResponse(BaseModel):
    messages: List[dict]


class ChannelInfoResponse(BaseModel):
    id: int
    name: Optional[str]
    type: int
    guild_id: Optional[int]

    model_config = {"from_attributes": True}


class DeleteMessageRequest(BaseModel):
    channel_id: int
    message_id: int


class SearchMessagesRequest(BaseModel):
    channel_id: int
    keyword: str = Field(..., description="Case-insensitive keyword to search in message content")
    limit: int = Field(100, ge=1, le=100) 