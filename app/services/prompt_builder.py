from dataclasses import dataclass, field
from typing import Any, Optional

from app.utils.helpers import (
    customer_display_name,
    first_active_offer_title,
    format_ctr,
    merchant_display_name,
    merchant_full_name,
    safe_get,
)


@dataclass
class ComposedPrompt:
    """Structured prompt object — independent from LLM implementation."""

    objective: str
    trigger_kind: str
    category_slug: str
    tone: str
    merchant: dict[str, Any]
    trigger: dict[str, Any]
    category: dict[str, Any]
    customer: Optional[dict[str, Any]] = None
    facts: list[str] = field(default_factory=list)
    cta_instruction: str = ""
    send_as: str = "vera"
    template_id: str = "generic_v1"

    def render_template(self) -> str:
        """Deterministic WhatsApp message from structured facts."""
        renderer = _TEMPLATE_RENDERERS.get(self.objective, _render_generic)
        return renderer(self)


def _owner_name(prompt: ComposedPrompt) -> str:
    return merchant_display_name(prompt.merchant)


def _business_name(prompt: ComposedPrompt) -> str:
    return merchant_full_name(prompt.merchant)


def _locality(prompt: ComposedPrompt) -> str:
    return safe_get(prompt.merchant, "identity", "locality", default="")


def _city(prompt: ComposedPrompt) -> str:
    return safe_get(prompt.merchant, "identity", "city", default="")


def _peer_ctr(prompt: ComposedPrompt) -> str:
    peer = prompt.category.get("peer_stats") or {}
    ctr = peer.get("avg_ctr", 0.03)
    return format_ctr(float(ctr))


def _merchant_ctr(prompt: ComposedPrompt) -> str:
    perf = prompt.merchant.get("performance") or {}
    ctr = perf.get("ctr", 0.02)
    return format_ctr(float(ctr))


def _digest_item(prompt: ComposedPrompt) -> dict[str, Any]:
    top_id = safe_get(prompt.trigger, "payload", "top_item_id")
    digest = prompt.category.get("digest") or []
    if top_id:
        for item in digest:
            if item.get("id") == top_id:
                return item
    return digest[0] if digest else {}


def _render_research_digest(p: ComposedPrompt) -> str:
    item = _digest_item(p)
    owner = _owner_name(p)
    title = item.get("title", "new clinical research")
    source = item.get("source", "")
    trial_n = item.get("trial_n")
    segment = item.get("patient_segment", "").replace("_", " ")

    trial_part = f"{trial_n:,}-patient trial" if trial_n else "recent trial"
    segment_part = f" for your {segment} patients" if segment else ""
    source_part = f" — {source}" if source else ""

    return (
        f"Dr. {owner}, JIDA's latest landed. One item relevant{segment_part} — "
        f"{trial_part}: {title}. Worth a 2-min read. "
        f"Want me to pull the abstract + draft a patient-ed WhatsApp you can share?{source_part}"
    )


def _render_renewal_due(p: ComposedPrompt) -> str:
    owner = _owner_name(p)
    sub = p.merchant.get("subscription") or {}
    days = sub.get("days_remaining") or safe_get(p.trigger, "payload", "days_remaining", default=14)
    plan = sub.get("plan") or safe_get(p.trigger, "payload", "plan", default="Pro")
    amount = safe_get(p.trigger, "payload", "renewal_amount")
    amount_part = f" (₹{amount:,})" if amount else ""
    business = _business_name(p)

    return (
        f"Hi {owner}, quick heads-up — {business}'s {plan} plan expires in {days} days{amount_part}. "
        f"Renew now to keep GBP posts, recall campaigns, and performance insights active. "
        f"Reply YES and I'll send the renewal link."
    )


def _render_recall_due(p: ComposedPrompt) -> str:
    customer = p.customer or {}
    name = customer_display_name(customer)
    business = _business_name(p)
    offer = first_active_offer_title(p.merchant) or "cleaning @ ₹299"
    slots = safe_get(p.trigger, "payload", "available_slots", default=[])
    slot_text = ""
    if len(slots) >= 2:
        slot_text = f" Apke liye 2 slots: {slots[0].get('label')} ya {slots[1].get('label')}."
    elif len(slots) == 1:
        slot_text = f" Slot available: {slots[0].get('label')}."

    last_visit = safe_get(customer, "relationship", "last_visit", default="")
    months_part = "your recall is due"
    if last_visit:
        months_part = f"it's been a while since your visit ({last_visit[:7]}) — recall is due"

    return (
        f"Hi {name}, {business} here. {months_part.capitalize()}.{slot_text} "
        f"{offer}. Reply 1 or 2 to book, or tell us a time that works."
    )


def _render_festival(p: ComposedPrompt) -> str:
    owner = _owner_name(p)
    festival = safe_get(p.trigger, "payload", "festival", default="the upcoming festival")
    days = safe_get(p.trigger, "payload", "days_until")
    offer = first_active_offer_title(p.merchant)
    locality = _locality(p)
    days_part = f" ({days} days away)" if days else ""
    offer_part = f" Your active offer '{offer}' is ready to promote." if offer else " Want me to draft a festival post + offer?"

    return (
        f"Hi {owner}, {festival}{days_part} is coming — {locality} footfall typically spikes. "
        f"{offer_part} Reply YES to schedule a Google post for the week before."
    )


