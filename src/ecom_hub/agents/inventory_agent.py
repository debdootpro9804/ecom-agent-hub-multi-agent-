# src/ecom_hub/agents/inventory_agent.py

import time
from langchain.agents import create_agent
from langchain_openai import AzureChatOpenAI
from ecom_hub.prompts import INVENTORY_SYSTEM_PROMPT
from ecom_hub.config import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_DEPLOYMENT_NAME,
)
from ecom_hub.models.agent import AgentResponse, AgentType
from ecom_hub.models.product import LowStockEventPayload
from ecom_hub.tools.inventory_tools import (
    check_stock_level,
    calculate_reorder_quantity,
    create_purchase_order,
)




def build_inventory_agent():
    model = AzureChatOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_deployment=AZURE_OPENAI_DEPLOYMENT_NAME,
        temperature=0.2,     # lower temp — this is an operational decision, not creative writing
        max_tokens=600,
    )

    tools = [check_stock_level, calculate_reorder_quantity, create_purchase_order]

    return create_agent(
        model=model,
        tools=tools,
        system_prompt=INVENTORY_SYSTEM_PROMPT,
    )


_inventory_agent = build_inventory_agent()


def run_inventory_agent(payload: LowStockEventPayload, event_id: str) -> AgentResponse:
    start = time.time() * 1000

    user_message = f"""
A low stock alert was triggered:

Product ID: {payload.product_id}
Product Name: {payload.product_name}
Current Stock (reported): {payload.current_stock}

Please check the real stock levels, decide whether to reorder, and act accordingly.
"""

    try:
        result = _inventory_agent.invoke({
            "messages": [{"role": "user", "content": user_message}]
        })
        summary = result["messages"][-1].content

        return AgentResponse(
            event_id=event_id,
            handled_by=AgentType.INVENTORY,
            success=True,
            result={
                "summary": summary,
                "product_id": payload.product_id,
            },
            processing_time_ms=(time.time() * 1000) - start,
        )

    except Exception as e:
        return AgentResponse(
            event_id=event_id,
            handled_by=AgentType.INVENTORY,
            success=False,
            result={},
            error=str(e),
            processing_time_ms=(time.time() * 1000) - start,
        )