import hmac
import hashlib
import json
import logging
import re
from typing import Any, Dict

from app.config.settings import settings

logger = logging.getLogger(__name__)

class RetellWebhookAdapter:
    def verify_signature(self, signature: str, payload: bytes) -> bool:
        api_key = settings.retell_api_key
        
        if not api_key:
            logger.warning("API key is not configured. Failing verification.")
            return False
            
        try:
            # Retell signatures have the format v={timestamp},d={digest}
            match = re.fullmatch(r"v=(\d+),d=([0-9a-f]{64})", signature)
            if not match:
                logger.warning("Invalid signature format.")
                return False
                
            poststamp = match.group(1)
            post_digest = match.group(2)
            
            # The digest is computed on the raw payload + timestamp string
            input_bytes = payload + poststamp.encode("utf-8")
            
            expected_digest = hmac.new(
                api_key.encode("utf-8"),
                input_bytes,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(expected_digest, post_digest)
        except Exception as e:
            logger.error(f"Signature verification error: {str(e)}")
            return False
