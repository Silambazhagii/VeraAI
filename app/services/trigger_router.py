from typing import Any, Optional

from app.models.api_models import Decision
from app.models.enums import CtaType, DecisionPriority, SendAs
from app.utils.helpers import active_offers, normalize_trigger_kind, safe_get


class TriggerRouter:
    """Route trigger kinds to decision objectives — pure deterministic logic."""

    MERCHANT_KINDS = {
        "research_digest",
        "renewal_due",
        "festival",
        "festival_upcoming",
        "review_request",
        "review_theme_emerged",
        "regulation_change",
        "performance_drop",
        "perf_dip",
        "subscription_expiry",
        "active_offer",
    }

    CUSTOMER_KINDS = {
        "recall_due",
        "customer_followup",
        "wedding_package_followup",
        "curious_ask_due",
        "winback_eligible",
    }

    def normalize_kind(self, kind: str) -> str:
        return normalize_trigger_kind(kind)

    def objective_for_kind(self, kind: str) -> str:
        normalized = self.normalize_kind(kind)
        if normalized in {"festival_upcoming"}:
            return "festival"
        if normalized in {"perf_dip"}:
            return "performance_drop"
        if normalized in {"review_theme_emerged"}:
            return "review_request"
        return normalized

    def should_skip(
        self,
        kind: str,
        merchant: dict[str, Any],
        trigger: dict[str, Any],
        customer: Optional[dict[str, Any]],
    ) -> tuple[bool, str]:
        normalized = self.normalize_kind(kind)
        signals = merchant.get("signals") or []
        sub = merchant.get("subscription") or {}

        if normalized == "renewal_due":
            days = sub.get("days_remaining", 999)
            if days > 30:
                return True, f"Renewal not urgent ({days} days remaining)"

        if normalized == "subscription_expiry":
            days = sub.get("days_remaining", 999)
            if days > 14:
                return True, "Subscription not near expiry"

        if normalized == "active_offer":
            if not active_offers(merchant):
                return True, "No active offers to promote"

        if normalized == "performance_drop":
            perf = merchant.get("performance") or {}
            delta = safe_get(trigger, "payload", "delta_pct", default=0)
            if float(delta) > -0.15 and "perf_dip" not in " ".join(signals):
                return True, "Performance dip not significant"

        if normalized == "recall_due":
            if customer:
                consent = customer.get("consent") or {}
                scope = consent.get("scope") or []
                if scope and "recall_reminders" not in scope:
                    return True, "Customer has not consented to recall reminders"
            else:
                return True, "Missing customer context for recall"

        if normalized == "festival":
            days = safe_get(trigger, "payload", "days_until", default=999)
            if days and int(days) > 60:
                return True, "Festival too far out"

        return False, ""

    def compute_priority(self, trigger: dict[str, Any], merchant: dict[str, Any]) -> str:
        urgency = int(trigger.get("urgency", 1))
        score = urgency * 2
        signals = merchant.get("signals") or []
        sub = merchant.get("subscription") or {}

        if sub.get("days_remaining", 999) <= 14:
            score += 4
        if any("ctr_below" in s for s in signals):
            score += 3
        if any("stale_posts" in s for s in signals):
            score += 2
        if any("perf_dip" in s for s in signals):
            score += 3
        if any("no_active_offers" in s for s in signals):
            score += 2

        if score >= 10:
            return DecisionPriority.CRITICAL.value
        if score >= 7:
            return DecisionPriority.HIGH.value
        if score >= 4:
            return DecisionPriority.MEDIUM.value
        return DecisionPriority.LOW.value

    def decide(
        self,
        category: dict[str, Any],
        merchant: dict[str, Any],
        trigger: dict[str, Any],
        customer: Optional[dict[str, Any]] = None,
    ) -> Decision:
        kind = trigger.get("kind", "")
        normalized = self.normalize_kind(kind)
        scope = trigger.get("scope", "merchant")

        skip, skip_reason = self.should_skip(kind, merchant, trigger, customer)
        if skip:
            return Decision(
                should_send=False,
                priority=DecisionPriority.LOW.value,
                reason=skip_reason,
                action_type="skip",
            )

        priority = self.compute_priority(trigger, merchant)
        objective = self.objective_for_kind(kind)

        if scope == "customer" or normalized in self.CUSTOMER_KINDS:
            send_as = SendAs.MERCHANT_ON_BEHALF
            recipient = "customer"
            cta = CtaType.MULTI_CHOICE_SLOT if normalized == "recall_due" else CtaType.OPEN_ENDED
        else:
            send_as = SendAs.VERA
            recipient = "merchant"
            cta = CtaType.BINARY_YES_NO if normalized in {"renewal_due", "subscription_expiry"} else CtaType.OPEN_ENDED

        if normalized in {"renewal_due", "subscription_expiry", "performance_drop", "perf_dip"}:
            cta = CtaType.BINARY_YES_NO

        template = f"vera_{objective}_v1"
        if send_as == SendAs.MERCHANT_ON_BEHALF:
            template = f"merchant_{objective}_v1"

        return Decision(
            should_send=True,
            priority=priority,
            reason=f"Trigger {kind} is actionable for {recipient}",
            action_type="send",
            send_as=send_as,
            recipient=recipient,
            template_name=template,
            cta=cta,
            objective=objective,
        )
