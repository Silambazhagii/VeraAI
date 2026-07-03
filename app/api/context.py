from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.core.logger import get_logger
from app.models.api_models import ContextPushRequest, ContextPushResponse
from app.models.category import CategoryContext
from app.models.customer import CustomerContext
from app.models.enums import ContextScope
from app.models.merchant import MerchantContext
from app.models.trigger import TriggerContext
from app.services.context_store import ContextStore, SaveResult, StoreResult, get_context_store
from app.utils.helpers import utc_now_iso
from app.utils.ids import generate_ack_id

logger = get_logger(__name__)
router = APIRouter(prefix="/v1", tags=["context"])

_VALIDATORS = {
    ContextScope.CATEGORY: CategoryContext,
    ContextScope.MERCHANT: MerchantContext,
    ContextScope.CUSTOMER: CustomerContext,
    ContextScope.TRIGGER: TriggerContext,
}


def get_store() -> ContextStore:
    return get_context_store()


def _validate_payload(scope: ContextScope, payload: dict) -> dict:
    model_cls = _VALIDATORS.get(scope)
    if not model_cls:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"accepted": False, "reason": "invalid_scope", "details": f"Unknown scope: {scope}"},
        )
    try:
        validated = model_cls.model_validate(payload)
        return validated.model_dump()
    except Exception as exc:
        logger.warning("Payload validation failed for scope %s: %s", scope.value, exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"accepted": False, "reason": "invalid_payload", "details": str(exc)},
        ) from exc


@router.post("/context", response_model=ContextPushResponse)
def push_context(
    request: ContextPushRequest,
    store: ContextStore = Depends(get_store),
) -> ContextPushResponse:
    logger.info(
        "Context push scope=%s id=%s version=%s",
        request.scope.value,
        request.context_id,
        request.version,
    )

    validated_payload = _validate_payload(request.scope, request.payload)
    result: SaveResult = store.save(
        scope=request.scope,
        context_id=request.context_id,
        version=request.version,
        payload=validated_payload,
        delivered_at=request.delivered_at,
    )

    if result.result == StoreResult.REJECTED:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "accepted": False,
                "reason": "stale_version",
                "current_version": result.current_version,
            },
        )

    return ContextPushResponse(
        accepted=True,
        ack_id=generate_ack_id(request.context_id, request.version),
        stored_at=utc_now_iso(),
    )
