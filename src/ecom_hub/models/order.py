from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class OrderStatus(str,Enum):
    """
    Every possible state an order can be in.
    Using str + Enum means the value is a plain string in JSON
    e.g. "pending" not "OrderStatus.pending"
    """
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class OrderItem(BaseModel):
    """A single item within an order."""
    product_id: str
    product_name:str
    quantity: int = Field(gt=0) # Must be greater than 0
    unit_price: float = Field(gt=0) # Must be greater than 0

    @property
    def subtotal(self) -> float:
        return self.quantity * self.unit_price


class Order(BaseModel):
    """The complete customer order."""

    order_id: str = Field(default_factory=lambda: str(uuid4()))
    customer_id: str
    customer_email: str
    items: list[OrderItem]
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    notes: str = ""

    @property
    def total_amount(self) -> float:
        return sum(item.subtotal for item in self.items)

class OrderStatusUpdate(BaseModel):
    """Model for updating the status of an order."""

    order_id: str
    new_status: OrderStatus
    reason: str = ""

