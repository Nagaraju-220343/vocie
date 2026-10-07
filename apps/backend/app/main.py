from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config.settings import settings
from app.db.indexes import ensure_indexes
from app.db.mongodb import MongoDBManager
from app.logging.setup import setup_logging
from app.utils.exceptions import AppException, app_exception_handler

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Startup
    MongoDBManager.connect()
    ensure_indexes()
    yield
    # Shutdown
    MongoDBManager.disconnect()

app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

# Set up CORS
origins = [origin.strip() for origin in settings.cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)  # type: ignore

# Routers
app.include_router(api_router, prefix="/api")

# Socket.IO
import socketio
from app.realtime.socket import sio
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

