from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class EventType(str,Enum):

    """Every type of event the system can receive.
    The orchastrator reads this and decides which agent to call"""

    CUSTOMER_EMAIL = "customer_email"
    NEW_ORDER = "new_order"
    ORDER_STATUS_REQUEST = "order_status_request"
    LOW_STOCK_ALERT = "low_stock_alert"
    DAILY_REPORT_REQUEST="daily_report_request"

class AgentType(str,Enum):
    """Specialist agents available in the system."""

    ORCHESTRATOR = "orchestrator"
    SUPPORT = "support"
    ORDER = "order"
    INVENTORY = "inventory"
    ANALYTICS = "analytics"

class IncomingEvent(BaseModel):
    """
    Every request to our system comes in as an IncomingEvent.
    This is the single entry point — one shape for all inputs.
    The Orchestrator reads event_type and routes accordingly."""
         
    event_id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex)
    event_type: EventType
    payload: dict      # flexible — holds different data per event type
    received_at: datetime = Field(default_factory=datetime.utcnow)

class AgentResponse(BaseModel):
    """
    Every agent returns this same shape response for easy to log, trace , test"""
    event_id:str
    handled_by: AgentType
    success: bool
    result: dict
    error: str=""
    processing_time_ms: float = 0.0