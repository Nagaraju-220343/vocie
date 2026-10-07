import hmac
import hashlib
import json
import logging
from typing import Any, Dict

from app.config.settings import settings

logger = logging.getLogger(__name__)

class RetellWebhookAdapter:
    def __init__(self) -> None:
        self.secret = settings.retell_webhook_secret

    def verify_signature(self, signature: str, payload: bytes) -> bool:
        if not self.secret:
            logger.warning("Webhook secret is not configured. Failing verification.")
            return False
            
        expected_signature = hmac.new(
            self.secret.encode("utf-8"),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
