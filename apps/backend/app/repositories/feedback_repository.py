from typing import List, Optional

from bson.objectid import ObjectId
from pymongo.collection import Collection

from app.db.mongodb import MongoDBManager
from app.models.feedback import FeedbackModel


class FeedbackRepository:
    @property
    def collection(self) -> Collection:
        return MongoDBManager.get_db().feedback

    def create(self, feedback: FeedbackModel) -> str:
        doc = feedback.model_dump(by_alias=True, exclude={"id"}, exclude_none=True)
        result = self.collection.insert_one(doc)
        return str(result.inserted_id)

    def get_by_id(self, feedback_id: str) -> Optional[FeedbackModel]:
        doc = self.collection.find_one({"_id": ObjectId(feedback_id)})
        if doc and "_id" in doc: doc["_id"] = str(doc["_id"])
        return FeedbackModel(**doc) if doc else None

    def list_by_call_id(self, call_id: str) -> List[FeedbackModel]:
        cursor = self.collection.find({"callId": call_id}).sort("createdAt", -1)
        return [FeedbackModel(**{**doc, "_id": str(doc["_id"])}) for doc in cursor if doc]

    def list(self, limit: int = 50, skip: int = 0, filters: Optional[dict] = None) -> List[FeedbackModel]:
        cursor = self.collection.find(filters or {}).sort("createdAt", -1).skip(skip).limit(limit)
        return [FeedbackModel(**{**doc, "_id": str(doc["_id"])}) for doc in cursor if doc]

    def count(self, filters: Optional[dict] = None) -> int:
        return self.collection.count_documents(filters or {})
