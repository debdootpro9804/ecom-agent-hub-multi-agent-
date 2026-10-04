# tests/test_orchestrator.py

from unittest.mock import patch

with patch.dict("os.environ", {
    "AZURE_OPENAI_ENDPOINT": "https://dummy.openai.azure.com",
    "AZURE_OPENAI_API_KEY": "dummy-key",
    "AZURE_OPENAI_API_VERSION": "2024-02-15-preview",
    "AZURE_OPENAI_DEPLOYMENT_NAME": "dummy-deployment",
}):
    from ecom_hub.agents.orchestrator import route_event, OrchestratorState

from ecom_hub.models.agent import IncomingEvent, EventType


def _make_state(event_type: EventType, payload: dict | None = None) -> OrchestratorState:
    event = IncomingEvent(event_type=event_type, payload=payload or {})
    return {"event": event, "response": None}


def test_customer_email_routes_to_support():
    state = _make_state(EventType.CUSTOMER_EMAIL)
    assert route_event(state) == "support"


def test_order_status_request_routes_to_support():
    state = _make_state(EventType.ORDER_STATUS_REQUEST)
    assert route_event(state) == "support"


def test_low_stock_alert_routes_to_inventory():
    state = _make_state(EventType.LOW_STOCK_ALERT)
    assert route_event(state) == "inventory"


def test_new_order_routes_to_fallback():
    """new_order has no real agent yet — should fall back gracefully."""
    state = _make_state(EventType.NEW_ORDER)
    assert route_event(state) == "fallback"


def test_daily_report_routes_to_fallback():
    state = _make_state(EventType.DAILY_REPORT_REQUEST)
    assert route_event(state) == "fallback"