import logging
from fastapi import FastAPI
from app.api.routes import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(
    title="FrontRow LLM Engine Microservice",
    description="Decoupled natural language query parser for event ticketing search",
    version="0.1.0",
)

app.include_router(router)


@app.get("/")
async def root():
    return {
        "service": "FrontRow LLM Engine Microservice",
        "docs": "/docs",
        "health": "/health",
    }
