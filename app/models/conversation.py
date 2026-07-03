from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.models.enums import ConversationStatus, Intent, SendAs


class ConversationTurn(BaseModel):
    turn_number: int
    role: str
    message: str
    received_at: Optional[str] = None


class ConversationState(BaseModel):
    conversation_id: str
    merchant_id: str
    customer_id: Optional[str] = None
    trigger_id: str
    send_as: SendAs = SendAs.VERA
    trigger_kind: str = ""
    suppression_key: str = ""
    status: ConversationStatus = ConversationStatus.ACTIVE
    history: list[ConversationTurn] = Field(default_factory=list)
    last_intent: Intent = Intent.UNKNOWN
    pending_action: Optional[str] = None
    auto_reply_count: int = 0
    bodies_sent: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
