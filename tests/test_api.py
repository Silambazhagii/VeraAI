import pytest
from fastapi.testclient import TestClient

from main import app
from app.models.enums import ContextScope, Intent
from app.services.auto_reply_detector import auto_reply_detector
from app.services.context_store import get_context_store
from app.services.conversation_manager import get_conversation_manager
from app.services.intent_classifier import intent_classifier

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_state():
    get_context_store().clear()
    get_conversation_manager().clear()
    yield


SAMPLE_CATEGORY = {
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

SAMPLE_MERCHANT = {
    "merchant_id": "m_001_drmeera_dentist_delhi",
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

SAMPLE_TRIGGER = {
    "id": "trg_001_research_digest_dentists",
    "scope": "merchant",
    "kind": "research_digest",
    "source": "external",
    "merchant_id": "m_001_drmeera_dentist_delhi",
    "customer_id": None,
    "payload": {"category": "dentists", "top_item_id": "d_2026W17_jida_fluoride"},
    "urgency": 2,
    "suppression_key": "research:dentists:2026-W17",
    "expires_at": "2026-05-03T00:00:00Z",
}


def _push(scope: str, context_id: str, version: int, payload: dict):
    return client.post(
        "/v1/context",
        json={
            "scope": scope,
            "context_id": context_id,
            "version": version,
            "payload": payload,
            "delivered_at": "2026-04-26T10:00:00Z",
        },
    )


def test_healthz():
    r = client.get("/v1/healthz")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "uptime_seconds" in data
    assert data["contexts_loaded"]["category"] == 0


def test_metadata():
    r = client.get("/v1/metadata")
    assert r.status_code == 200
    data = r.json()
    assert data["team_name"] == "Magicpin Challenge"
    assert data["version"] == "1.0"
    assert "contact_email" in data


def test_context_insert_and_idempotent():
    r = _push("category", "dentists", 1, SAMPLE_CATEGORY)
    assert r.status_code == 200
    assert r.json()["accepted"] is True

    r2 = _push("category", "dentists", 1, SAMPLE_CATEGORY)
    assert r2.status_code == 200
    assert r2.json()["accepted"] is True

    health = client.get("/v1/healthz").json()
    assert health["contexts_loaded"]["category"] == 1


def test_context_version_replace():
    _push("merchant", "m_001_drmeera_dentist_delhi", 1, SAMPLE_MERCHANT)
    updated = {**SAMPLE_MERCHANT, "performance": {"views": 3000, "calls": 25, "ctr": 0.025}}
    r = _push("merchant", "m_001_drmeera_dentist_delhi", 2, updated)
    assert r.status_code == 200
    assert r.json()["accepted"] is True


def test_context_stale_version_409():
    _push("merchant", "m_001_drmeera_dentist_delhi", 2, SAMPLE_MERCHANT)
    r = _push("merchant", "m_001_drmeera_dentist_delhi", 1, SAMPLE_MERCHANT)
    assert r.status_code == 409
    assert r.json()["accepted"] is False
    assert r.json()["reason"] == "stale_version"
    assert r.json()["current_version"] == 2


def test_context_invalid_scope_400():
    r = client.post(
        "/v1/context",
        json={
            "scope": "invalid",
            "context_id": "x",
            "version": 1,
            "payload": {},
            "delivered_at": "2026-04-26T10:00:00Z",
        },
    )
    assert r.status_code == 422


def test_tick_returns_action():
    _push("category", "dentists", 1, SAMPLE_CATEGORY)
    _push("merchant", "m_001_drmeera_dentist_delhi", 1, SAMPLE_MERCHANT)
    _push("trigger", "trg_001_research_digest_dentists", 1, SAMPLE_TRIGGER)

    r = client.post(
        "/v1/tick",
        json={
            "now": "2026-04-26T10:35:00Z",
            "available_triggers": ["trg_001_research_digest_dentists"],
        },
    )
    assert r.status_code == 200
    actions = r.json()["actions"]
    assert len(actions) == 1
    action = actions[0]
    assert action["merchant_id"] == "m_001_drmeera_dentist_delhi"
    assert action["trigger_id"] == "trg_001_research_digest_dentists"
    assert "Meera" in action["body"]
    assert action["conversation_id"]
    assert action["cta"]
    assert action["rationale"]


def test_tick_empty_when_no_triggers():
    r = client.post("/v1/tick", json={"now": "2026-04-26T10:35:00Z", "available_triggers": []})
    assert r.status_code == 200
    assert r.json()["actions"] == []


def test_reply_yes_after_tick():
    _push("category", "dentists", 1, SAMPLE_CATEGORY)
    _push("merchant", "m_001_drmeera_dentist_delhi", 1, SAMPLE_MERCHANT)
    _push("trigger", "trg_001_research_digest_dentists", 1, SAMPLE_TRIGGER)

    tick = client.post(
        "/v1/tick",
        json={
            "now": "2026-04-26T10:35:00Z",
            "available_triggers": ["trg_001_research_digest_dentists"],
        },
    ).json()
    conv_id = tick["actions"][0]["conversation_id"]

    r = client.post(
        "/v1/reply",
        json={
            "conversation_id": conv_id,
            "merchant_id": "m_001_drmeera_dentist_delhi",
            "customer_id": None,
            "from_role": "merchant",
            "message": "Yes please send the abstract",
            "received_at": "2026-04-26T10:42:00Z",
            "turn_number": 2,
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["action"] == "send"
    assert data["body"]
    assert "abstract" in data["body"].lower() or "draft" in data["body"].lower()


def test_reply_auto_reply_detection():
    store = get_context_store()
    conv_mgr = get_conversation_manager()
    from app.models.enums import SendAs

    conv_mgr.create(
        conversation_id="conv_auto_test",
        merchant_id="m_001",
        trigger_id="trg_1",
        send_as=SendAs.VERA,
        trigger_kind="research_digest",
        suppression_key="test",
    )

    r = client.post(
        "/v1/reply",
        json={
            "conversation_id": "conv_auto_test",
            "merchant_id": "m_001",
            "from_role": "merchant",
            "message": "Thank you for contacting Dr. Meera's Dental Clinic! Our team will respond shortly.",
            "received_at": "2026-04-26T10:42:00Z",
            "turn_number": 2,
        },
    )
    assert r.status_code == 200
    assert r.json()["action"] in ("send", "wait", "end")


def test_reply_stop_ends_conversation():
    from app.models.enums import SendAs

    get_conversation_manager().create(
        conversation_id="conv_stop",
        merchant_id="m_001",
        trigger_id="trg_1",
        send_as=SendAs.VERA,
        trigger_kind="research_digest",
        suppression_key="test",
    )

    r = client.post(
        "/v1/reply",
        json={
            "conversation_id": "conv_stop",
            "merchant_id": "m_001",
            "from_role": "merchant",
            "message": "Stop messaging me",
            "received_at": "2026-04-26T10:42:00Z",
            "turn_number": 2,
        },
    )
    assert r.json()["action"] == "end"


def test_intent_classifier():
    assert intent_classifier.classify("Yes please") == Intent.YES
    assert intent_classifier.classify("Not interested, stop") == Intent.STOP
    assert intent_classifier.classify("What is the price?") == Intent.PRICE
    assert intent_classifier.classify("Call me tomorrow") == Intent.CALL_ME


def test_auto_reply_detector():
    assert auto_reply_detector.is_auto_reply(
        "Thank you for contacting us! Our team will respond shortly."
    )
    assert not auto_reply_detector.is_auto_reply("Yes, send me the details")


def test_context_store_versioning():
    store = get_context_store()
    store.save(ContextScope.CATEGORY, "dentists", 1, {"slug": "dentists"})
    result = store.save(ContextScope.CATEGORY, "dentists", 1, {"slug": "dentists"})
    from app.services.context_store import StoreResult

    assert result.result == StoreResult.IGNORED
    rejected = store.save(ContextScope.CATEGORY, "dentists", 0, {"slug": "old"})
    assert rejected.result == StoreResult.REJECTED
