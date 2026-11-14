import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from pymongo.errors import PyMongoError

from backend.config.database_config import get_db_client
from backend.config.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    db_client: AsyncIOMotorClient = get_db_client()

    app.state.db_client = db_client

    logger.info("Application startup complete")

    try:
        yield
    finally:
        db_client.close()
        logger.info("Application shutdown complete")


app = FastAPI(
    title="Backend API",
    version="1.0.0",
    lifespan=lifespan,
)


class HealthResponse(BaseModel):
    status: Literal["healthy", "unhealthy"]
    database: Literal["connected", "disconnected"]


@app.get("/api/v1/health", response_model=HealthResponse, tags=["Health"])
async def health_check(request: Request) -> JSONResponse:
    db_client: AsyncIOMotorClient = request.app.state.db_client

    try:
        await db_client.admin.command("ping")
        db_status: Literal["connected", "disconnected"] = "connected"
    except PyMongoError:
        logger.warning("Database health check failed", exc_info=True)
        db_status = "disconnected"

    healthy = db_status == "connected"
    logger.info(
        "Health check result: database=%s healthy=%s",
        db_status,
        healthy,
    )

    return JSONResponse(
        status_code=200 if healthy else 503,
        content={
            "status": "healthy" if healthy else "unhealthy",
            "database": db_status,
        },
    )
