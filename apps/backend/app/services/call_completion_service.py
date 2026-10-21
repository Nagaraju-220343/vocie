import logging
from typing import List, Optional

from app.models.call import CallModel
from app.models.customer import CustomerModel
from app.models.order import OrderModel
from app.models.transcript import TranscriptMessage
from app.repositories.call_repository import CallRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.order_repository import OrderRepository

logger = logging.getLogger(__name__)

class CallCompletionService:
    def __init__(self) -> None:
        self.call_repo = CallRepository()
        self.customer_repo = CustomerRepository()
        self.order_repo = OrderRepository()

    def process_completed_call(self, provider_call_id: str, final_transcript: List[TranscriptMessage], retell_call_data: Optional[dict] = None) -> Optional[CallModel]:
        logger.info(f"Processing completed call {provider_call_id}")
        
        call = self._get_or_create_call(provider_call_id)
        if not call or not call.id:
            logger.error(f"Could not find or create call for {provider_call_id}")
            return None

        full_transcript_lower = " ".join([m.text for m in final_transcript]).lower()

        # Extract metadata from Retell call data (duration, recording, summary only)
        retell_customer_name = None
        if retell_call_data:
            analysis = retell_call_data.get("call_analysis") or {}
            custom_data = analysis.get("custom_analysis_data") or {}
            if isinstance(custom_data, dict):
                retell_customer_name = custom_data.get("customer_name") or custom_data.get("customerName")

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


        # Build a food blacklist to avoid saving a food item as a customer name
        ordered_item_names = {i.name.lower().strip() for i in order.items} if order and order.items else set()
        food_blacklist = {"pizza", "pizzas", "burger", "burgers", "margherita", "salad", "salade", "drink", "order", "item", "dish", "business"}

        import re

        def clean_name_str(val: Optional[str]) -> Optional[str]:
            if not val or not val.strip():
                return None
            cleaned = val.strip()
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
                return None
            words = set(lower.split())
            if words & food_blacklist:
                return None
            return cleaned.title()

        # Phone from the order (set by agent during call)
        phone_val = order.phone if order else None

        # Determine best customer name using only data collected during this call.
        # We intentionally do NOT fall back to phone-matched historical records
        # to avoid silently assigning the wrong name from a previous caller.
        candidate_name = None
        for name_source in [
            (order.customerName if order else None),
            retell_customer_name,
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

        # Upsert customer record if we have a phone number
        if phone_val and order:
            customer = self._upsert_customer_by_phone(
                phone=phone_val,
                customer_name=candidate_name,
                order_customer_id=str(order.customerId) if order.customerId else None
            )
            if customer and order and order.id:
                self.order_repo.update(str(order.id), {"customerId": customer.id})

        call.status = "COMPLETED"
        self.call_repo.update(str(call.id), call.model_dump(exclude_none=True))

        return self.call_repo.get_by_provider_call_id(provider_call_id)

    def process_call_analysis(self, provider_call_id: str, retell_call_data: dict) -> Optional[CallModel]:
        """
        Process post-call analysis webhook from Retell (call_analyzed event).
        Only updates metadata: call duration, recording URL, and call summary.
        Does NOT overwrite customerName — that is already set correctly by update_order during the call.
        """
        call = self.call_repo.get_by_provider_call_id(provider_call_id)
        if not call or not call.id:
            return None

        updates = {}
        analysis = retell_call_data.get("call_analysis") or {}

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

    def _upsert_customer_by_phone(self, phone: str, customer_name: Optional[str] = None, order_customer_id: Optional[str] = None) -> Optional[CustomerModel]:
        """Upsert a customer record by phone number and increment call count."""
        if not phone:
            logger.warning("Cannot upsert customer: No phone number available.")
            return None

        import re
        target_digits = re.sub(r"\D", "", phone)
        customers = self.customer_repo.list()

        existing = None
        for c in customers:
            c_digits = re.sub(r"\D", "", c.phone or "")
            if c_digits and (target_digits.endswith(c_digits[-8:]) or c_digits.endswith(target_digits[-8:])):
                existing = c
                break

        if existing:
            updates: dict = {"callCount": existing.callCount + 1}
            # Only update name if the existing record has a placeholder
            if customer_name and (not existing.name or existing.name.lower() in ["unknown", "customer"]):
                updates["name"] = customer_name
            if existing.id:
                self.customer_repo.update(str(existing.id), updates)
                return self.customer_repo.get_by_id(str(existing.id))
            return existing
        else:
            new_customer = CustomerModel(
                name=customer_name or "Customer",
                phone=phone,
                callCount=1
            )
            c_id = self.customer_repo.create(new_customer)
            return self.customer_repo.get_by_id(c_id)
