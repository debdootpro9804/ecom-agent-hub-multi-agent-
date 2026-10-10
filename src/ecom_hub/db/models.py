from datetime import date,datetime
from decimal import Decimal

from sqlalchemy import Date,DateTime,ForeignKey,Integer,Numeric,String,Text,func
from sqlalchemy.orm import relationship,Mapped,mapped_column

from ecom_hub.db.base import Base

class ProductRow(Base):
    __tablename__="products"

    product_id: Mapped[str]=mapped_column(String(50),primary_key=True)
    name: Mapped[str]=mapped_column(String(200))
    description: Mapped[str]=mapped_column(Text,default=" ")
    category: Mapped[str]=mapped_column(String(100),default="general")
    price: Mapped[Decimal]=mapped_column(Numeric(10,2))
    unit_cost: Mapped[Decimal]=mapped_column(Numeric(10,2))
    stock_quantity: Mapped[int]=mapped_column(Integer)
    reorder_threshold: Mapped[int]=mapped_column(Integer)
    supplier: Mapped[str]=mapped_column(String(100))
    lead_time_days: Mapped[int]=mapped_column(Integer,default=7)

class OrderRow(Base):
    __tablename__ = "orders"

    order_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    customer_id: Mapped[str] = mapped_column(String(50), index=True)
    customer_name: Mapped[str] = mapped_column(String(200), default="")
    customer_email: Mapped[str] = mapped_column(String(320), index=True)
    status: Mapped[str] = mapped_column(String(30), default="pending", index=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    tracking_number: Mapped[str | None] = mapped_column(String(100))
    estimated_delivery: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # lazy="selectin" loads items together with the order, in one extra query.
    # This matters in async code: the default lazy loading tries to hit the DB
    # at attribute access time and crashes with "MissingGreenlet".
    items: Mapped[list["OrderItemRow"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

class OrderItemRow(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[str] = mapped_column(
        ForeignKey("orders.order_id", ondelete="CASCADE"), index=True
    )
    # Deliberately NOT a foreign key to products: an order item is a snapshot
    # of what the customer bought at that price, even if the product changes later.
    product_id: Mapped[str] = mapped_column(String(50))
    product_name: Mapped[str] = mapped_column(String(200))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    order: Mapped["OrderRow"] = relationship(back_populates="items")


class PurchaseOrderRow(Base):
    __tablename__ = "purchase_orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.product_id"), index=True)
    quantity: Mapped[int] = mapped_column(Integer)
    supplier: Mapped[str] = mapped_column(String(200))
    estimated_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String(30), default="submitted")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    @property
    def po_id(self) -> str:
        return f"PO-{self.id:04d}"        

