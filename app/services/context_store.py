import threading
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from app.core.logger import get_logger
from app.models.enums import ContextScope

logger = get_logger(__name__)


class StoreResult(str, Enum):
    INSERTED = "inserted"
    REPLACED = "replaced"
    IGNORED = "ignored"
    REJECTED = "rejected"


@dataclass
class ContextEntry:
    context_id: str
    version: int
    payload: dict[str, Any]
    delivered_at: str = ""


@dataclass
class SaveResult:
    result: StoreResult
    current_version: Optional[int] = None


class ContextStore:
    """Thread-safe in-memory context store with version control."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._categories: dict[str, ContextEntry] = {}
        self._merchants: dict[str, ContextEntry] = {}
        self._customers: dict[str, ContextEntry] = {}
        self._triggers: dict[str, ContextEntry] = {}
        self._suppressed_keys: set[str] = set()
        self._opted_out_merchants: set[str] = set()

    def _bucket(self, scope: ContextScope) -> dict[str, ContextEntry]:
        mapping = {
            ContextScope.CATEGORY: self._categories,
            ContextScope.MERCHANT: self._merchants,
            ContextScope.CUSTOMER: self._customers,
            ContextScope.TRIGGER: self._triggers,
        }
        return mapping[scope]

    def save(
        self,
        scope: ContextScope,
        context_id: str,
        version: int,
        payload: dict[str, Any],
        delivered_at: str = "",
    ) -> SaveResult:
        with self._lock:
            store = self._bucket(scope)
            existing = store.get(context_id)

            if existing is None:
                store[context_id] = ContextEntry(
                    context_id=context_id,
                    version=version,
                    payload=payload,
                    delivered_at=delivered_at,
                )
                if scope == ContextScope.MERCHANT and context_id in self._opted_out_merchants:
                    self._opted_out_merchants.remove(context_id)
                logger.info("Inserted context scope=%s id=%s v=%s", scope.value, context_id, version)
                return SaveResult(result=StoreResult.INSERTED)

            if version > existing.version:
                store[context_id] = ContextEntry(
                    context_id=context_id,
                    version=version,
                    payload=payload,
                    delivered_at=delivered_at,
                )
                if scope == ContextScope.MERCHANT and context_id in self._opted_out_merchants:
                    self._opted_out_merchants.remove(context_id)
                logger.info(
                    "Replaced context scope=%s id=%s v%s->v%s",
                    scope.value,
                    context_id,
                    existing.version,
                    version,
                )
                return SaveResult(result=StoreResult.REPLACED)

            if version == existing.version:
                logger.info("Ignored duplicate context scope=%s id=%s v=%s", scope.value, context_id, version)
                return SaveResult(result=StoreResult.IGNORED, current_version=existing.version)

            logger.warning(
                "Rejected stale context scope=%s id=%s incoming=%s current=%s",
                scope.value,
                context_id,
                version,
                existing.version,
            )
            return SaveResult(result=StoreResult.REJECTED, current_version=existing.version)

    def get(self, scope: ContextScope, context_id: str) -> Optional[dict[str, Any]]:
        with self._lock:
            entry = self._bucket(scope).get(context_id)
            return entry.payload if entry else None

    def get_version(self, scope: ContextScope, context_id: str) -> Optional[int]:
        with self._lock:
            entry = self._bucket(scope).get(context_id)
            return entry.version if entry else None

    def counts(self) -> dict[str, int]:
        with self._lock:
            return {
                "category": len(self._categories),
                "merchant": len(self._merchants),
                "customer": len(self._customers),
                "trigger": len(self._triggers),
            }

    def get_trigger(self, trigger_id: str) -> Optional[dict[str, Any]]:
        return self.get(ContextScope.TRIGGER, trigger_id)

    def resolve_contexts(
        self, trigger_id: str
    ) -> tuple[Optional[dict[str, Any]], Optional[dict[str, Any]], Optional[dict[str, Any]], Optional[dict[str, Any]]]:
        trigger = self.get_trigger(trigger_id)
        if not trigger:
            return None, None, None, None

        merchant_id = trigger.get("merchant_id")
        customer_id = trigger.get("customer_id")
        merchant = self.get(ContextScope.MERCHANT, merchant_id) if merchant_id else None
        customer = self.get(ContextScope.CUSTOMER, customer_id) if customer_id else None

        category_slug = None
        if merchant:
            category_slug = merchant.get("category_slug")
        if not category_slug:
            category_slug = (trigger.get("payload") or {}).get("category")

        category = self.get(ContextScope.CATEGORY, category_slug) if category_slug else None
        return category, merchant, trigger, customer

    def is_suppressed(self, key: str) -> bool:
        with self._lock:
            return key in self._suppressed_keys

    def mark_suppressed(self, key: str) -> None:
        with self._lock:
            self._suppressed_keys.add(key)

    def is_merchant_opted_out(self, merchant_id: str) -> bool:
        with self._lock:
            return merchant_id in self._opted_out_merchants

    def mark_merchant_opted_out(self, merchant_id: str) -> None:
        with self._lock:
            self._opted_out_merchants.add(merchant_id)

    def clear(self) -> None:
        with self._lock:
            self._categories.clear()
            self._merchants.clear()
            self._customers.clear()
            self._triggers.clear()
            self._suppressed_keys.clear()
            self._opted_out_merchants.clear()


_store: Optional[ContextStore] = None


def get_context_store() -> ContextStore:
    global _store
    if _store is None:
        _store = ContextStore()
    return _store
