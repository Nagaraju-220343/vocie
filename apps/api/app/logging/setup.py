import logging
import sys

from app.config.settings import settings


def setup_logging() -> None:
    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    logger = logging.getLogger(__name__)
    logger.info(f"Starting {settings.app_name}")
    logger.info(f"Environment: {settings.app_env}")
