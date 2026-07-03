from datetime import datetime, timezone
from typing import Any, Optional


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def safe_get(data: Optional[dict[str, Any]], *keys: str, default: Any = None) -> Any:
    current: Any = data or {}
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key, default)
        if current is None:
            return default
    return current


def merchant_display_name(merchant: dict[str, Any]) -> str:
    identity = merchant.get("identity") or {}
    return identity.get("owner_first_name") or identity.get("name", "there")


def merchant_full_name(merchant: dict[str, Any]) -> str:
    identity = merchant.get("identity") or {}
    return identity.get("name", "your business")


def customer_display_name(customer: dict[str, Any]) -> str:
    identity = customer.get("identity") or {}
    return identity.get("name", "there")


def active_offers(merchant: dict[str, Any]) -> list[dict[str, Any]]:
    offers = merchant.get("offers") or []
    return [o for o in offers if o.get("status") == "active"]


def first_active_offer_title(merchant: dict[str, Any]) -> Optional[str]:
    active = active_offers(merchant)
    return active[0]["title"] if active else None


def normalize_trigger_kind(kind: str) -> str:
    aliases = {
        "perf_dip": "performance_drop",
        "festival_upcoming": "festival",
        "review_theme_emerged": "review_request",
        "wedding_package_followup": "customer_followup",
        "curious_ask_due": "customer_followup",
        "winback_eligible": "customer_followup",
    }
    return aliases.get(kind, kind)


def format_ctr(ctr: float) -> str:
    return f"{ctr * 100:.1f}%"
