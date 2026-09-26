# tests/test_routes.py

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

# We mock config so tests don't need real Azure credentials
with patch.dict("os.environ", {
    "AZURE_OPENAI_ENDPOINT": "https://dummy.openai.azure.com",
    "AZURE_OPENAI_API_KEY": "dummy-key",
    "AZURE_OPENAI_API_VERSION": "2024-02-15-preview",
    "AZURE_OPENAI_DEPLOYMENT_NAME": "dummy-deployment",
}):
    from ecom_hub.main import app

client = TestClient(app)
HEADERS = {"X-Api-Key": "dev-key"}


# ── Health ──────────────────────────────────────────────────────────────────

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "E-com Agent Hub is running 🚀"


def test_health_check():
    response = client.get("/health/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_readiness_check():
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


# ── Orders ──────────────────────────────────────────────────────────────────

def test_create_order():
    payload = {
        "customer_id": "cust_001",
        "customer_email": "test@example.com",
        "items": [
            {
                "product_id": "prod_1",
                "product_name": "Wireless Headphones",
                "quantity": 2,
                "unit_price": 49.99,
            }
        ],
    }
    response = client.post("/orders/", json=payload, headers=HEADERS)
    assert response.status_code == 201
    data = response.json()
    assert data["total_amount"] == 99.98
    assert data["status"] == "pending"


def test_create_order_no_api_key():
    """Requests without API key should be rejected."""
    payload = {
        "customer_id": "cust_001",
        "customer_email": "test@example.com",
        "items": [
            {
                "product_id": "prod_1",
                "product_name": "Headphones",
                "quantity": 1,
                "unit_price": 49.99,
            }
        ],
    }
    response = client.post("/orders/", json=payload)
    assert response.status_code == 401


def test_get_order_not_found():
    response = client.get("/orders/nonexistent-id", headers=HEADERS)
    assert response.status_code == 404


# ── Events ──────────────────────────────────────────────────────────────────

def test_receive_customer_email_event():
    payload = {
        "event_type": "customer_email",
        "payload": {
            "customer_email": "test@example.com",
            "subject": "Where is my order?",
            "body": "I ordered 2 days ago, no update yet.",
        },
    }
    response = client.post("/events/", json=payload, headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["handled_by"] == "support"


def test_receive_low_stock_event():
    payload = {
        "event_type": "low_stock_alert",
        "payload": {
            "product_id": "prod_1",
            "product_name": "Headphones",
            "current_stock": 3,
        },
    }
    response = client.post("/events/", json=payload, headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["handled_by"] == "inventory"


def test_list_event_types():
    response = client.get("/events/types", headers=HEADERS)
    assert response.status_code == 200
    assert "event_types" in response.json()