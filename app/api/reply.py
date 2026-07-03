from fastapi import APIRouter, Depends, HTTPException, status

from app.core.logger import get_logger
from app.models.api_models import ReplyRequest, ReplyResponse
from app.models.enums import CtaType, Intent, ReplyAction
from app.services.context_store import ContextStore, get_context_store
from app.services.conversation_manager import ConversationManager, get_conversation_manager
from app.services.intent_classifier import intent_classifier
from app.utils.helpers import merchant_display_name

logger = get_logger(__name__)
router = APIRouter(prefix="/v1", tags=["reply"])


def get_store() -> ContextStore:
    return get_context_store()


def get_conversations() -> ConversationManager:
    return get_conversation_manager()


def _reply_impl(
    request: ReplyRequest,
    store: ContextStore,
    conversations: ConversationManager,
    conv,
) -> ReplyResponse:
    if conv.status.value == "ended":
        return ReplyResponse(
            action=ReplyAction.END,
            rationale="Conversation already ended",
        )

    merchant_history = [
        t.message for t in conv.history if t.role in ("merchant", "customer")
    ]
    conversations.add_turn(
        request.conversation_id,
        request.from_role,
        request.message,
        request.turn_number,
        request.received_at,
    )

    intent = intent_classifier.classify(request.message, merchant_history)
    conversations.set_intent(request.conversation_id, intent)
    logger.info("Classified intent: %s", intent.value)

    merchant_id = request.merchant_id or conv.merchant_id
    from app.models.enums import ContextScope

    merchant = store.get(ContextScope.MERCHANT, merchant_id) or {}
    owner = merchant_display_name(merchant) if merchant else "there"

    if intent == Intent.AUTO_REPLY:
        count = conversations.increment_auto_reply(request.conversation_id)
        if count == 1:
            body = (
                f"Looks like an auto-reply. When the owner sees this, "
                f"just reply YES for the {conv.trigger_kind.replace('_', ' ')} update."
            )
            conversations.record_bot_message(request.conversation_id, body)
            return ReplyResponse(
                action=ReplyAction.SEND,
                body=body,
                cta=CtaType.BINARY_YES_NO,
                rationale="Detected auto-reply; one explicit prompt for the owner.",
            )
        if count == 2:
            conversations.set_waiting(request.conversation_id)
            return ReplyResponse(
                action=ReplyAction.WAIT,
                wait_seconds=14400,
                rationale="Same auto-reply twice; backing off 4 hours for owner.",
            )
        conversations.end(request.conversation_id)
        return ReplyResponse(
            action=ReplyAction.END,
            rationale="Auto-reply 3x with no real reply; closing conversation.",
        )

    if intent == Intent.STOP:
        store.mark_merchant_opted_out(merchant_id)
        if conv.suppression_key:
            store.mark_suppressed(conv.suppression_key)
        conversations.end(request.conversation_id)
        return ReplyResponse(
            action=ReplyAction.END,
            rationale="Merchant opted out; suppressing future messages.",
        )

    if intent == Intent.LATER:
        conversations.set_waiting(request.conversation_id)
        return ReplyResponse(
            action=ReplyAction.WAIT,
            wait_seconds=1800,
            rationale="Merchant asked for time; backing off 30 minutes.",
        )

    if intent in (Intent.YES, Intent.INTERESTED, Intent.DETAILS, Intent.CALL_ME):
        pending = conv.pending_action or conv.trigger_kind
        body = _action_mode_reply(owner, pending, intent)
        if conversations.body_already_sent(request.conversation_id, body):
            body = _variation_reply(owner, pending)
        conversations.record_bot_message(request.conversation_id, body)
        conversations.set_pending_action(request.conversation_id, "executing")
        return ReplyResponse(
            action=ReplyAction.SEND,
            body=body,
            cta=CtaType.BINARY_CONFIRM_CANCEL if intent == Intent.YES else CtaType.OPEN_ENDED,
            rationale="Honoring merchant commitment; switching to action mode.",
        )

    if intent == Intent.PRICE:
        offers = (merchant.get("offers") or []) if merchant else []
        active = [o for o in offers if o.get("status") == "active"]
        price_text = active[0]["title"] if active else "pricing varies by service"
        body = f"Active offer: {price_text}. Want me to promote this on your Google listing? Reply YES."
        conversations.record_bot_message(request.conversation_id, body)
        return ReplyResponse(
            action=ReplyAction.SEND,
            body=body,
            cta=CtaType.BINARY_YES_NO,
            rationale="Answered pricing question from merchant catalog.",
        )

    if intent == Intent.QUESTION:
        body = (
            f"Good question, {owner}. I can help with GBP posts, recall campaigns, and performance insights. "
            f"Want to continue with the {conv.trigger_kind.replace('_', ' ')} update? Reply YES."
        )
        conversations.record_bot_message(request.conversation_id, body)
        return ReplyResponse(
            action=ReplyAction.SEND,
            body=body,
            cta=CtaType.OPEN_ENDED,
            rationale="Answered question and redirected to original trigger.",
        )

    if intent == Intent.NO:
        conversations.end(request.conversation_id)
        return ReplyResponse(
            action=ReplyAction.END,
            rationale="Merchant declined; closing gracefully.",
        )

    body = f"Got it, {owner}. Reply YES to proceed or STOP to opt out."
    conversations.record_bot_message(request.conversation_id, body)
    return ReplyResponse(
        action=ReplyAction.SEND,
        body=body,
        cta=CtaType.BINARY_YES_NO,
        rationale="Unclear intent; offering simple binary choice.",
    )


