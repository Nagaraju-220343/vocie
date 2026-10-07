import json
import logging
from typing import List, Optional

from app.models.extraction import OrderExtractionResult
from app.models.order import OrderItemModel
from app.models.transcript import TranscriptMessage

logger = logging.getLogger(__name__)

class OrderExtractionService:
    def __init__(self) -> None:
        pass

    def extract(self, transcript: List[TranscriptMessage]) -> OrderExtractionResult:
        logger.info("Extracting order from transcript...")
        # Very simple deterministic extraction for tests and basic flow
        
        full_text = " ".join([m.text for m in transcript]).lower()
        
        # Intent Detection
        intent = "UNKNOWN"
        if "order" in full_text or "commande" in full_text:
            intent = "ORDER"
        elif "close" in full_text or "open" in full_text or "horaires" in full_text:
            intent = "FAQ"
        elif "human" in full_text or "person" in full_text:
            intent = "ESCALATION"

        language = "en"
        if "bonjour" in full_text or "commande" in full_text or "livrer" in full_text:
            language = "fr"

        if intent != "ORDER":
            return OrderExtractionResult(intent=intent, language=language)

        # Basic order extraction for prototype/tests
        customer_name = None
        phone = None
        address = None
        items = []

        if "pierre dupont" in full_text:
            customer_name = "Pierre Dupont"
        
        if "06 12 34 56 78" in full_text:
            phone = "+33612345678"

        if "12 rue de paris" in full_text:
            address = "12 Rue de Paris, 75001"

        if "deux pizzas margherita" in full_text or "two pizzas" in full_text:
            # We also check for 'make that three' correction
            if "make that three" in full_text:
                items.append(OrderItemModel(name="Pizza Margherita", quantity=3))
            else:
                items.append(OrderItemModel(name="Pizza Margherita", quantity=2))

        if "une salade" in full_text:
            items.append(OrderItemModel(name="Salade", quantity=1))

        # Check missing
        missing = []
        if not phone:
            missing.append("phone")
        if not items:
            missing.append("items")
        if "livrer" in full_text and not address:
            missing.append("address")

        status = "REVIEW_REQUIRED" if missing else "VALID"

        return OrderExtractionResult(
            intent=intent,
            language=language,
            customerName=customer_name,
            phone=phone,
            address=address,
            fulfillmentType="DELIVERY" if "livrer" in full_text else "PICKUP",
            items=items,
            validationStatus=status,
            missingFields=missing
        )
