import logging
from typing import Dict, Any

from langgraph.graph import StateGraph, START, END
from app.graph.state import CallState
from app.graph.nodes import update_call_state, update_transcript, update_order, validate_order, handle_escalation

logger = logging.getLogger(__name__)

from langgraph.graph.state import CompiledStateGraph

def build_call_graph() -> CompiledStateGraph:
    workflow = StateGraph(CallState)  # type: ignore
    
    # Add nodes
    workflow.add_node("update_call_state", update_call_state)
    workflow.add_node("update_transcript", update_transcript)
    workflow.add_node("update_order", update_order)
    workflow.add_node("validate_order", validate_order)
    workflow.add_node("handle_escalation", handle_escalation)
    
    # Add edges - in a real complex graph these would be conditional
    # For this simple prototype live state, the workflow just processes updates 
    # directly as requested, so we can define simple routing or just single executions.
    # We'll use conditional edges from START based on an 'action' injected before calling invoke.

    # To avoid modifying CallState just for routing, we could just use the graph to enforce constraints.
    # Let's keep it extremely simple.
    workflow.add_conditional_edges(
        START,
        lambda x: x.get("_action", "update_call_state"),
        {
            "update_call_state": "update_call_state",
            "update_transcript": "update_transcript",
            "update_order": "update_order",
            "handle_escalation": "handle_escalation"
        }
    )
    
    workflow.add_edge("update_order", "validate_order")
    
    workflow.add_edge("update_call_state", END)
    workflow.add_edge("update_transcript", END)
    workflow.add_edge("validate_order", END)
    workflow.add_edge("handle_escalation", END)

    return workflow.compile()

# Global graph instance
call_graph = build_call_graph()

class LiveStateService:
    def __init__(self) -> None:
        self.graph = call_graph
        
    def process_event(self, state: CallState, action: str) -> CallState:
        """
        Process a live state update using LangGraph.
        In production, this would use LangGraph's checkpointer to load/save state.
        For the prototype, we pass the current hydrated state in, run the step, and get it out.
        """
        state["_action"] = action # type: ignore
        new_state = self.graph.invoke(state)
        new_state.pop("_action", None)
        # mypy requires explicit type casting from Any to CallState here
        import typing
        return typing.cast(CallState, new_state)
