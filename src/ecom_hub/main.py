from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ..ecom_hub.config import APP_ENV

app = FastAPI(
    title="E-com Agent Hub",
    description="AI-powered e-commerce operations hub",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "env": APP_ENV,
        "version": "0.1.0",
    }


@app.get("/")
async def root():
    return {"message": "E-com Agent Hub is running 🚀"}