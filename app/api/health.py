import time

from fastapi import APIRouter, Depends

from app.models.api_models import HealthResponse
from app.services.context_store import ContextStore, get_context_store

router = APIRouter(prefix="/v1", tags=["health"])

_START_TIME = time.time()


def get_store() -> ContextStore:
    return get_context_store()


@router.get("/healthz", response_model=HealthResponse)
def healthz(store: ContextStore = Depends(get_store)) -> HealthResponse:
    return HealthResponse(
        status="ok",
        uptime_seconds=int(time.time() - _START_TIME),
        contexts_loaded=store.counts(),
    )


@router.post("/reset")
def reset_endpoint(
    store: ContextStore = Depends(get_store),
) -> dict:
    from app.services.conversation_manager import get_conversation_manager
    store.clear()
    get_conversation_manager().clear()
    
    # Reload seeds
    from pathlib import Path
    import json
    from app.models.enums import ContextScope
    
    dataset_dir = Path("dataset")
    if dataset_dir.exists():
        # Categories
        categories_dir = dataset_dir / "categories"
        if categories_dir.exists():
            for file in categories_dir.glob("*.json"):
                with open(file, "r") as f:
                    payload = json.load(f)
                    slug = payload.get("slug")
                    if slug:
                        store.save(ContextScope.CATEGORY, slug, 1, payload, "2026-04-26T10:00:00Z")
        # Merchants
        merchants_file = dataset_dir / "merchants_seed.json"
        if merchants_file.exists():
            with open(merchants_file, "r") as f:
                merchants_data = json.load(f)
                merchants = merchants_data.get("merchants", [])
                for item in merchants:
                    merchant_id = item.get("merchant_id")
                    if merchant_id:
                        store.save(ContextScope.MERCHANT, merchant_id, 1, item, "2026-04-26T10:00:00Z")
        # Customers
        customers_file = dataset_dir / "customers_seed.json"
        if customers_file.exists():
            with open(customers_file, "r") as f:
                customers_data = json.load(f)
                customers = customers_data.get("customers", [])
                for item in customers:
                    customer_id = item.get("customer_id")
                    if customer_id:
                        store.save(ContextScope.CUSTOMER, customer_id, 1, item, "2026-04-26T10:00:00Z")
        # Triggers
        triggers_file = dataset_dir / "triggers_seed.json"
        if triggers_file.exists():
            with open(triggers_file, "r") as f:
                triggers_data = json.load(f)
                triggers = triggers_data.get("triggers", [])
                for item in triggers:
                    trigger_id = item.get("id")
                    if trigger_id:
                        store.save(ContextScope.TRIGGER, trigger_id, 1, item, "2026-04-26T10:00:00Z")
                        
    return {"status": "ok", "message": "State reset and re-seeded successfully"}
