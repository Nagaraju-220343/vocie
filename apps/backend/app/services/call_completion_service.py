import logging
from typing import Optional, List

from app.models.call import CallModel
from app.models.customer import CustomerModel
from app.models.order import OrderModel, OrderItemModel
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

    def process_completed_call(self, provider_call_id: str, final_transcript: List[TranscriptMessage]) -> Optional[CallModel]:
        logger.info(f"Processing completed call {provider_call_id}")
        
        call = self._get_or_create_call(provider_call_id)
        
        # We process intent even if it was already processed to handle idempotency.
        # But we must avoid duplicating orders.
        
        result = self.extraction_service.extract(final_transcript)
        logger.info(f"Extraction result: Intent={result.intent}, Validation={result.validationStatus}")

        call.intent = result.intent
        call.language = result.language
        
        if result.intent == "ORDER":
            customer = self._upsert_customer(result)
            if customer:
                # Update call customer ref if your model has it (Optional)
                # Ensure no duplicate order
                existing_orders = self.order_repo.list() # Ideally find_by_call_id
                order = next((o for o in existing_orders if o.callId == call.id), None)
                if not order:
                    logger.info("Creating new order from call.")
                    order = self._create_order(call.id, customer.id, result)
                else:
                    logger.info("Order already exists for this call.")
        
        call.status = "COMPLETED"
        self.call_repo.update(str(call.id), call.model_dump(exclude_none=True))
        
        return self.call_repo.get_by_provider_call_id(provider_call_id)

    def _get_or_create_call(self, provider_call_id: str) -> CallModel:
        call = self.call_repo.get_by_provider_call_id(provider_call_id)
        if not call:
            logger.info("Call not found, creating new one.")
            new_call = CallModel(
                providerCallId=provider_call_id,
                direction="inbound",
                fromNumber="unknown",
                toNumber="unknown",
                language="unknown",
                intent="UNKNOWN",
                status="IN_PROGRESS"
            )
            created_id = self.call_repo.create(new_call)
            call = self.call_repo.get_by_id(created_id)
        return call # type: ignore

    def _upsert_customer(self, result) -> Optional[CustomerModel]:
        if not result.phone:
            logger.warning("Cannot upsert customer: No phone number extracted.")
            return None
            
        customers = self.customer_repo.list()
        existing = next((c for c in customers if c.phone == result.phone), None)
        
        if existing:
            updates = {}
            if result.customerName and not existing.name:
                updates["name"] = result.customerName
            updates["callCount"] = existing.callCount + 1
            self.customer_repo.update(str(existing.id), updates)
            return self.customer_repo.get_by_id(str(existing.id))
        else:
            new_customer = CustomerModel(
                name=result.customerName,
                phone=result.phone,
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
