from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import uuid
from datetime import datetime

class ChatMessage(BaseModel):
    id: str
    content: str
    role: str  # 'user' or 'assistant'
    timestamp: datetime
    
class ConversationState(BaseModel):
    """State object for managing conversation flow in LangGraph"""
    conversation_id: str
    messages: List[ChatMessage]
    current_step: str
    user_input: str
    processed_input: str
    llm_response: str
    final_response: str
    metadata: Dict[str, Any]
    
    @classmethod
    def create_new(cls, user_input: str) -> "ConversationState":
        """Create a new conversation state"""
        return cls(
            conversation_id=str(uuid.uuid4()),
            messages=[],
            current_step="input",
            user_input=user_input,
            processed_input="",
            llm_response="",
            final_response="",
            metadata={}
        )
    
    def add_message(self, content: str, role: str) -> None:
        """Add a message to the conversation"""
        message = ChatMessage(
            id=str(uuid.uuid4()),
            content=content,
            role=role,
            timestamp=datetime.now()
        )
        self.messages.append(message)

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    status: str
