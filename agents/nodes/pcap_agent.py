import sys
sys.path.insert(0, '.')

import json
import time
from langchain_core.messages import AIMessage

from agents.graph.state import PacketAnalyzerState
from agents.tools.pcap_tools import parse_pcap_file, extract_flows, compute_statistics, detect_packet_anomalies
from agents.prompts.pcap_prompts import PCAP_AGENT_SYSTEM_PROMPT
from config import settings


def _get_llm():
    if settings.llm_provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=settings.model_name, temperature=0, openai_api_key=settings.openai_api_key)
    else:
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model=settings.model_name, temperature=0, anthropic_api_key=settings.anthropic_api_key)


async def pcap_agent_node(state: PacketAnalyzerState) -> dict:
    """PCAP Parsing Agent: parses PCAP file, extracts flows, statistics, and anomalies."""
    file_path = state["file_path"]
    session_id = state["session_id"]

    trace_entry = {
        "sender_agent": "pcap_agent",
        "recipient_agent": "orchestrator",
        "message_type": "task_result",
        "timestamp": time.time(),
        "summary": f"Parsing PCAP file: {file_path}",
        "payload": {},
        "confidence_score": 1.0,
    }

    try:
        # Step 1: Parse PCAP file
        pcap_result_str = parse_pcap_file.invoke({"file_path": file_path})
        pcap_result = json.loads(pcap_result_str)

        if pcap_result.get("status") == "error":
            trace_entry["message_type"] = "error"
            trace_entry["summary"] = f"PCAP parse failed: {pcap_result.get('error')}"
            return {
                "error_message": f"PCAP parse error: {pcap_result.get('error')}",
                "agent_statuses": {**state.get("agent_statuses", {}), "pcap_agent": "failed"},
                "agent_trace": state.get("agent_trace", []) + [trace_entry],
                "current_agent": "pcap_agent",
            }

        total_packets = pcap_result.get("total_packets", 0)

        # Step 2: Extract flows
        flows_result_str = extract_flows.invoke({"packets_json": pcap_result_str})

        # Step 3: Compute statistics
        stats_result_str = compute_statistics.invoke({"packets_json": pcap_result_str})

        # Step 4: Detect anomalies
        anomalies_result_str = detect_packet_anomalies.invoke({"packets_json": pcap_result_str})

        # Trim packets list to avoid state bloat (keep first 200 for downstream agents)
        pcap_trimmed = pcap_result.copy()
        pcap_trimmed["packets"] = pcap_result.get("packets", [])[:200]
        pcap_trimmed_str = json.dumps(pcap_trimmed)

        stats_data = json.loads(stats_result_str)
        protocols_found = list(stats_data.get("statistics", {}).get("protocol_distribution", {}).keys())
        anomaly_count = json.loads(anomalies_result_str).get("total_anomalies", 0)

        trace_entry["summary"] = (
            f"Parsed {total_packets} packets, {json.loads(flows_result_str).get('total_flows', 0)} flows, "
            f"protocols: {protocols_found[:5]}, anomalies: {anomaly_count}"
        )
        trace_entry["payload"] = {"total_packets": total_packets, "protocols": protocols_found}

        msg = AIMessage(content=f"[PCAP Agent] Parsed {total_packets} packets. Protocols detected: {', '.join(protocols_found[:8])}. Anomalies: {anomaly_count}.")

        return {
            "pcap_raw_json": pcap_trimmed_str,
            "flows_raw_json": flows_result_str,
            "statistics_raw_json": stats_result_str,
            "anomalies_raw_json": anomalies_result_str,
            "agent_statuses": {**state.get("agent_statuses", {}), "pcap_agent": "complete"},
            "current_agent": "pcap_agent",
            "messages": [msg],
            "agent_trace": state.get("agent_trace", []) + [trace_entry],
            "retry_count": 0,
        }

    except Exception as e:
        trace_entry["message_type"] = "error"
        trace_entry["summary"] = f"Unexpected error: {e}"
        return {
            "error_message": str(e),
            "agent_statuses": {**state.get("agent_statuses", {}), "pcap_agent": "failed"},
            "agent_trace": state.get("agent_trace", []) + [trace_entry],
            "current_agent": "pcap_agent",
        }
