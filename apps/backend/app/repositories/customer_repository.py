from typing import List, Optional

from bson.objectid import ObjectId
from pymongo.collection import Collection

from app.db.mongodb import MongoDBManager
from app.models.customer import CustomerModel


class CustomerRepository:
    @property
    def collection(self) -> Collection:
        return MongoDBManager.get_db().customers

    def create(self, customer: CustomerModel) -> str:
        doc = customer.model_dump(by_alias=True, exclude={"id"}, exclude_none=True)
        result = self.collection.insert_one(doc)
        return str(result.inserted_id)

    def get_by_id(self, customer_id: str) -> Optional[CustomerModel]:
        doc = self.collection.find_one({"_id": ObjectId(customer_id)})
        if doc and "_id" in doc: doc["_id"] = str(doc["_id"])
        return CustomerModel(**doc) if doc else None

    def get_by_phone(self, phone: str) -> Optional[CustomerModel]:
        doc = self.collection.find_one({"phone": phone})
        if doc and "_id" in doc: doc["_id"] = str(doc["_id"])
        return CustomerModel(**doc) if doc else None

    def update(self, customer_id: str, updates: dict) -> bool:
        result = self.collection.update_one(
            {"_id": ObjectId(customer_id)},
            {"$set": updates}
        )
        return result.modified_count > 0

    def list(self, limit: int = 50, skip: int = 0, filters: Optional[dict] = None) -> List[CustomerModel]:
        cursor = self.collection.find(filters or {}).sort("createdAt", -1).skip(skip).limit(limit)
        return [CustomerModel(**{**doc, "_id": str(doc["_id"])}) for doc in cursor if doc]

    def count(self, filters: Optional[dict] = None) -> int:
        return self.collection.count_documents(filters or {})
