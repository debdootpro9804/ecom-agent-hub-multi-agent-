from pydantic import BaseModel, Field

class Product(BaseModel):
    """A single product in the catalog."""

    product_id: str
    name: str
    description: str=""
    price: float = Field(gt=0) # Must be greater than 0
    stock_quantity: int = Field(ge=0) # Must be greater than or equal to 0
    reorder_threshold: int = Field(ge=5) # for alert when stock drops to 5
    category: str="general"

    @property
    def is_low_stock(self) -> bool:
        return self.stock_quantity <= self.reorder_threshold

    @property
    def is_out_of_stock(self) -> bool:
        return self.stock_quantity == 0

class StockAlert(BaseModel):
    """raises an alert when stock is low."""

    product_id: str
    product_name: str
    current_stock: int
    reorder_threshold: int
    suggested_reorder_quantity: int