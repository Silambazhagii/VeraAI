"""Scoring optimization helpers — ensure messages meet judge rubric criteria."""

from typing import Any

from app.utils.helpers import merchant_display_name, merchant_full_name


def ensure_merchant_anchor(body: str, merchant: dict[str, Any]) -> str:
    """Ensure merchant name appears in the message."""
    owner = merchant_display_name(merchant)
    business = merchant_full_name(merchant)
    if owner.lower() in body.lower() or business.lower() in body.lower():
        return body
    return f"Hi {owner}, {body}"


def has_specificity_anchor(body: str) -> bool:
    """Check if message contains verifiable specificity (numbers, prices, dates)."""
    import re

    patterns = [
        r"\d+%",
        r"₹\s?\d+",
        r"\d{3,}",
        r"\d+-month",
        r"\d+ days",
        r"p\.\d+",
        r"JIDA|DCI|CTR",
    ]
    return any(re.search(p, body, re.IGNORECASE) for p in patterns)


def score_message_quality(body: str, merchant: dict[str, Any], trigger_kind: str) -> int:
    """Heuristic quality score 0-10 for internal validation."""
    score = 5
    if has_specificity_anchor(body):
        score += 2
    owner = merchant_display_name(merchant)
    if owner.lower() in body.lower():
        score += 1
    if trigger_kind.replace("_", " ") in body.lower() or _trigger_keyword_in_body(body, trigger_kind):
        score += 1
    if len(body) < 500:
        score += 1
    return min(10, score)


def _trigger_keyword_in_body(body: str, kind: str) -> bool:
    keywords = {
        "research_digest": ["jida", "research", "trial", "recall"],
        "renewal_due": ["renew", "expir", "plan"],
        "recall_due": ["recall", "visit", "slot"],
        "festival": ["festival", "diwali", "post"],
        "performance_drop": ["dropped", "ctr", "calls"],
        "regulation_change": ["compliance", "dci", "regulation"],
        "review_request": ["review", "rating"],
        "active_offer": ["offer", "₹"],
    }
    normalized = kind.replace("perf_dip", "performance_drop")
    for kw in keywords.get(normalized, []):
        if kw in body.lower():
            return True
    return False
