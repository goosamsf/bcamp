import sys
sys.path.insert(0, '.')

import json
import os
import time
from langchain_core.messages import AIMessage

from agents.graph.state import PacketAnalyzerState


async def orchestrator_agent_node(state: PacketAnalyzerState) -> dict:
    """Orchestrator Agent: validates state and decides routing. Uses ReAct reasoning."""
    current = state.get("current_agent", "start")
    error = state.get("error_message")

    trace_entry = {
        "sender_agent": "orchestrator",
        "recipient_agent": "next_agent",
        "message_type": "routing",
        "timestamp": time.time(),
        "summary": "",
        "payload": {},
        "confidence_score": 1.0,
    }

    # Initial validation: check file exists
    if current == "start" or current is None:
        file_path = state.get("file_path", "")
        if not os.path.exists(file_path):
            trace_entry["summary"] = f"File not found: {file_path}"
            msg = AIMessage(content=f"[Orchestrator] Error: PCAP file not found at {file_path}")
            return {
                "error_message": f"File not found: {file_path}",
                "is_complete": True,
                "current_agent": "orchestrator",
                "messages": [msg],
                "agent_trace": state.get("agent_trace", []) + [trace_entry],
            }
        trace_entry["summary"] = f"File validated: {file_path} → routing to pcap_agent"
        msg = AIMessage(content=f"[Orchestrator] File validated. Starting PCAP analysis pipeline...")

    elif current == "pcap_agent":
        # Validate PCAP agent output
        if error:
            trace_entry["summary"] = f"PCAP agent failed: {error}"
            msg = AIMessage(content=f"[Orchestrator] PCAP parsing failed: {error}")
            return {
                "is_complete": True,
                "current_agent": "orchestrator",
                "messages": [msg],
                "agent_trace": state.get("agent_trace", []) + [trace_entry],
            }

        pcap_json = state.get("pcap_raw_json", "{}")
        pcap_data = json.loads(pcap_json)
        total = pcap_data.get("total_packets", 0)
        if total == 0:
            trace_entry["summary"] = "No packets found in capture"
            msg = AIMessage(content="[Orchestrator] No packets found. Cannot continue analysis.")
            return {
                "error_message": "No packets found in capture file",
                "is_complete": True,
                "messages": [msg],
                "agent_trace": state.get("agent_trace", []) + [trace_entry],
            }

        trace_entry["summary"] = f"PCAP validated ({total} packets) → routing to protocol_agent"
        msg = AIMessage(content=f"[Orchestrator] PCAP analysis complete ({total} packets). Routing to Protocol Agent...")

    elif current == "protocol_agent":
        if error:
            trace_entry["summary"] = f"Protocol agent failed: {error}"
            msg = AIMessage(content=f"[Orchestrator] Protocol agent failed: {error}. Continuing to education with available data...")
            # Continue even on partial failure
        else:
            trace_entry["summary"] = "Protocol analysis validated → routing to education_agent"
            msg = AIMessage(content="[Orchestrator] Protocol analysis complete. Routing to Education Agent...")

    elif current == "education_agent":
        trace_entry["summary"] = "Education content generated → routing to summary_agent"
        msg = AIMessage(content="[Orchestrator] Educational content generated. Routing to Summary Agent...")

    else:
        trace_entry["summary"] = f"Unexpected state: current_agent={current}"
        msg = AIMessage(content=f"[Orchestrator] Unexpected state. Attempting recovery...")

    return {
        "current_agent": "orchestrator",
        "messages": [msg],
        "agent_trace": state.get("agent_trace", []) + [trace_entry],
        "error_message": None,  # clear error for retry
    }
