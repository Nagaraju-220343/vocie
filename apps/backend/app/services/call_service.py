from typing import List, Optional, Tuple

from app.models.call import CallModel
from app.repositories.call_repository import CallRepository
from app.schemas.call import CallCreate, CallUpdate


class CallService:
    def __init__(self, repository: Optional[CallRepository] = None):
        self.repository = repository or CallRepository()

    def get_call(self, call_id: str) -> Optional[CallModel]:
        return self.repository.get_by_id(call_id)

    def get_call_by_provider_id(self, provider_call_id: str) -> Optional[CallModel]:
        return self.repository.get_by_provider_call_id(provider_call_id)

    def list_calls(self, page: int, page_size: int, filters: dict) -> Tuple[List[CallModel], int]:
        skip = (page - 1) * page_size
        items = self.repository.list(limit=page_size, skip=skip, filters=filters)
        total = self.repository.count(filters=filters)
        return items, total

    def create_call(self, call_data: CallCreate) -> Optional[CallModel]:
        if self.repository.get_by_provider_call_id(call_data.providerCallId):
            return None # Duplicate
        call_model = CallModel(**call_data.model_dump())
        call_id = self.repository.create(call_model)
        return self.repository.get_by_id(call_id)

    def update_call(self, call_id: str, update_data: CallUpdate) -> Optional[CallModel]:
        updates = update_data.model_dump(exclude_unset=True)
        if not updates:
            return self.get_call(call_id)
        if self.repository.update(call_id, updates):
            return self.get_call(call_id)
        return None
