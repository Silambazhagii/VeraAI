from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class MerchantContext(BaseModel):
    model_config = ConfigDict(extra="allow")

    merchant_id: str
    category_slug: str
    identity: dict[str, Any] = Field(default_factory=dict)
    subscription: dict[str, Any] = Field(default_factory=dict)
    performance: dict[str, Any] = Field(default_factory=dict)
    offers: list[dict[str, Any]] = Field(default_factory=list)
    conversation_history: list[dict[str, Any]] = Field(default_factory=list)
    customer_aggregate: dict[str, Any] = Field(default_factory=dict)
    signals: list[str] = Field(default_factory=list)
    review_themes: list[dict[str, Any]] = Field(default_factory=list)
