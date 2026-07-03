from fastapi import APIRouter

from app.core.config import get_settings
from app.models.api_models import MetadataResponse

router = APIRouter(prefix="/v1", tags=["metadata"])


@router.get("/metadata", response_model=MetadataResponse)
def metadata() -> MetadataResponse:
    settings = get_settings()
    return MetadataResponse(
        team_name=settings.team_name,
        model=settings.model_name,
        approach=settings.approach,
        version=settings.version,
        contact_email=settings.contact_email,
        environment="development",
        architecture="Clean Architecture (API, Services, Models)",
        llm_provider="Mock LLM / Template Composer",
        storage="Thread-Safe In-Memory Context Store",
    )
