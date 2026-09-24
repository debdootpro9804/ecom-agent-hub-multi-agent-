import time
from fastapi import APIRouter,Depends
from ...models.agent import IncomingEvent,AgentResponse,AgentType,EventType
from ...api.dependencies import verify_api_key

router = APIRouter(
    prefix="/events",
    tags=["events"],
    dependencies=[Depends(verify_api_key)]
)

def _mock_handle_event(event: IncomingEvent) -> AgentResponse:
    routing_map = {
        EventType.CUSTOMER_EMAIL: AgentType.SUPPORT,
        EventType.NEW_ORDER: AgentType.ORDER,
        EventType.ORDER_STATUS_REQUEST: AgentType.SUPPORT,
        EventType.LOW_STOCK_ALERT: AgentType.INVENTORY,
        EventType.DAILY_REPORT_REQUEST: AgentType.ANALYTICS,
    }

    agent=routing_map.get(event.event_type,AgentType.ORCHESTRATOR)

    return AgentResponse(
        event_id=event.event_id,
        handled_by=agent,
        success=True,
        result={
            "message":f"Event of type {event.event_type} handled by {agent.value} agent",
            "event_type": event.event_type.value,
            "payload_received": event.payload
        }
    )

@router.post("/",response_model=AgentResponse)
async def receive_agent(event:IncomingEvent) -> AgentResponse:
    start=time.time()*1000
    response=_mock_handle_event(event)
    end=time.time()*1000
    print(f"Event processing time: {end-start} ms")
    return response

@router.get("/types")
async def list_event_types() ->dict:
    """Returns all valid event types which the system accepts"""

    return{
        "event_types": [event_type.value for event_type in EventType],
        "description": "List of all valid event types which the system accepts"
    }




