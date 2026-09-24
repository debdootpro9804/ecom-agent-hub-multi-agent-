# src/ecom_hub/api/dependencies.py

import time
from fastapi import Header, HTTPException


async def verify_api_key(x_api_key: str = Header(default="dev-key")):
    """
    Simple API key check.
    In production this would check against a real secrets store.
    For now, any request with header X-API-Key: dev-key passes.
    
    FastAPI automatically reads the X-Api-Key header and passes
    it here — we don't write any parsing code.
    """
    if x_api_key != "dev-key":
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    return x_api_key


def get_request_timer():
    """
    Returns the current time in ms.
    Used to measure how long each request takes.
    We'll attach this to AgentResponse.processing_time_ms later.
    """
    return time.time() * 1000