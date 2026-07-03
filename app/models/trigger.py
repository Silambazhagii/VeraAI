from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class TriggerContext(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    scope: str
    kind: str
    source: Optional[str] = None
    merchant_id: Optional[str] = None
    customer_id: Optional[str] = None
    payload: dict[str, Any] = Field(default_factory=dict)
    urgency: int = 1
    suppression_key: str = ""
    expires_at: Optional[str] = None