def _render_review_request(p: ComposedPrompt) -> str:
    owner = _owner_name(p)
    theme = safe_get(p.trigger, "payload", "theme", default="service quality")
    count = safe_get(p.trigger, "payload", "occurrences_30d", default=3)
    quote = safe_get(p.trigger, "payload", "common_quote", default="")
    quote_part = f' — merchants mention "{quote[:60]}"' if quote else ""

    return (
        f"Hi {owner}, {count} recent reviews in {_locality(p)} flagged '{theme.replace('_', ' ')}'{quote_part}. "
        f"I've drafted a response template + a GBP post addressing wait times. "
        f"Want me to share both? Reply YES."
    )


def _render_regulation_change(p: ComposedPrompt) -> str:
    owner = _owner_name(p)
    item = _digest_item(p)
    title = item.get("title", "regulatory update")
    source = item.get("source", "")
    deadline = safe_get(p.trigger, "payload", "deadline_iso", default="")

    deadline_part = f" Effective {deadline[:10]}." if deadline else ""
    return (
        f"Dr. {owner}, compliance update: {title}.{deadline_part} "
        f"Worth a 3-min review for your clinic ops. Want the summary + checklist? — {source}"
    )


def _render_performance_drop(p: ComposedPrompt) -> str:
    owner = _owner_name(p)
    metric = safe_get(p.trigger, "payload", "metric", default="calls")
    delta = safe_get(p.trigger, "payload", "delta_pct", default=-0.3)
    pct = abs(int(float(delta) * 100))
    ctr = _merchant_ctr(p)
    peer = _peer_ctr(p)
    offer = first_active_offer_title(p.merchant)

    return (
        f"Hi {owner}, your {metric} dropped {pct}% this week (profile CTR {ctr} vs peer {peer}). "
        f"{'Active offer: ' + offer + '. ' if offer else ''}"
        f"I can refresh your Google posts + boost the listing — 5-min setup. Reply YES to start."
    )


def _render_customer_followup(p: ComposedPrompt) -> str:
    customer = p.customer or {}
    name = customer_display_name(customer)
    business = _business_name(p)
    return (
        f"Hi {name}, {business} here. We wanted to follow up on your last visit — "
        f"we have slots open this week. Reply YES and we'll share times that work for you."
    )


def _render_subscription_expiry(p: ComposedPrompt) -> str:
    return _render_renewal_due(p)


def _render_active_offer(p: ComposedPrompt) -> str:
    owner = _owner_name(p)
    offer = first_active_offer_title(p.merchant)
    if not offer:
        catalog = p.category.get("offer_catalog") or []
        offer = catalog[0]["title"] if catalog else "a new service offer"
    return (
        f"Hi {owner}, your listing in {_city(p)} could use a boost — "
        f"promote '{offer}' on Google this week. I can draft the post now. Reply YES to review."
    )


def _render_generic(p: ComposedPrompt) -> str:
    owner = _owner_name(p)
    facts = " ".join(p.facts[:2]) if p.facts else "I have an update for your business."
    default_cta = "Reply YES if you would like me to proceed."
    return f"Hi {owner}, {facts} {p.cta_instruction or default_cta}"


_TEMPLATE_RENDERERS = {
    "research_digest": _render_research_digest,
    "renewal_due": _render_renewal_due,
    "recall_due": _render_recall_due,
    "festival": _render_festival,
    "festival_upcoming": _render_festival,
    "review_request": _render_review_request,
    "review_theme_emerged": _render_review_request,
    "regulation_change": _render_regulation_change,
    "performance_drop": _render_performance_drop,
    "perf_dip": _render_performance_drop,
    "customer_followup": _render_customer_followup,
    "subscription_expiry": _render_subscription_expiry,
    "active_offer": _render_active_offer,
}


class PromptBuilder:
    """Build structured prompts from context layers."""

    def build(
        self,
        objective: str,
        trigger_kind: str,
        category: dict[str, Any],
        merchant: dict[str, Any],
        trigger: dict[str, Any],
        customer: Optional[dict[str, Any]] = None,
        send_as: str = "vera",
        cta: str = "open_ended",
    ) -> ComposedPrompt:
        voice = category.get("voice") or {}
        tone = voice.get("tone", "professional")
        slug = category.get("slug", "general")
        facts = self._extract_facts(category, merchant, trigger, customer)

        cta_map = {
            "open_ended": "Reply with your preference.",
            "binary_yes_no": "Reply YES or STOP.",
            "binary_confirm_cancel": "Reply CONFIRM to proceed.",
        }

        return ComposedPrompt(
            objective=objective,
            trigger_kind=trigger_kind,
            category_slug=slug,
            tone=tone,
            merchant=merchant,
            trigger=trigger,
            category=category,
            customer=customer,
            facts=facts,
            cta_instruction=cta_map.get(cta, "Reply YES to continue."),
            send_as=send_as,
            template_id=f"{slug}_{objective}_v1",
        )

    def _extract_facts(
        self,
        category: dict[str, Any],
        merchant: dict[str, Any],
        trigger: dict[str, Any],
        customer: Optional[dict[str, Any]],
    ) -> list[str]:
        facts: list[str] = []
        perf = merchant.get("performance") or {}
        if perf.get("views"):
            facts.append(f"{perf['views']} profile views (30d)")
        if perf.get("ctr"):
            facts.append(f"CTR {format_ctr(float(perf['ctr']))}")
        signals = merchant.get("signals") or []
        for sig in signals[:2]:
            facts.append(sig.replace("_", " "))
        if customer:
            rel = customer.get("relationship") or {}
            if rel.get("last_visit"):
                facts.append(f"last visit {rel['last_visit'][:10]}")
        payload = trigger.get("payload") or {}
        if payload.get("festival"):
            facts.append(f"{payload['festival']} approaching")
        return facts
