# src/ecom_hub/api/routes/events.py

import time
from fastapi import APIRouter, Depends
from ecom_hub.models.agent import IncomingEvent, AgentResponse, AgentType, EventType
from ecom_hub.models.customer import CustomerEmail
from ecom_hub.api.dependencies import verify_api_key
from ecom_hub.agents.support_agent import run_support_agent

router = APIRouter(
    prefix="/events",
    tags=["Events"],
    dependencies=[Depends(verify_api_key)],
)


def _mock_handle_event(event: IncomingEvent) -> AgentResponse:
    """
    Still used for event types we haven't built agents for yet.
    We'll replace each mock one by one as we build the real agents.
    """
    routing_map = {
        EventType.NEW_ORDER: AgentType.ORDER,
        EventType.ORDER_STATUS_REQUEST: AgentType.SUPPORT,
        EventType.LOW_STOCK_ALERT: AgentType.INVENTORY,
        EventType.DAILY_REPORT_REQUEST: AgentType.ANALYTICS,
    }
    agent = routing_map.get(event.event_type, AgentType.ORCHESTRATOR)
    return AgentResponse(
        event_id=event.event_id,
        handled_by=agent,
        success=True,
        result={
            "message": f"[MOCK] Event would be routed to {agent.value} agent",
            "event_type": event.event_type.value,
            "payload_received": event.payload,
        }
    )


@router.post("/", response_model=AgentResponse)
async def receive_event(event: IncomingEvent) -> AgentResponse:
    """
    Main entry point for all system events.
    customer_email → real Support Agent
    everything else → mock for now (replaced in Step 5)
    """
    start = time.time() * 1000

    # ── Real agent for customer emails ───────────────────────────────────────
    if event.event_type == EventType.CUSTOMER_EMAIL:
        try:
            email = CustomerEmail(**event.payload)
            return run_support_agent(email, event.event_id)
        except Exception as e:
            return AgentResponse(
                event_id=event.event_id,
                handled_by=AgentType.SUPPORT,
                success=False,
                result={},
                error=f"Failed to parse email payload: {str(e)}",
                processing_time_ms=(time.time() * 1000) - start,
            )

    # ── Mock for everything else ─────────────────────────────────────────────
    response = _mock_handle_event(event)
    response.processing_time_ms = (time.time() * 1000) - start
    return response


@router.get("/types")
async def list_event_types() -> dict:
    """Returns all valid event types the system accepts."""
    return {
        "event_types": [e.value for e in EventType],
        "description": "Use any of these as event_type when posting to /events/"
    }