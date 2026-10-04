# src/ecom_hub/tools/inventory_tools.py

from langchain_core.tools import tool

# Fake inventory DB — replaced with real PostgreSQL in Step 6
FAKE_INVENTORY = {
    "prod_1": {
        "product_id": "prod_1",
        "name": "Wireless Headphones",
        "stock": 3,
        "reorder_threshold": 10,
        "supplier": "AudioTech Supplies",
        "lead_time_days": 5,
        "unit_cost": 45.00,
    },
    "prod_2": {
        "product_id": "prod_2",
        "name": "Mechanical Keyboard",
        "stock": 25,
        "reorder_threshold": 15,
        "supplier": "KeyMakers Inc",
        "lead_time_days": 7,
        "unit_cost": 65.00,
    },
}

# In-memory purchase order log — replaced with real DB in Step 6
_PURCHASE_ORDERS: list[dict] = []


@tool
def check_stock_level(product_id: str) -> dict:
    """
    Check the current stock level and reorder threshold for a product.
    Always call this first to get accurate, up-to-date numbers.
    """
    product = FAKE_INVENTORY.get(product_id)
    if not product:
        return {"found": False, "message": f"No product found with ID {product_id}"}
    return {
        "found": True,
        **product,
        "is_low_stock": product["stock"] <= product["reorder_threshold"],
    }


@tool
def calculate_reorder_quantity(product_id: str, target_stock: int = 50) -> dict:
    """
    Calculate how many units to reorder to reach a healthy target stock level.
    Call this after confirming stock is actually low.
    target_stock defaults to 50 units if not specified by the user.
    """
    product = FAKE_INVENTORY.get(product_id)
    if not product:
        return {"found": False, "message": f"No product found with ID {product_id}"}

    current_stock = product["stock"]
    reorder_qty = max(target_stock - current_stock, 0)
    estimated_cost = reorder_qty * product["unit_cost"]

    return {
        "found": True,
        "product_id": product_id,
        "current_stock": current_stock,
        "target_stock": target_stock,
        "suggested_reorder_quantity": reorder_qty,
        "estimated_cost": round(estimated_cost, 2),
        "supplier": product["supplier"],
        "lead_time_days": product["lead_time_days"],
    }


@tool
def create_purchase_order(product_id: str, quantity: int) -> dict:
    """
    Create a purchase order with the supplier to restock a product.
    Only call this after calculating the reorder quantity and confirming it's sensible.
    """
    product = FAKE_INVENTORY.get(product_id)
    if not product:
        return {"found": False, "message": f"No product found with ID {product_id}"}

    po_id = f"PO-{len(_PURCHASE_ORDERS) + 1:04d}"
    order = {
        "po_id": po_id,
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": quantity,
        "supplier": product["supplier"],
        "estimated_cost": round(quantity * product["unit_cost"], 2),
        "status": "submitted",
    }
    _PURCHASE_ORDERS.append(order)
    return order