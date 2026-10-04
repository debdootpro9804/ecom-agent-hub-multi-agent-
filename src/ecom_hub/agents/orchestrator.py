# src/ecom_hub/agents/orchestrator.py

import time
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END

from ecom_hub.models.agent import IncomingEvent, AgentResponse, AgentType, EventType
from ecom_hub.models.customer import CustomerEmail
from ecom_hub.models.product import LowStockEventPayload
from ecom_hub.agents.support_agent import run_support_agent
from ecom_hub.agents.inventory_agent import run_inventory_agent


class OrchestratorState(TypedDict):
    """
    The shared state that flows through every node in the graph.
    Every node reads from this and can return partial updates to it.
    """
    event: IncomingEvent
    response: Optional[AgentResponse]


# ── Nodes ────────────────────────────────────────────────────────────────────
# Each node is just a function: (state) -> partial state update

def support_node(state: OrchestratorState) -> dict:
    """Runs when the router decides this is a Support Agent job."""
    event = state["event"]
    try:
        email = CustomerEmail(**event.payload)
        response = run_support_agent(email, event.event_id)
    except Exception as e:
        response = AgentResponse(
            event_id=event.event_id,
            handled_by=AgentType.SUPPORT,
            success=False,
            result={},
            error=f"Failed to parse email payload: {str(e)}",
        )
    return {"response": response}


def inventory_node(state: OrchestratorState) -> dict:
    """Runs when the router decides this is an Inventory Agent job."""
    event = state["event"]
    try:
        payload = LowStockEventPayload(**event.payload)
        response = run_inventory_agent(payload, event.event_id)
    except Exception as e:
        response = AgentResponse(
            event_id=event.event_id,
            handled_by=AgentType.INVENTORY,
            success=False,
            result={},
            error=f"Failed to parse stock alert payload: {str(e)}",
        )
    return {"response": response}


def fallback_node(state: OrchestratorState) -> dict:
    """
    Runs for event types we haven't built a real agent for yet
    (new_order, daily_report_request). Replaced one by one as we
    build Order and Analytics agents later.
    """
    event = state["event"]
    response = AgentResponse(
        event_id=event.event_id,
        handled_by=AgentType.ORCHESTRATOR,
        success=True,
        result={
            "message": f"[MOCK] No specialist agent built yet for {event.event_type.value}",
            "event_type": event.event_type.value,
        },
    )
    return {"response": response}


# ── Router ───────────────────────────────────────────────────────────────────
# This is a PURE function — no LLM call, no side effects. Just reads
# event_type and returns the name of the next node. Fast, free, 100% testable.

def route_event(state: OrchestratorState) -> str:
    event_type = state["event"].event_type
    routing = {
        EventType.CUSTOMER_EMAIL: "support",
        EventType.ORDER_STATUS_REQUEST: "support",
        EventType.LOW_STOCK_ALERT: "inventory",
    }
    return routing.get(event_type, "fallback")


# ── Build the graph ─────────────────────────────────────────────────────────

def build_orchestrator():
    graph = StateGraph(OrchestratorState)

    # Register nodes
    graph.add_node("support", support_node)
    graph.add_node("inventory", inventory_node)
    graph.add_node("fallback", fallback_node)

    # Conditional edge FROM the start — route_event decides which node runs first
    graph.add_conditional_edges(
        START,
        route_event,
        {
            "support": "support",
            "inventory": "inventory",
            "fallback": "fallback",
        },
    )

    # All three paths end the graph after running
    graph.add_edge("support", END)
    graph.add_edge("inventory", END)
    graph.add_edge("fallback", END)

    return graph.compile()


# Build once at module load, reuse for every request
_orchestrator = build_orchestrator()


def run_orchestrator(event: IncomingEvent) -> AgentResponse:
    """
    Main entry point. Takes any IncomingEvent, runs it through the graph,
    returns the AgentResponse — regardless of which agent actually handled it.
    """
    start = time.time() * 1000

    result = _orchestrator.invoke({"event": event, "response": None})
    response = result["response"]
    response.processing_time_ms = (time.time() * 1000) - start

    return response