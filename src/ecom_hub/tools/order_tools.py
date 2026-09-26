# src/ecom_hub/tools/order_tools.py

from langchain_core.tools import tool

# ── Fake database ────────────────────────────────────────────────────────────
# We replace this with real PostgreSQL in Step 6.
# For now it's a dict so we can focus on the agent logic.

FAKE_ORDERS = {
    "ORD-001": {
        "order_id": "ORD-001",
        "customer_name": "Debdoot",
        "customer_email": "debdoot@example.com",
        "items": [{"name": "Wireless Headphones", "quantity": 1, "price": 99.99}],
        "status": "shipped",
        "created_at": "2024-01-10",
        "estimated_delivery": "2024-01-15",
        "tracking_number": "TRK-789456",
    },
    "ORD-002": {
        "order_id": "ORD-002",
        "customer_name": "Debdoot",
        "customer_email": "debdoot@example.com",
        "items": [{"name": "Mechanical Keyboard", "quantity": 1, "price": 149.99}],
        "status": "processing",
        "created_at": "2024-01-12",
        "estimated_delivery": "2024-01-18",
        "tracking_number": None,
    },
    "ORD-003": {
        "order_id": "ORD-003",
        "customer_name": "Priya",
        "customer_email": "priya@example.com",
        "items": [{"name": "USB Hub", "quantity": 2, "price": 29.99}],
        "status": "delivered",
        "created_at": "2024-01-05",
        "estimated_delivery": "2024-01-10",
        "tracking_number": "TRK-123789",
    },
}

FAKE_POLICIES = {
    "return": "Items can be returned within 15 days of delivery in original condition.",
    "refund": "Refunds are processed within 5-7 business days after return is received.",
    "shipping": "Standard shipping takes 3-5 business days. Express shipping takes 1-2 days.",
    "cancellation": "Orders can be cancelled within 1 hour of placement.",
}


# ── Tools ────────────────────────────────────────────────────────────────────
# The @tool decorator does two things:
# 1. Wraps the function so LangChain can call it
# 2. Uses the docstring as the tool description — the LLM reads this
#    to decide WHEN to use the tool. Write clear docstrings.

@tool
def look_up_order(order_id: str) -> dict:
    """
    Look up a customer order by order ID.
    Use this when the customer mentions an order ID or asks about order status.
    Returns order details including status, items, and tracking info.
    """
    order = FAKE_ORDERS.get(order_id.upper())
    if not order:
        return {
            "found": False,
            "message": f"No order found with ID {order_id}"
        }
    return {"found": True, **order}


@tool
def get_policy(policy_type: str) -> str:
    """
    Get store policy information.
    Use this when customer asks about returns, refunds, shipping, or cancellations.
    policy_type must be one of: return, refund, shipping, cancellation
    """
    policy = FAKE_POLICIES.get(policy_type.lower())
    if not policy:
        available = ", ".join(FAKE_POLICIES.keys())
        return f"Policy not found. Available policies: {available}"
    return policy


@tool
def list_customer_orders(customer_email: str) -> dict:
    """
    List all orders for a customer by their email address.
    Use this when a customer asks 'what are my orders' or
    mentions they have multiple orders.
    """
    customer_orders = [
        order for order in FAKE_ORDERS.values()
        if order["customer_email"].lower() == customer_email.lower()
    ]
    if not customer_orders:
        return {
            "found": False,
            "message": f"No orders found for {customer_email}"
        }
    return {
        "found": True,
        "total_orders": len(customer_orders),
        "orders": customer_orders
    }