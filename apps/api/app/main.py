from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health
from app.config.settings import settings
from app.logging.setup import setup_logging
from app.utils.exceptions import AppException, app_exception_handler

setup_logging()

app = FastAPI(title=settings.app_name, version="0.1.0")

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
app.include_router(health.router, prefix="/api", tags=["health"])
