from typing import Any, Dict, Optional

from pydantic import BaseModel


class RetellCreateCallRequest(BaseModel):
    from_number: str
    to_number: str
    override_agent_id: Optional[str] = None
    retell_llm_dynamic_variables: Optional[Dict[str, Any]] = None

class RetellCallResponse(BaseModel):
    call_id: str
    call_status: str
    agent_id: str
    from_number: str
    to_number: str
