import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from core.config import settings
from typing import Optional
import certifi

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None


db = MongoDB()


async def connect_to_mongo():
    try:
        # # logger.debug(f"Connecting to MongoDB at {settings.MONGODB_URL}")
        db.client = AsyncIOMotorClient(settings.MONGODB_URL, tlsCAFile=certifi.where())
        db.db = db.client[settings.DATABASE_NAME]
        # # logger.debug(f"Connected to MongoDB: {settings.DATABASE_NAME}")
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {str(e)}")
        raise e


async def close_mongo_connection():
    if db.client is not None:
        # # logger.debug("Closing MongoDB connection")
        db.client.close()
