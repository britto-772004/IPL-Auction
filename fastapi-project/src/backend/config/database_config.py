from motor.motor_asyncio import AsyncIOMotorClient

from backend.config.env_config import settings


def get_db_client() -> AsyncIOMotorClient:
    return AsyncIOMotorClient(settings.mongodb_url)
