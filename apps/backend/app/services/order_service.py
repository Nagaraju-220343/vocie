import re
from typing import List, Optional, Tuple

from app.models.order import OrderModel
from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderCreate, OrderUpdate


def clean_name(val: Optional[str]) -> Optional[str]:
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
    return cleaned.title()


class OrderService:
    def __init__(self, repository: Optional[OrderRepository] = None):
        self.repository = repository or OrderRepository()

    def get_order(self, identifier: str) -> Optional[OrderModel]:
        from bson.objectid import ObjectId
        if ObjectId.is_valid(identifier):
            order = self.repository.get_by_id(identifier)
            if order:
                return order
                
        orders = self.repository.find_by_call_id(identifier)
        if orders:
            return orders[0]
        return None

    def list_orders(self, page: int, page_size: int, filters: dict) -> Tuple[List[OrderModel], int]:
        skip = (page - 1) * page_size
        items = self.repository.list(limit=page_size, skip=skip, filters=filters)
        total = self.repository.count(filters=filters)
        return items, total

    def create_order(self, order_data: OrderCreate) -> Optional[OrderModel]:
        order_model = OrderModel(**order_data.model_dump())
        order_id = self.repository.create(order_model)
        return self.repository.get_by_id(order_id)

    def update_order(self, identifier: str, update_data: OrderUpdate) -> Tuple[Optional[OrderModel], Optional[str]]:
        order = self.get_order(identifier)
        from bson.objectid import ObjectId
        
        # Validate items if provided
        if update_data.items is not None:
            if len(update_data.items) == 0:
                return None, "Order items cannot be empty when items are provided"
            for item in update_data.items:
                if not item.name or not item.name.strip():
                    return None, "Item name cannot be empty"
                if item.quantity <= 0:
                    return None, f"Invalid quantity ({item.quantity}) for item {item.name}. Quantity must be positive"

        if not order:
            if not ObjectId.is_valid(identifier):
                new_order = OrderCreate(
                    callId=identifier,
                    status="DRAFT",
                    orderType=update_data.orderType or "UNKNOWN",
                    restaurant=update_data.restaurant or "dominos_le_chesnay",
                    source=update_data.source or "retell_voice_agent"
                )
                order_model = OrderModel(**new_order.model_dump())
                created_id = self.repository.create(order_model)
                order = self.repository.get_by_id(created_id)
            else:
                return None, f"Order {identifier} not found"
                
        if not order or not order.id:
            return None, "Failed to persist draft order"
                
        updates = update_data.model_dump(exclude_unset=True)
        if "customerName" in updates and updates["customerName"]:
            cleaned_cname = clean_name(updates["customerName"])
            if cleaned_cname:
                updates["customerName"] = cleaned_cname

        if updates:
            success = self.repository.update(str(order.id), updates)
            if not success and str(order.id):
                # Verify whether the document already matches or update failed
                refetched = self.get_order(str(order.id))
                if not refetched:
                    return None, "Database update failed: record not found"
            if "customerName" in updates and updates["customerName"]:
                from app.repositories.call_repository import CallRepository
                call_repo = CallRepository()
                call = call_repo.get_by_provider_call_id(order.callId)
                if call and call.id:
                    call_repo.update(str(call.id), {"fromNumber": updates["customerName"], "customerName": updates["customerName"]})
                    
        persisted = self.get_order(str(order.id))
        if not persisted:
            return None, "Failed to retrieve persisted order after update"
        return persisted, None

    def confirm_order(self, identifier: str) -> Tuple[Optional[OrderModel], Optional[str], bool]:
        """
        Confirms an order.
        Returns: (order, error_message, is_duplicate)
        """
        order = self.get_order(identifier)
        if not order or not order.id:
            return None, "Order draft does not exist. Please place an order first", False
        
        # Idempotency check: prevent duplicate mutations
        if order.status == "CONFIRMED":
            return order, None, True
            
        if not order.items or len(order.items) == 0:
            return None, "Order must have at least one valid item before confirmation", False
            
        for item in order.items:
            if item.quantity <= 0:
                return None, f"Invalid quantity for item {item.name}. Must be at least 1", False
                
        if not order.customerName and not order.phone:
            return None, "Customer details required: please provide customer name or phone number", False
            
        if order.orderType == "DELIVERY" and (not order.address or not order.address.strip()):
            return None, "Delivery address is required for DELIVERY orders", False
            
        clean_cname = clean_name(order.customerName) or order.customerName
        updated_status = self.repository.update(str(order.id), {"status": "CONFIRMED", "customerName": clean_cname})
        if updated_status:
            if clean_cname:
                from app.repositories.call_repository import CallRepository
                call_repo = CallRepository()
                call = call_repo.get_by_provider_call_id(order.callId)
                if call and call.id:
                    call_repo.update(str(call.id), {"fromNumber": clean_cname, "customerName": clean_cname})
            
            # Sync customer profile
            from app.models.customer import CustomerModel
            from app.repositories.customer_repository import CustomerRepository
            cust_repo = CustomerRepository()
            customer = None
            if order.phone:
                phone_digits = re.sub(r"\D", "", order.phone)
                for c in cust_repo.list():
                    c_digits = re.sub(r"\D", "", c.phone or "")
                    if c_digits and (phone_digits.endswith(c_digits[-8:]) or c_digits.endswith(phone_digits[-8:])):
                        customer = c
                        break
            if not customer:
                c = CustomerModel(
                    name=clean_cname or "Customer",
                    phone=order.phone or "Unknown",
                    address=order.address,
                    callCount=1,
                    lastCallAt=order.createdAt
                )
                cust_repo.create(c)
            else:
                cust_updates = {"callCount": customer.callCount + 1, "lastCallAt": order.createdAt}
                if clean_cname and (not customer.name or customer.name.lower() in ["unknown", "customer"]):
                    cust_updates["name"] = clean_cname
                cust_repo.update(str(customer.id), cust_updates)
            
            # Cancel any prior unconfirmed draft orders for this same phone
            if order.phone:
                phone_digits = re.sub(r"\D", "", order.phone)
                for old_ord in self.repository.list():
                    if old_ord.id and str(old_ord.id) != str(order.id) and old_ord.status in ["DRAFT", "PENDING", "REVIEW_REQUIRED"]:
                        old_digits = re.sub(r"\D", "", old_ord.phone or "")
                        if old_digits and (phone_digits.endswith(old_digits[-8:]) or old_digits.endswith(phone_digits[-8:])):
                            self.repository.update(str(old_ord.id), {"status": "CANCELLED", "notes": (old_ord.notes or "") + " [Superseded by confirmed order]"})

            confirmed_order = self.get_order(str(order.id))
            return confirmed_order, None, False
            
        return None, "Database persistence failed during order confirmation", False
