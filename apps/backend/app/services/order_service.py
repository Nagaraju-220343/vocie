from typing import List, Optional, Tuple

from app.models.order import OrderModel
from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderCreate, OrderUpdate


class OrderService:
    def __init__(self, repository: Optional[OrderRepository] = None):
        self.repository = repository or OrderRepository()

    def get_order(self, order_id: str) -> Optional[OrderModel]:
        return self.repository.get_by_id(order_id)

    def list_orders(self, page: int, page_size: int, filters: dict) -> Tuple[List[OrderModel], int]:
        skip = (page - 1) * page_size
        items = self.repository.list(limit=page_size, skip=skip, filters=filters)
        total = self.repository.count(filters=filters)
        return items, total

    def create_order(self, order_data: OrderCreate) -> Optional[OrderModel]:
        order_model = OrderModel(**order_data.model_dump())
        order_id = self.repository.create(order_model)
        return self.repository.get_by_id(order_id)

    def update_order(self, order_id: str, update_data: OrderUpdate) -> Optional[OrderModel]:
        updates = update_data.model_dump(exclude_unset=True)
        if not updates:
            return self.get_order(order_id)
        if self.repository.update(order_id, updates):
            return self.get_order(order_id)
        return None
