# src/ecom_hub/main.py

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..ecom_hub.config import APP_ENV, validate_required_secrets
from ..ecom_hub.api.routes import health, events, orders


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Code before yield runs on startup.
    Code after yield runs on shutdown.
    This is the modern FastAPI way — replaces @app.on_event("startup").
    """
    # STARTUP
    print("[startup] E-com Agent Hub starting...")
    validate_required_secrets()
    print("[startup] Ready ✅")

    yield  # app is live and serving requests here

    # SHUTDOWN
    print("[shutdown] Shutting down...")


app = FastAPI(
    title="E-com Agent Hub",
    description="AI-powered e-commerce operations hub",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router)
app.include_router(events.router)
app.include_router(orders.router)


@app.get("/", tags=["Root"])
async def root():
    return {"message": "E-com Agent Hub is running 🚀", "env": APP_ENV}