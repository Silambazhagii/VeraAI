from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class CustomerContext(BaseModel):
    model_config = ConfigDict(extra="allow")

    customer_id: str
    merchant_id: str
    identity: dict[str, Any] = Field(default_factory=dict)
    relationship: dict[str, Any] = Field(default_factory=dict)
    state: Optional[str] = None
    preferences: dict[str, Any] = Field(default_factory=dict)
    consent: dict[str, Any] = Field(default_factory=dict)
