from datetime import datetime
from pydantic import BaseModel, EmailStr,Field

class Customer(BaseModel):
    """A customer in the system."""

    customer_id: str
    name: str
    email:EmailStr
    phone: str
    total_orders: int =0
    total_spent: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CustomerEmail(BaseModel):
    """An inbound email from a customer."""

    customer_id: str
    customer_email: EmailStr
    customer_name: str
    subject: str
    body: str
    received_at: datetime = Field(default_factory=datetime.utcnow)

class EmailReply(BaseModel):
    """A reply our system sends to a customer."""

    to_email: EmailStr
    subject: str
    body: str
    generated_by_agent: str #which agent wrote our mail
    #sent_at: datetime = Field(default_factory=datetime.utcnow)
    