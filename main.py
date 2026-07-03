from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, FileResponse

from app.api import context, health, metadata, reply, tick
from app.core.logger import get_logger, setup_logging
from app.services.context_store import get_context_store
from app.models.enums import ContextScope

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Magicpin AI Bot starting")
    try:
        from pathlib import Path
        import json
        
        store = get_context_store()
        dataset_dir = Path("dataset")
        if dataset_dir.exists():
            # 1. Categories
            categories_dir = dataset_dir / "categories"
            if categories_dir.exists():
                for file in categories_dir.glob("*.json"):
                    with open(file, "r") as f:
                        payload = json.load(f)
                        slug = payload.get("slug")
                        if slug:
                            store.save(ContextScope.CATEGORY, slug, 1, payload, "2026-04-26T10:00:00Z")
                            
            # 2. Merchants
            merchants_file = dataset_dir / "merchants_seed.json"
            if merchants_file.exists():
                with open(merchants_file, "r") as f:
                    merchants_data = json.load(f)
                    merchants = merchants_data.get("merchants", [])
                    for item in merchants:
                        merchant_id = item.get("merchant_id")
                        if merchant_id:
                            store.save(ContextScope.MERCHANT, merchant_id, 1, item, "2026-04-26T10:00:00Z")
                            
            # 3. Customers
            customers_file = dataset_dir / "customers_seed.json"
            if customers_file.exists():
                with open(customers_file, "r") as f:
                    customers_data = json.load(f)
                    customers = customers_data.get("customers", [])
                    for item in customers:
                        customer_id = item.get("customer_id")
                        if customer_id:
                            store.save(ContextScope.CUSTOMER, customer_id, 1, item, "2026-04-26T10:00:00Z")
                            
            # 4. Triggers
            triggers_file = dataset_dir / "triggers_seed.json"
            if triggers_file.exists():
                with open(triggers_file, "r") as f:
                    triggers_data = json.load(f)
                    triggers = triggers_data.get("triggers", [])
                    for item in triggers:
                        trigger_id = item.get("id")
                        if trigger_id:
                            store.save(ContextScope.TRIGGER, trigger_id, 1, item, "2026-04-26T10:00:00Z")
            logger.info("Successfully loaded seed dataset into ContextStore")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
    yield
    logger.info("Magicpin AI Bot shutting down")


app = FastAPI(
    title="Magicpin AI Bot",
    description="Intelligent AI Merchant Assistant for Magicpin AI Challenge",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(metadata.router)
app.include_router(context.router)
app.include_router(tick.router)
app.include_router(reply.router)


@app.get("/")
async def read_index():
    return FileResponse("static/index.html")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error on %s %s: %s", request.method, request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"},
    )
