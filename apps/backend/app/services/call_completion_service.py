import logging
from typing import Optional, List

from app.models.call import CallModel
from app.models.customer import CustomerModel
from app.models.order import OrderModel
from app.models.transcript import TranscriptMessage
from app.repositories.call_repository import CallRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.order_repository import OrderRepository
from app.services.extraction_service import OrderExtractionService

logger = logging.getLogger(__name__)

class CallCompletionService:
    def __init__(self) -> None:
        self.call_repo = CallRepository()
        self.customer_repo = CustomerRepository()
        self.order_repo = OrderRepository()
        self.extraction_service = OrderExtractionService()

    def process_completed_call(self, provider_call_id: str, final_transcript: List[TranscriptMessage], retell_call_data: Optional[dict] = None) -> Optional[CallModel]:
        logger.info(f"Processing completed call {provider_call_id}")
        
        call = self._get_or_create_call(provider_call_id)
        if not call or not call.id:
            logger.error(f"Could not find or create call for {provider_call_id}")
            return None
        
        # We process intent even if it was already processed to handle idempotency.
        # But we must avoid duplicating orders.
        result = self.extraction_service.extract(final_transcript)
        logger.info(f"Extraction result: Intent={result.intent}, Validation={result.validationStatus}, Customer={result.customerName}")

        call.intent = result.intent
        call.language = result.language
        
        # Extract customer name from retell call analysis if available
        retell_customer_name = None
        if retell_call_data:
            analysis = retell_call_data.get("call_analysis") or {}
            custom_data = analysis.get("custom_analysis_data") or {}
            if isinstance(custom_data, dict):
                retell_customer_name = custom_data.get("customer_name") or custom_data.get("customerName")
            
            # Duration & recording & summary
            duration_ms = retell_call_data.get("duration_ms")
            if duration_ms is not None:
                call.durationSeconds = max(round(duration_ms / 1000), 1)
            
            rec_url = retell_call_data.get("recording_url")
            if rec_url:
                call.recordingUrl = rec_url
                
            summary = analysis.get("call_summary")
            if summary:
                call.summary = summary

        existing_orders = self.order_repo.find_by_call_id(call.id)
        if not existing_orders:
            existing_orders = self.order_repo.find_by_call_id(provider_call_id)
        order = existing_orders[0] if existing_orders else None

        # Build list of ordered item names to ensure food is never saved as customer name
        ordered_item_names = {i.name.lower().strip() for i in order.items} if order and order.items else set()
        food_blacklist = {"pizza", "pizzas", "burger", "burgers", "margherita", "salad", "salade", "drink", "order", "item", "dish", "business"}

        import re

        def clean_name_str(val: Optional[str]) -> Optional[str]:
            if not val or not val.strip():
                return None
            cleaned = val.strip()
            # Strip multiple leading speech fillers
            cleaned = re.sub(
                r"^(\s*(uh|um|er|ah|eh|oh|well|yeah|yep|so|it's|its|im|i'm|this is|my name is|name is|je m'appelle|c'est|le nom est)\b[\s,.:!?-]*)+",
                "",
                cleaned,
                flags=re.IGNORECASE
            ).strip()
            cleaned = re.sub(r"^[\s,.:!?-]+", "", cleaned).rstrip(",.:!?-").strip()
            if re.fullmatch(r"([a-zA-Z]\s+)+[a-zA-Z]", cleaned):
                cleaned = cleaned.replace(" ", "")
            if not cleaned or len(cleaned) < 2:
                return None
            lower = cleaned.lower()
            if lower in ["unknown", "web browser", "guest caller", "web call", "customer"] or "browser" in lower:
                return None
            if lower in ordered_item_names:
                return False
            words = set(lower.split())
            if words & food_blacklist:
                return None
            return cleaned.title()

        # Phone matching for customer reconciliation across calls
        phone_val = (order.phone if order else None) or result.phone
        existing_cust_name = None
        if phone_val:
            phone_digits = re.sub(r"\D", "", phone_val)
            if len(phone_digits) >= 7:
                for c in self.customer_repo.list():
                    c_digits = re.sub(r"\D", "", c.phone or "")
                    if c_digits and (phone_digits.endswith(c_digits[-8:]) or c_digits.endswith(phone_digits[-8:])):
                        cleaned_c_name = clean_name_str(c.name)
                        if cleaned_c_name:
                            existing_cust_name = cleaned_c_name
                            break

        # Determine best customer name: prioritize existing customer on file, then confirmed order name, then retell analysis, then transcript extraction
        candidate_name = None
        for name_source in [
            existing_cust_name,
            (order.customerName if order else None),
            retell_customer_name,
            result.customerName,
            call.customerName,
            call.fromNumber
        ]:
            cleaned_val = clean_name_str(name_source)
            if cleaned_val:
                candidate_name = cleaned_val
                break

        if candidate_name:
            call.customerName = candidate_name
            call.fromNumber = candidate_name
            if order and order.id:
                self.order_repo.update(str(order.id), {"customerName": candidate_name})
        elif not call.fromNumber or not clean_name_str(call.fromNumber):
            call.fromNumber = "Customer"
        
        if result.intent == "ORDER":
            customer = self._upsert_customer(result, phone=phone_val, customer_name=candidate_name)
            if customer:
                if not order:
                    logger.info("Creating new order from call.")
                    order = self._create_order(str(call.id), str(customer.id) if customer and customer.id else None, result)
                else:
                    logger.info("Order already exists for this call. Updating it.")
                    updates = {
                        "customerId": customer.id if customer else order.customerId,
                        "customerName": candidate_name or order.customerName,
                        "phone": phone_val or order.phone,
                        "address": result.address or order.address,
                    }
                    if order.status != "CONFIRMED":
                        updates["items"] = [item.model_dump() for item in result.items] if result.items else order.items
                        # If call ended without explicit confirmation, mark as CANCELLED so it does not linger as duplicate draft
                        updates["status"] = "CANCELLED"
                        updates["notes"] = (order.notes or "") + " [Call ended without confirmation]"
                        updates["orderType"] = result.fulfillmentType or order.orderType
                    
                    if order.id:
                        self.order_repo.update(str(order.id), updates)
                        order = self.order_repo.get_by_id(str(order.id))
            elif order and order.status != "CONFIRMED":
                # Order exists but was never confirmed before call ended
                self.order_repo.update(str(order.id), {
                    "status": "CANCELLED",
                    "notes": (order.notes or "") + " [Call ended without confirmation]"
                })
        
        call.status = "COMPLETED"
        self.call_repo.update(str(call.id), call.model_dump(exclude_none=True))
        
        return self.call_repo.get_by_provider_call_id(provider_call_id)

    def process_call_analysis(self, provider_call_id: str, retell_call_data: dict) -> Optional[CallModel]:
        """
        Process post-call analysis webhook from Retell (call_analyzed event).
        Extracts LLM post-call analysis custom data (like customer_name) and summary.
        """
        call = self.call_repo.get_by_provider_call_id(provider_call_id)
        if not call or not call.id:
            return None

        updates = {}
        analysis = retell_call_data.get("call_analysis") or {}
        custom_data = analysis.get("custom_analysis_data") or {}
        
        cust_name = None
        if isinstance(custom_data, dict):
            cust_name = custom_data.get("customer_name") or custom_data.get("customerName")

        food_blacklist = {"pizza", "pizzas", "burger", "burgers", "margherita", "salad", "salade", "drink", "order", "item", "dish", "business"}
        if cust_name and cust_name.strip():
            clean_name = cust_name.strip()
            cand_words = set(clean_name.lower().split())
            if not (cand_words & food_blacklist) and clean_name.lower() not in ["unknown", "web browser", "customer"]:
                updates["customerName"] = clean_name
                if not call.fromNumber or call.fromNumber in ["unknown", "Web Browser", "Guest Caller", "Web Call", "Customer", ""] or "browser" in call.fromNumber.lower():
                    updates["fromNumber"] = clean_name
        elif not call.fromNumber or call.fromNumber in ["unknown", "Web Browser"] or "browser" in call.fromNumber.lower():
            updates["fromNumber"] = "Customer"

        summary = analysis.get("call_summary")
        if summary:
            updates["summary"] = summary

        duration_ms = retell_call_data.get("duration_ms")
        if duration_ms is not None:
            updates["durationSeconds"] = max(round(duration_ms / 1000), 1)

        rec_url = retell_call_data.get("recording_url")
        if rec_url:
            updates["recordingUrl"] = rec_url

        if updates:
            self.call_repo.update(str(call.id), updates)
            
            # Broadcast update via socket
            try:
                import asyncio
                from app.realtime.socket import publisher
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = asyncio.get_event_loop()
                loop.create_task(publisher.publish("call.updated", provider_call_id, 0, {
                    "callId": str(call.id),
                    "providerCallId": provider_call_id,
                    **updates
                }))
            except Exception as e:
                logger.warning(f"Could not publish call.updated event: {e}")

        return self.call_repo.get_by_provider_call_id(provider_call_id)

    def _get_or_create_call(self, provider_call_id: str) -> Optional[CallModel]:
        call = self.call_repo.get_by_provider_call_id(provider_call_id)
        if not call:
            logger.info("Call not found, creating new one.")
            new_call = CallModel(
                providerCallId=provider_call_id,
                direction="inbound",
                fromNumber="Customer",
                toNumber="unknown",
                language="unknown",
                intent="UNKNOWN",
                status="IN_PROGRESS"
            )
            created_id = self.call_repo.create(new_call)
            call = self.call_repo.get_by_id(created_id)
        return call

    def _upsert_customer(self, result, phone: Optional[str] = None, customer_name: Optional[str] = None) -> Optional[CustomerModel]:
        target_phone = phone or result.phone
        if not target_phone:
            logger.warning("Cannot upsert customer: No phone number available.")
            return None
            
        import re
        target_digits = re.sub(r"\D", "", target_phone)
        customers = self.customer_repo.list()
        
        # Match by phone digits (last 8 digits)
        existing = None
        for c in customers:
            c_digits = re.sub(r"\D", "", c.phone or "")
            if c_digits and (target_digits.endswith(c_digits[-8:]) or c_digits.endswith(target_digits[-8:])):
                existing = c
                break
                
        name_val = customer_name or result.customerName
        
        if existing:
            updates = {}
            if name_val and (not existing.name or existing.name.lower() in ["unknown", "customer"]):
                updates["name"] = name_val
            updates["callCount"] = existing.callCount + 1
            if existing.id:
                self.customer_repo.update(str(existing.id), updates)
                return self.customer_repo.get_by_id(str(existing.id))
            return existing
        else:
            new_customer = CustomerModel(
                name=name_val or "Customer",
                phone=target_phone,
                callCount=1
            )
            c_id = self.customer_repo.create(new_customer)
            return self.customer_repo.get_by_id(c_id)

    def _create_order(self, call_id: str, customer_id: Optional[str], result) -> OrderModel:
        order = OrderModel(
            callId=call_id,
            customerId=customer_id,
            customerName=result.customerName,
            phone=result.phone,
            address=result.address,
            items=result.items,
            status=result.validationStatus,
            orderType=result.fulfillmentType or "UNKNOWN"
        )
        self.order_repo.create(order)
        return order
