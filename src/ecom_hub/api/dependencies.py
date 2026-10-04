# src/ecom_hub/api/dependencies.py

import time
from fastapi import Header, HTTPException


async def verify_api_key(x_api_key: str | None = Header(default=None)):
    """
    Require a valid API key header for protected endpoints.
    Missing or incorrect values are rejected with 401.
    """
    if not x_api_key or x_api_key != "dev-key":
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )
    return x_api_key


def get_request_timer():
    """
    Returns the current time in ms.
    Used to measure how long each request takes.
    We'll attach this to AgentResponse.processing_time_ms later.
    """
    return time.time() * 1000