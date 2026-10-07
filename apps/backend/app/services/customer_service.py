from typing import List, Optional, Tuple

from app.models.customer import CustomerModel
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerService:
    def __init__(self, repository: Optional[CustomerRepository] = None):
        self.repository = repository or CustomerRepository()

    def get_customer(self, customer_id: str) -> Optional[CustomerModel]:
        return self.repository.get_by_id(customer_id)

    def list_customers(self, page: int, page_size: int, filters: dict) -> Tuple[List[CustomerModel], int]:
        skip = (page - 1) * page_size
        items = self.repository.list(limit=page_size, skip=skip, filters=filters)
        total = self.repository.count(filters=filters)
        return items, total

    def create_customer(self, customer_data: CustomerCreate) -> Optional[CustomerModel]:
        customer_model = CustomerModel(**customer_data.model_dump())
        customer_id = self.repository.create(customer_model)
        return self.repository.get_by_id(customer_id)

    def update_customer(self, customer_id: str, update_data: CustomerUpdate) -> Optional[CustomerModel]:
        updates = update_data.model_dump(exclude_unset=True)
        if not updates:
            return self.get_customer(customer_id)
        if self.repository.update(customer_id, updates):
            return self.get_customer(customer_id)
        return None
