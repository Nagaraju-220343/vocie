from typing import List, Optional

from bson.objectid import ObjectId
from pymongo.collection import Collection

from app.db.mongodb import MongoDBManager
from app.models.order import OrderModel


class OrderRepository:
    @property
    def collection(self) -> Collection:
        return MongoDBManager.get_db().orders

    def create(self, order: OrderModel) -> str:
        doc = order.model_dump(by_alias=True, exclude={"id"}, exclude_none=True)
        result = self.collection.insert_one(doc)
        return str(result.inserted_id)

    def get_by_id(self, order_id: str) -> Optional[OrderModel]:
        doc = self.collection.find_one({"_id": ObjectId(order_id)})
        if doc and "_id" in doc: doc["_id"] = str(doc["_id"])
        return OrderModel(**doc) if doc else None

    def update(self, order_id: str, updates: dict) -> bool:
        result = self.collection.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": updates}
        )
        return result.modified_count > 0

    def list(self, limit: int = 50, skip: int = 0, filters: Optional[dict] = None) -> List[OrderModel]:
        cursor = self.collection.find(filters or {}).sort("createdAt", -1).skip(skip).limit(limit)
        return [OrderModel(**{**doc, "_id": str(doc["_id"])}) for doc in cursor if doc]

    def count(self, filters: Optional[dict] = None) -> int:
        return self.collection.count_documents(filters or {})

    def find_by_call_id(self, call_id: str) -> List[OrderModel]:
        cursor = self.collection.find({"callId": call_id}).sort("createdAt", -1)
        return [OrderModel(**{**doc, "_id": str(doc["_id"])}) for doc in cursor if doc]
