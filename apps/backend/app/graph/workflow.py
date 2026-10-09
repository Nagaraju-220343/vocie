import logging
from typing import Dict, Any

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.mongodb import MongoDBSaver
from app.graph.state import CallState
from app.graph.nodes import update_call_state, update_transcript, update_order, validate_order, handle_escalation
from app.db.mongodb import MongoDBManager

logger = logging.getLogger(__name__)

from langgraph.graph.state import CompiledStateGraph

def build_call_graph(checkpointer=None) -> CompiledStateGraph:
    workflow = StateGraph(CallState)  # type: ignore
    
    # Add nodes
    workflow.add_node("update_call_state", update_call_state)
    workflow.add_node("update_transcript", update_transcript)
    workflow.add_node("update_order", update_order)
    workflow.add_node("validate_order", validate_order)
    workflow.add_node("handle_escalation", handle_escalation)
    
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

    return workflow.compile(checkpointer=checkpointer)

class LiveStateService:
    def __init__(self) -> None:
        self._graph: CompiledStateGraph | None = None
        
    def get_graph(self) -> CompiledStateGraph:
        if self._graph is None:
            # Get the MongoDBSaver only when requested (so MongoDBManager.client is initialized)
            if not MongoDBManager.client:
                MongoDBManager.connect()
            checkpointer = MongoDBSaver(MongoDBManager.client)
            self._graph = build_call_graph(checkpointer=checkpointer)
        return self._graph

    def process_event(self, call_id: str, state_update: dict, action: str) -> CallState:
        """
        Process a live state update using LangGraph with persistent MongoDB state.
        """
        graph = self.get_graph()
        thread_id = f"call:{call_id}"
        config = {"configurable": {"thread_id": thread_id}}
        
        # We merge _action into the payload so the router uses it
        state_update["_action"] = action
        
        # Ensure we always pass the call_id down if not in payload
        if "call_id" not in state_update:
            state_update["call_id"] = call_id
            
        new_state = graph.invoke(state_update, config)
        
        # Cleanup _action
        if "_action" in new_state:
            new_state.pop("_action")
            
        import typing
        return typing.cast(CallState, new_state)

live_state_service = LiveStateService()
