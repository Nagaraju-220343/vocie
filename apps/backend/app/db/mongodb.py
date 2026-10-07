import logging

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConnectionFailure

from app.config.settings import settings

logger = logging.getLogger(__name__)

class MongoDBManager:
    client: MongoClient | None = None
    db: Database | None = None

    @classmethod
    def connect(cls) -> None:
        if cls.client is not None:
            return
            
        logger.info(f"Connecting to MongoDB at {settings.mongodb_uri}")
        try:
            cls.client = MongoClient(
                settings.mongodb_uri,
                serverSelectionTimeoutMS=5000,
                tz_aware=True
            )
            # Ping the database to verify connection
            cls.client.admin.command('ping')
            cls.db = cls.client[settings.mongodb_database]
            logger.info("Successfully connected to MongoDB")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            cls.client = None
            cls.db = None
            raise

    @classmethod
    def disconnect(cls) -> None:
        if cls.client:
            cls.client.close()
            cls.client = None
            cls.db = None
            logger.info("Disconnected from MongoDB")

    @classmethod
    def get_db(cls) -> Database:
        if cls.db is None:
            raise RuntimeError("Database not connected. Call MongoDBManager.connect() first.")
        return cls.db
