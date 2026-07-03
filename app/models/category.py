from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class CategoryContext(BaseModel):
    model_config = ConfigDict(extra="allow")

    slug: str
    display_name: Optional[str] = None
    voice: dict[str, Any] = Field(default_factory=dict)
    offer_catalog: list[dict[str, Any]] = Field(default_factory=list)
    peer_stats: dict[str, Any] = Field(default_factory=dict)
    digest: list[dict[str, Any]] = Field(default_factory=list)
    patient_content_library: list[dict[str, Any]] = Field(default_factory=list)
    seasonal_beats: list[dict[str, Any]] = Field(default_factory=list)
    trend_signals: list[dict[str, Any]] = Field(default_factory=list)
