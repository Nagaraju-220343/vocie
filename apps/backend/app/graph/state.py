from typing import TypedDict, List, Optional, Dict, Any

class CallState(TypedDict):
    call_id: str
    provider_call_id: str

    status: str
    language: str
    intent: str

    transcript: List[Dict[str, Any]]
    customer: Optional[Dict[str, Any]]
    order: Optional[Dict[str, Any]]

    order_validation_status: Optional[str]
    escalation: Optional[Dict[str, Any]]

    last_sequence: int
