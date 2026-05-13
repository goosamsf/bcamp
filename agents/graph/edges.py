import sys
sys.path.insert(0, '.')

from agents.graph.state import PacketAnalyzerState


def route_from_orchestrator(state: PacketAnalyzerState) -> str:
    """Conditional edge: decide which agent to route to from orchestrator."""
    current = state.get("current_agent", "orchestrator")
    error = state.get("error_message")
    is_complete = state.get("is_complete", False)

    if is_complete or (error and current == "orchestrator"):
        return "__end__"

    # Route based on what has been completed
    if state.get("educational_content_json"):
        return "summary_agent"
    elif state.get("protocol_analysis_json"):
        return "education_agent"
    elif state.get("pcap_raw_json"):
        return "protocol_agent"
    else:
        return "pcap_agent"


def route_after_pcap(state: PacketAnalyzerState) -> str:
    """After PCAP agent, always go back to orchestrator for validation."""
    return "orchestrator"


def route_after_protocol(state: PacketAnalyzerState) -> str:
    """After protocol agent, always go back to orchestrator."""
    return "orchestrator"


def route_after_education(state: PacketAnalyzerState) -> str:
    """After education agent, always go back to orchestrator."""
    return "orchestrator"


def route_after_summary(state: PacketAnalyzerState) -> str:
    """After summary agent, analysis is complete."""
    return "__end__"
