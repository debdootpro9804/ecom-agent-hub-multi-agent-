# src/ecom_hub/api/routes/events.py

from fastapi import APIRouter, Depends
from ecom_hub.models.agent import IncomingEvent, AgentResponse, EventType
from ecom_hub.api.dependencies import verify_api_key
from ecom_hub.agents.orchestrator import run_orchestrator

router = APIRouter(
    prefix="/events",
    tags=["Events"],
    dependencies=[Depends(verify_api_key)],
)


@router.post("/", response_model=AgentResponse)
async def receive_event(event: IncomingEvent) -> AgentResponse:
    """
    Main entry point for all system events.
    The Orchestrator (LangGraph) handles ALL routing logic internally.
    This route doesn't know or care which agent ends up handling it.
    """
    return run_orchestrator(event)


@router.get("/types")
async def list_event_types() -> dict:
    """Returns all valid event types the system accepts."""
    return {
        "event_types": [e.value for e in EventType],
        "description": "Use any of these as event_type when posting to /events/"
    }