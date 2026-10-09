from typing import List, Optional, Tuple

from app.models.order import OrderModel
from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderCreate, OrderUpdate


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
                
        updates = update_data.model_dump(exclude_unset=True)
        if updates:
            self.repository.update(str(order.id), updates)
            if "customerName" in updates and updates["customerName"]:
                from app.repositories.call_repository import CallRepository
                call_repo = CallRepository()
                call = call_repo.get_by_provider_call_id(order.callId)
                if call and call.fromNumber == "unknown":
                    call_repo.update(str(call.id), {"fromNumber": updates["customerName"]})
        return self.get_order(str(order.id))

    def confirm_order(self, identifier: str) -> Tuple[Optional[OrderModel], Optional[str]]:
        order = self.get_order(identifier)
        if not order:
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
            
        if self.repository.update(str(order.id), {"status": "CONFIRMED"}):
            # Sync customer
            from app.models.customer import CustomerModel
            from app.repositories.customer_repository import CustomerRepository
            cust_repo = CustomerRepository()
            customer = None
            if order.phone:
                customer = cust_repo.get_by_phone(order.phone)
            if not customer:
                c = CustomerModel(
                    name=order.customerName or "Unknown",
                    phone=order.phone or "Unknown",
                    address=order.address,
                    callCount=1,
                    lastCallAt=order.createdAt
                )
                cust_repo.create(c)
            else:
                cust_repo.update(str(customer.id), {"callCount": customer.callCount + 1, "lastCallAt": order.createdAt})
            return self.get_order(str(order.id)), None
            
        return None, "Failed to confirm order"
