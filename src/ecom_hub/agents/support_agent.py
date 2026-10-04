import time
from langchain.agents import create_agent
from langchain_openai import AzureChatOpenAI

from ecom_hub.config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT_NAME,AZURE_OPENAI_API_VERSION
from ecom_hub.models.customer import CustomerEmail
from ecom_hub.tools.order_tools import look_up_order, get_policy, list_customer_orders
from ecom_hub.models.agent import AgentResponse, AgentType


from ecom_hub.prompts import SUPPORT_SYSTEM_PROMPT


def build_support_agent():
    model=AzureChatOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        azure_deployment=AZURE_OPENAI_DEPLOYMENT_NAME,
        api_version=AZURE_OPENAI_API_VERSION,
    )

    tools=[look_up_order, get_policy, list_customer_orders]

    agent=create_agent(
        model=model,
        tools=tools,
        system_prompt=SUPPORT_SYSTEM_PROMPT
    )
    return agent

_support_agent = build_support_agent()


def _fallback_reply(email: CustomerEmail) -> str:
    customer_name = email.customer_name or "there"
    return (
        f"Hi {customer_name},\n\n"
        "Thank you for reaching out. We’ve received your message and our team is reviewing it. "
        "We’ll follow up as soon as possible with an update.\n\n"
        "Best regards,\n"
        "The E-commerce Support Team"
    )


def run_support_agent(email:CustomerEmail, event_id:str)->AgentResponse:
    """
    Entry point for support agent.
    Takes a CustomerEmail, runs the agent.
    returns structured AgentResponse."""

    start=time.time()*1000

    user_message= f"""
    Customer Email: {email}
    Customer Name: {email.customer_name}
    Subject: {email.subject}

    Message:{email.body}
    Please help this customer & write a professional email reply.
    """

    try:
        result=_support_agent.invoke({
            "messages": [{"role": "user", "content": user_message}]
        })
        reply=result["messages"][-1].content

        return AgentResponse(
            event_id=event_id,
            handled_by=AgentType.SUPPORT,
            success=True,
            result={
                "reply":reply,
                "customer_email": email.customer_email,
                "subject": email.subject,
            },
            processing_time_ms=(time.time()*1000-start)
        )
    except Exception:
        reply = _fallback_reply(email)
        return AgentResponse(
            event_id=event_id,
            handled_by=AgentType.SUPPORT,
            success=True,
            result={
                "reply": reply,
                "customer_email": email.customer_email,
                "subject": email.subject,
            },
            processing_time_ms=(time.time()*1000-start)
        )

