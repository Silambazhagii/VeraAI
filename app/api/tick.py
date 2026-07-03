from fastapi import APIRouter, Depends

from app.core.logger import get_logger
from app.models.api_models import TickAction, TickRequest, TickResponse
from app.services.context_store import ContextStore, get_context_store
from app.services.conversation_manager import ConversationManager, get_conversation_manager
from app.services.decision_engine import DecisionEngine
from app.services.message_composer import MessageComposer
from app.services.scoring_rules import ensure_merchant_anchor
from app.utils.ids import generate_conversation_id

logger = get_logger(__name__)
router = APIRouter(prefix="/v1", tags=["tick"])


def get_store() -> ContextStore:
    return get_context_store()


def get_conversations() -> ConversationManager:
    return get_conversation_manager()


def get_decision_engine(store: ContextStore = Depends(get_store)) -> DecisionEngine:
    return DecisionEngine(store)


def get_composer() -> MessageComposer:
    return MessageComposer()


@router.post("/tick", response_model=TickResponse)
def tick(
    request: TickRequest,
    store: ContextStore = Depends(get_store),
    conversations: ConversationManager = Depends(get_conversations),
    engine: DecisionEngine = Depends(get_decision_engine),
    composer: MessageComposer = Depends(get_composer),
) -> TickResponse:
    logger.info("Tick at %s with triggers: %s", request.now, request.available_triggers)
    actions: list[TickAction] = []

    for trigger_id in request.available_triggers[:20]:
        decision, category, merchant, trigger, customer = engine.evaluate_trigger(trigger_id)
        if not decision.should_send:
            logger.info("Skipping trigger %s: %s", trigger_id, decision.reason)
            continue

        merchant_id = merchant.get("merchant_id", "")
        if conversations.has_active_conversation(merchant_id, trigger_id):
            logger.info("Active conversation exists for %s/%s", merchant_id, trigger_id)
            continue

        body = composer.compose(decision, category, merchant, trigger, customer)
        body = ensure_merchant_anchor(body, merchant)

        conversation_id = generate_conversation_id()
        customer_id = trigger.get("customer_id") or (customer.get("customer_id") if customer else None)
        suppression_key = trigger.get("suppression_key", "")

        conversations.create(
            conversation_id=conversation_id,
            merchant_id=merchant_id,
            trigger_id=trigger_id,
            send_as=decision.send_as,
            trigger_kind=trigger.get("kind", ""),
            suppression_key=suppression_key,
            customer_id=customer_id,
            pending_action=decision.objective,
        )
        conversations.record_bot_message(conversation_id, body)

        if suppression_key:
            store.mark_suppressed(suppression_key)

        template_params = composer.build_template_params(body, merchant, customer)
        rationale = (
            f"{decision.priority.upper()} priority {decision.objective} for "
            f"{decision.recipient}; {decision.reason}"
        )

        actions.append(
            TickAction(
                conversation_id=conversation_id,
                merchant_id=merchant_id,
                customer_id=customer_id,
                send_as=decision.send_as,
                trigger_id=trigger_id,
                template_name=decision.template_name,
                template_params=template_params,
                body=body,
                cta=decision.cta,
                suppression_key=suppression_key,
                rationale=rationale,
            )
        )

    logger.info("Tick returning %d action(s)", len(actions))
    return TickResponse(actions=actions)
