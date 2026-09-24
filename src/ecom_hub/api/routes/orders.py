from fastapi import APIRouter,Depends,HTTPException
from ...models.order import Order,OrderStatusUpdate
from ...api.dependencies import verify_api_key

router=APIRouter(
    prefix="/orders",
    tags=["orders"],
    dependencies=[Depends(verify_api_key)]
)

_orders_store: dict[str, Order] = {}

@router.post("/",status_code=201)
async def create_order(order:Order)-> dict:
    """
    Accepts a new order & stores it.
    """

    _orders_store[order.order_id] = order

    return {
        "message": "Order received successfully",
        "order_id": order.order_id,
        "status": order.status,
        "total_amount": order.total_amount
    }

@router.get("/{order_id}")
async def get_order(order_id: str) -> dict:
    """
    Fetches a single order by its order ID
    """
    order=_orders_store.get(order_id)

    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")

    return order.model_dump()

@router.get("/")
async def list_orders() -> dict:
    """
    Fetches all orders present currently in system.
    """
    return{
        "total_orders": len(_orders_store),
        "orders":[i.model_dump() for i in _orders_store.values()]
    }

@router.patch("/status")
async def update_order_status(update: OrderStatusUpdate) -> dict:
    """Update the status of an existing order."""

    order=_orders_store.get(update.order_id)
    if not order:
        raise HTTPException(status_code=404,detail=f"Order {update.order_id} not found")

    updated_order=order.model_copy(update={"status":update.new_status})
    _orders_store[update.order_id]=updated_order

    return {
        "message": "Order status updated successfully",
        "order_id": update.order_id,
        "status": update.new_status,
        "reason": update.reason
    }