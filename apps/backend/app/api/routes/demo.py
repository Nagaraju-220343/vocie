from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import asyncio
import logging
from typing import Dict, Any

from app.models.call import CallModel
from app.repositories.call_repository import CallRepository
from app.realtime.socket import publisher

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/demo", tags=["Demo"])

class DemoStartResponse(BaseModel):
    demoCallId: str
    scenario: str
    status: str

async def run_demo_scenario(call_id: str, scenario: str) -> None:
    # Simulate a realistic call progression with delays
    logger.info(f"Starting demo scenario {scenario} for call {call_id}")
    call_repo = CallRepository()
    
    # 1. Start
    await asyncio.sleep(1)
    call_repo.update(call_id, {"status": "IN_PROGRESS"})
    await publisher.publish("call.started", call_id, 1, {"status": "IN_PROGRESS"})
    
    # 2. Transcripts
    if scenario == "FRENCH_ORDER":
        await asyncio.sleep(2)
        await publisher.publish("transcript.updated", call_id, 2, {"role": "user", "content": "Bonjour, je voudrais deux pizzas margherita et une salade."})
        
        await asyncio.sleep(2)
        await publisher.publish("transcript.updated", call_id, 3, {"role": "agent", "content": "Bien sûr. Et pour l'adresse ?"})
        
        await asyncio.sleep(2)
        await publisher.publish("transcript.updated", call_id, 4, {"role": "user", "content": "12 Rue de Paris, 75001. Pierre Dupont. 06 12 34 56 78."})
        
        # 3. Intent & Order
        await asyncio.sleep(1)
        call_repo.update(call_id, {"intent": "ORDER", "language": "fr"})
        await publisher.publish("call.intent.updated", call_id, 5, {"intent": "ORDER", "language": "fr"})
        
        await asyncio.sleep(1)
        order_payload = {
            "customer": {"name": "Pierre Dupont", "phone": "+33612345678"},
            "order": {
                "items": [
                    {"name": "Pizza Margherita", "quantity": 2},
                    {"name": "Salade", "quantity": 1}
                ],
                "address": "12 Rue de Paris, 75001"
            }
        }
        await publisher.publish("order.updated", call_id, 6, order_payload)
        
        # 4. End
        await asyncio.sleep(1)
        call_repo.update(call_id, {"status": "COMPLETED"})
        await publisher.publish("call.ended", call_id, 7, {"status": "COMPLETED"})
        
    elif scenario == "FRENCH_FAQ":
        await asyncio.sleep(2)
        await publisher.publish("transcript.updated", call_id, 2, {"role": "user", "content": "Quels sont vos horaires ?"})
        
        await asyncio.sleep(2)
        call_repo.update(call_id, {"intent": "FAQ", "language": "fr"})
        await publisher.publish("call.intent.updated", call_id, 3, {"intent": "FAQ"})
        
        await asyncio.sleep(1)
        await publisher.publish("transcript.updated", call_id, 4, {"role": "agent", "content": "Nous sommes ouverts de 11h à 23h."})
        
        await asyncio.sleep(1)
        call_repo.update(call_id, {"status": "COMPLETED"})
        await publisher.publish("call.ended", call_id, 5, {"status": "COMPLETED"})

    elif scenario == "ENGLISH_ORDER":
        # Similar to French order
        await asyncio.sleep(2)
        await publisher.publish("transcript.updated", call_id, 2, {"role": "user", "content": "I want a burger."})
        await asyncio.sleep(1)
        call_repo.update(call_id, {"intent": "ORDER", "language": "en"})
        await publisher.publish("call.intent.updated", call_id, 3, {"intent": "ORDER"})
        await asyncio.sleep(1)
        call_repo.update(call_id, {"status": "COMPLETED"})
        await publisher.publish("call.ended", call_id, 4, {"status": "COMPLETED"})
        
    elif scenario == "ESCALATION":
        await asyncio.sleep(2)
        await publisher.publish("transcript.updated", call_id, 2, {"role": "user", "content": "Je voudrais parler à quelqu'un."})
        
        await asyncio.sleep(1)
        call_repo.update(call_id, {"status": "ESCALATED", "escalationReason": "CUSTOMER_REQUEST"})
        await publisher.publish("call.escalated", call_id, 3, {"status": "ESCALATED", "reason": "CUSTOMER_REQUEST"})

@router.post("/scenarios/{scenario}/start", response_model=DemoStartResponse)
def start_demo_scenario(scenario: str, background_tasks: BackgroundTasks) -> DemoStartResponse:
    valid_scenarios = ["FRENCH_ORDER", "FRENCH_FAQ", "ENGLISH_ORDER", "ESCALATION"]
    if scenario not in valid_scenarios:
        raise HTTPException(status_code=400, detail="Invalid scenario")
        
    # Create an initial demo call
    call_repo = CallRepository()
    
    # Check if a model accepts required fields
    import datetime
    now = datetime.datetime.now(datetime.timezone.utc)
    demo_call = CallModel(
        providerCallId=f"demo_{scenario}_{int(now.timestamp())}",
        status="PENDING",
        direction="INBOUND",
        transcriptMessages=[],
        fromNumber="demo",
        toNumber="demo",
        language="en" if "ENGLISH" in scenario else "fr",
        intent="UNKNOWN",
    )
    
    call_id = call_repo.create(demo_call)
    
    # Run the demo steps in background
    background_tasks.add_task(run_demo_scenario, call_id, scenario)
    
    return DemoStartResponse(demoCallId=call_id, scenario=scenario, status="PENDING")
