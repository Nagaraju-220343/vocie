from typing import List, Optional

from bson.objectid import ObjectId
from pymongo.collection import Collection

from app.db.mongodb import MongoDBManager
from app.models.faq import FaqModel


class FaqRepository:
    @property
    def collection(self) -> Collection:
        return MongoDBManager.get_db().faqs

    def create(self, faq: FaqModel) -> str:
        doc = faq.model_dump(by_alias=True, exclude={"id"}, exclude_none=True)
        result = self.collection.insert_one(doc)
        return str(result.inserted_id)

    def get_by_id(self, faq_id: str) -> Optional[FaqModel]:
        doc = self.collection.find_one({"_id": ObjectId(faq_id)})
        if doc and "_id" in doc: doc["_id"] = str(doc["_id"])
        return FaqModel(**doc) if doc else None

    def update(self, faq_id: str, updates: dict) -> bool:
        result = self.collection.update_one(
            {"_id": ObjectId(faq_id)},
            {"$set": updates}
        )
        return result.modified_count > 0

    def delete(self, faq_id: str) -> bool:
        result = self.collection.delete_one({"_id": ObjectId(faq_id)})
        return result.deleted_count > 0

    def list(self, limit: int = 50, skip: int = 0, filters: Optional[dict] = None) -> List[FaqModel]:
        cursor = self.collection.find(filters or {}).sort("updatedAt", -1).skip(skip).limit(limit)
        return [FaqModel(**{**doc, "_id": str(doc["_id"])}) for doc in cursor if doc]

    def count(self, filters: Optional[dict] = None) -> int:
        return self.collection.count_documents(filters or {})

    def get_active_faqs(self) -> List[FaqModel]:
        cursor = self.collection.find({"active": True}).sort("updatedAt", -1)
        return [FaqModel(**{**doc, "_id": str(doc["_id"])}) for doc in cursor if doc]