@router.post("/reply", response_model=ReplyResponse)
def reply(
    request: ReplyRequest,
    store: ContextStore = Depends(get_store),
    conversations: ConversationManager = Depends(get_conversations),
) -> ReplyResponse:
    logger.info(
        "Reply conv=%s turn=%d role=%s",
        request.conversation_id,
        request.turn_number,
        request.from_role,
    )

    conv = conversations.get(request.conversation_id)
    if not conv:
        # Auto-create conversation for testing/playground
        merchant_id = request.merchant_id or "m_001_drmeera_dentist_delhi"
        from app.models.enums import ContextScope, SendAs
        
        # Load sample category and merchant if store is empty
        if not store.get(ContextScope.MERCHANT, merchant_id):
            store.save(
                scope=ContextScope.MERCHANT,
                context_id=merchant_id,
                version=1,
                payload={
                    "merchant_id": merchant_id,
                    "category_slug": "dentists",
                    "identity": {
                        "name": "Dr. Meera's Dental Clinic",
                        "city": "Delhi",
                        "locality": "Lajpat Nagar",
                        "owner_first_name": "Meera",
                        "languages": ["en", "hi"],
                    },
                    "subscription": {"status": "active", "plan": "Pro", "days_remaining": 82},
                    "performance": {"views": 2410, "calls": 18, "ctr": 0.021},
                    "offers": [{"id": "o1", "title": "Dental Cleaning @ ₹299", "status": "active"}],
                    "signals": ["stale_posts:22d", "ctr_below_peer_median"],
                    "customer_aggregate": {"high_risk_adult_count": 124},
                }
            )
            if not store.get(ContextScope.CATEGORY, "dentists"):
                store.save(
                    scope=ContextScope.CATEGORY,
                    context_id="dentists",
                    version=1,
                    payload={
                        "slug": "dentists",
                        "display_name": "Dentists",
                        "voice": {"tone": "peer_clinical"},
                        "peer_stats": {"avg_ctr": 0.030},
                        "digest": [
                            {
                                "id": "d_2026W17_jida_fluoride",
                                "title": "3-month fluoride recall cuts caries 38% better",
                                "source": "JIDA Oct 2026, p.14",
                                "trial_n": 2100,
                                "patient_segment": "high_risk_adults",
                            }
                        ],
                        "offer_catalog": [{"title": "Dental Cleaning @ ₹299"}],
                    }
                )

        conv = conversations.create(
            conversation_id=request.conversation_id,
            merchant_id=merchant_id,
            trigger_id=f"trg_{request.conversation_id}",
            send_as=SendAs.VERA,
            trigger_kind="research_digest",
            suppression_key="",
            customer_id=request.customer_id,
            pending_action="research_digest",
        )

    res = _reply_impl(request, store, conversations, conv)
    
    # Enrich the response for the frontend command center
    res.intent = conv.last_intent.value if conv.last_intent else None
    res.conversation_state = conv.status.value if conv.status else None
    res.turn_number = len(conv.history)
    return res


def _action_mode_reply(owner: str, pending: str, intent: Intent) -> str:
    action_map = {
        "research_digest": (
            f"Sending the abstract now (PDF, 2 pages). Also drafted a patient-ed WhatsApp below — "
            f"copy-paste ready:\n\n\"3-month vs 6-month cleaning — new research shows it matters "
            f"for high-risk patients. Reply to book a quick check.\"\n\n"
            f"Want me to schedule the Google post for tomorrow 10am?"
        ),
        "renewal_due": (
            f"Great, {owner}. Sending your Pro renewal link now — ₹4,999 for 12 months. "
            f"Confirm and I'll activate within 5 minutes."
        ),
        "performance_drop": (
            f"On it. Refreshing your Google posts + boosting the listing for {_locality_placeholder(owner)}. "
            f"I'll share a before/after CTR snapshot in 48 hours."
        ),
        "recall_due": (
            f"Done — recall reminder queued for your patient list. "
            f"Confirm slot preference and I'll finalize the booking message."
        ),
        "regulation_change": (
            f"Pulling the DCI compliance summary + checklist now. "
            f"2-page PDF ready in 90 seconds. Reply CONFIRM to send to your team."
        ),
        "festival": (
            f"Drafting your festival Google post + offer copy now. "
            f"Preview in 2 minutes — reply CONFIRM to schedule."
        ),
        "review_request": (
            f"Sharing the review response template + GBP post draft now. "
            f"Both address the wait-time theme from this week's reviews."
        ),
        "active_offer": (
            f"Creating the Google post for your active offer now. "
            f"Preview ready in 2 minutes — reply CONFIRM to publish."
        ),
    }
    normalized = pending.replace("perf_dip", "performance_drop").replace("review_theme_emerged", "review_request")
    default = (
        f"Great, {owner}. Executing next step for {normalized.replace('_', ' ')} — "
        f"you'll have a draft in 90 seconds. Reply CONFIRM to proceed."
    )
    if intent == Intent.CALL_ME:
        return f"Noted, {owner}. I'll have the team call you within 2 hours to walk through the next steps."
    return action_map.get(normalized, default)


def _variation_reply(owner: str, pending: str) -> str:
    return (
        f"{owner}, continuing — your {pending.replace('_', ' ')} update is ready. "
        f"Reply CONFIRM to send or STOP to cancel."
    )


def _locality_placeholder(owner: str) -> str:
    return "your locality"
