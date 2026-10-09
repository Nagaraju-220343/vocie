import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from app.services.escalation_service import EscalationService
from app.db.mongodb import MongoDBManager

async def test_escalation():
    MongoDBManager.connect()
    try:
        service = EscalationService()
        result = service.escalate_call(call_id="provider_12345", reason="test")
        print("Result:", result)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_escalation())
