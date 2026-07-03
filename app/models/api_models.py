from typing import Any, Optional

from pydantic import BaseModel, Field

from app.models.enums import ContextScope, CtaType, ReplyAction, SendAs


class HealthResponse(BaseModel):
    status: str
    uptime_seconds: int
    contexts_loaded: dict[str, int]


class MetadataResponse(BaseModel):
    team_name: str
    model: str
    approach: str
    version: str
    contact_email: str
    environment: Optional[str] = "development"
    architecture: Optional[str] = "Clean Architecture (API, Services, Models)"
    llm_provider: Optional[str] = "Mock LLM / Template Composer"
    storage: Optional[str] = "Thread-Safe In-Memory Context Store"


class ContextPushRequest(BaseModel):
    scope: ContextScope
    context_id: str
    version: int
    payload: dict[str, Any]
    delivered_at: str


class ContextPushResponse(BaseModel):
    accepted: bool
    ack_id: Optional[str] = None
    stored_at: Optional[str] = None
    reason: Optional[str] = None
    current_version: Optional[int] = None


class TickRequest(BaseModel):
    now: str
    available_triggers: list[str] = Field(default_factory=list)


class TickAction(BaseModel):
    conversation_id: str
    merchant_id: str
    customer_id: Optional[str] = None
    send_as: SendAs = SendAs.VERA
    trigger_id: str
    template_name: str
    template_params: list[str] = Field(default_factory=list)
    body: str
    cta: CtaType
    suppression_key: str
    rationale: str


class TickResponse(BaseModel):
    actions: list[TickAction] = Field(default_factory=list)


class ReplyRequest(BaseModel):
    conversation_id: str
    merchant_id: Optional[str] = None
    customer_id: Optional[str] = None
    from_role: str = "merchant"
    message: str
    received_at: str
    turn_number: int


class ReplyResponse(BaseModel):
    action: ReplyAction
    body: Optional[str] = None
    cta: Optional[CtaType] = None
    wait_seconds: Optional[int] = None
    rationale: str
    intent: Optional[str] = None
    conversation_state: Optional[str] = None
    turn_number: Optional[int] = None


class Decision(BaseModel):
    should_send: bool
    priority: str
    reason: str
    action_type: str
    send_as: SendAs = SendAs.VERA
    recipient: str = "merchant"
    template_name: str = "vera_generic_v1"
    cta: CtaType = CtaType.OPEN_ENDED
    objective: str = "general_outreach"
