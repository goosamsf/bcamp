import sys
sys.path.insert(0, '.')

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from agents.graph.state import PacketAnalyzerState
from agents.graph.edges import (
    route_from_orchestrator,
    route_after_pcap,
    route_after_protocol,
    route_after_education,
    route_after_summary,
)
from agents.nodes.orchestrator_agent import orchestrator_agent_node
from agents.nodes.pcap_agent import pcap_agent_node
from agents.nodes.protocol_agent import protocol_agent_node
from agents.nodes.education_agent import education_agent_node
from agents.nodes.summary_agent import summary_agent_node


_compiled_graph = None
_checkpointer = None


def build_graph():
    """Build and compile the LangGraph StateGraph for the packet analyzer."""
    workflow = StateGraph(PacketAnalyzerState)

    # Add agent nodes
    workflow.add_node("orchestrator", orchestrator_agent_node)
    workflow.add_node("pcap_agent", pcap_agent_node)
    workflow.add_node("protocol_agent", protocol_agent_node)
    workflow.add_node("education_agent", education_agent_node)
    workflow.add_node("summary_agent", summary_agent_node)

    # Entry point
    workflow.add_edge(START, "orchestrator")

    # Orchestrator decides routing
    workflow.add_conditional_edges(
        "orchestrator",
        route_from_orchestrator,
        {
            "pcap_agent": "pcap_agent",
            "protocol_agent": "protocol_agent",
            "education_agent": "education_agent",
            "summary_agent": "summary_agent",
            "__end__": END,
        },
    )

    # Each agent returns to orchestrator for validation
    workflow.add_edge("pcap_agent", "orchestrator")
    workflow.add_edge("protocol_agent", "orchestrator")
    workflow.add_edge("education_agent", "orchestrator")

    # Summary agent terminates the flow
    workflow.add_edge("summary_agent", END)

    checkpointer = MemorySaver()
    compiled = workflow.compile(checkpointer=checkpointer)

    return compiled, checkpointer


def get_graph():
    """Get or build the compiled graph (singleton pattern)."""
    global _compiled_graph, _checkpointer

    if _compiled_graph is None:
        _compiled_graph, _checkpointer = build_graph()

    return _compiled_graph, _checkpointer


def reset_graph():
    """Reset the compiled graph (useful for testing)."""
    global _compiled_graph, _checkpointer
    _compiled_graph = None
    _checkpointer = None
