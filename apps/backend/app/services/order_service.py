from typing import List, Optional, Tuple

from app.models.order import OrderModel
from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderCreate, OrderUpdate


import re

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

    def update_order(self, identifier: str, update_data: OrderUpdate) -> Optional[OrderModel]:
        order = self.get_order(identifier)
        from bson.objectid import ObjectId
        
        if not order:
            if not ObjectId.is_valid(identifier):
                new_order = OrderCreate(
                    callId=identifier,
                    status="DRAFT",
                    orderType="UNKNOWN"
                )
                order_model = OrderModel(**new_order.model_dump())
                created_id = self.repository.create(order_model)
                order = self.repository.get_by_id(created_id)
            else:
                return None
                
        if not order or not order.id:
            return None
                
        updates = update_data.model_dump(exclude_unset=True)
        if "customerName" in updates and updates["customerName"]:
            cleaned_cname = clean_name(updates["customerName"])
            if cleaned_cname:
                updates["customerName"] = cleaned_cname

        if updates:
            self.repository.update(str(order.id), updates)
            if "customerName" in updates and updates["customerName"]:
                from app.repositories.call_repository import CallRepository
                call_repo = CallRepository()
                call = call_repo.get_by_provider_call_id(order.callId)
                if call and call.id:
                    call_repo.update(str(call.id), {"fromNumber": updates["customerName"], "customerName": updates["customerName"]})
        return self.get_order(str(order.id))

    def confirm_order(self, identifier: str) -> Tuple[Optional[OrderModel], Optional[str]]:
        order = self.get_order(identifier)
        if not order or not order.id:
            return None, "Order not found"
        
        if order.status == "CONFIRMED":
            return order, None
            
        if not order.items:
            return None, "Order must have at least one item"
            
        for item in order.items:
            if item.quantity <= 0:
                return None, f"Invalid quantity for item {item.name}"
                
        if not order.customerName and not order.phone:
            return None, "Customer name or phone is required"
            
        if order.orderType == "DELIVERY" and not order.address:
            return None, "Delivery address is required for DELIVERY orders"
            
        clean_cname = clean_name(order.customerName) or order.customerName
        if self.repository.update(str(order.id), {"status": "CONFIRMED", "customerName": clean_cname}):
            if clean_cname:
                from app.repositories.call_repository import CallRepository
                call_repo = CallRepository()
                call = call_repo.get_by_provider_call_id(order.callId)
                if call and call.id:
                    call_repo.update(str(call.id), {"fromNumber": clean_cname, "customerName": clean_cname})
            
            # Sync customer
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

            return self.get_order(str(order.id)), None
            
        return None, "Failed to confirm order"
