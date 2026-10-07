from typing import List, Optional

from bson.objectid import ObjectId
from pymongo.collection import Collection

from app.db.mongodb import MongoDBManager
from app.models.call import CallModel


class CallRepository:
    @property
    def collection(self) -> Collection:
        return MongoDBManager.get_db().calls

    def create(self, call: CallModel) -> str:
        doc = call.model_dump(by_alias=True, exclude={"id"}, exclude_none=True)
        result = self.collection.insert_one(doc)
        return str(result.inserted_id)

    def get_by_id(self, call_id: str) -> Optional[CallModel]:
        doc = self.collection.find_one({"_id": ObjectId(call_id)})
        if doc and "_id" in doc: doc["_id"] = str(doc["_id"])
        return CallModel(**doc) if doc else None

    def get_by_provider_call_id(self, provider_call_id: str) -> Optional[CallModel]:
        doc = self.collection.find_one({"providerCallId": provider_call_id})
        if doc and "_id" in doc: doc["_id"] = str(doc["_id"])
        return CallModel(**doc) if doc else None

    def update(self, call_id: str, updates: dict) -> bool:
        result = self.collection.update_one(
            {"_id": ObjectId(call_id)},
            {"$set": updates}
        )
        return result.modified_count > 0

    def upsert_by_provider_call_id(self, provider_call_id: str, call: CallModel) -> str:
        doc = call.model_dump(by_alias=True, exclude={"id"}, exclude_none=True)
        result = self.collection.update_one(
            {"providerCallId": provider_call_id},
            {"$set": doc},
            upsert=True
        )
        if result.upserted_id:
            return str(result.upserted_id)
        
        # If not upserted, we need to return the ID of the matched document
        matched = self.collection.find_one({"providerCallId": provider_call_id})
        return str(matched["_id"]) if matched else ""

    def list(self, limit: int = 50, skip: int = 0, filters: Optional[dict] = None) -> List[CallModel]:
        cursor = self.collection.find(filters or {}).sort("createdAt", -1).skip(skip).limit(limit)
        return [CallModel(**{**doc, "_id": str(doc["_id"])}) for doc in cursor if doc]

    def count(self, filters: Optional[dict] = None) -> int:
        return self.collection.count_documents(filters or {})
