from typing import Any, Optional

from app.core.logger import get_logger
from app.models.api_models import Decision
from app.services.context_store import ContextStore
from app.services.trigger_router import TriggerRouter

logger = get_logger(__name__)


class DecisionEngine:
    """Pure deterministic decision engine — no LLM."""

    def __init__(self, store: ContextStore, router: Optional[TriggerRouter] = None) -> None:
        self._store = store
        self._router = router or TriggerRouter()

    def evaluate_trigger(
        self, trigger_id: str
    ) -> tuple[Decision, dict[str, Any], dict[str, Any], dict[str, Any], Optional[dict[str, Any]]]:
        category, merchant, trigger, customer = self._store.resolve_contexts(trigger_id)

        empty_decision = Decision(
            should_send=False,
            priority="low",
            reason="Missing context",
            action_type="skip",
        )

        if not trigger:
            return empty_decision, {}, {}, {}, None
        if not merchant:
            d = Decision(should_send=False, priority="low", reason="Merchant context missing", action_type="skip")
            return d, category or {}, {}, trigger, customer
        if not category:
            d = Decision(should_send=False, priority="low", reason="Category context missing", action_type="skip")
            return d, {}, merchant, trigger, customer

        merchant_id = merchant.get("merchant_id", "")
        if self._store.is_merchant_opted_out(merchant_id):
            return (
                Decision(should_send=False, priority="low", reason="Merchant opted out", action_type="skip"),
                category,
                merchant,
                trigger,
                customer,
            )

        suppression_key = trigger.get("suppression_key", "")
        if suppression_key and self._store.is_suppressed(suppression_key):
            return (
                Decision(should_send=False, priority="low", reason="Trigger suppressed", action_type="skip"),
                category,
                merchant,
                trigger,
                customer,
            )

        decision = self._router.decide(category, merchant, trigger, customer)
        logger.info(
            "Decision for trigger %s: send=%s priority=%s",
            trigger_id,
            decision.should_send,
            decision.priority,
        )
        return decision, category, merchant, trigger, customer
