import sys
sys.path.insert(0, '.')

import json
import time
from langchain_core.messages import AIMessage

from agents.graph.state import PacketAnalyzerState
from agents.tools.rag_tools import query_rag_knowledge, lookup_rfc_summary
from agents.tools.analysis_tools import identify_protocol_from_port, analyze_tcp_flags
from agents.prompts.protocol_prompts import PROTOCOL_AGENT_SYSTEM_PROMPT
from schemas.analysis_schemas import ProtocolAnalysis
from schemas.packet_schemas import OSILayer
from config import settings


LAYER_MAP = {
    "DNS": OSILayer.LAYER_7_APPLICATION,
    "HTTP": OSILayer.LAYER_7_APPLICATION,
    "HTTPS": OSILayer.LAYER_7_APPLICATION,
    "TLS": OSILayer.LAYER_7_APPLICATION,
    "SSH": OSILayer.LAYER_7_APPLICATION,
    "FTP": OSILayer.LAYER_7_APPLICATION,
    "SMTP": OSILayer.LAYER_7_APPLICATION,
    "IMAP": OSILayer.LAYER_7_APPLICATION,
    "NTP": OSILayer.LAYER_7_APPLICATION,
    "DHCP": OSILayer.LAYER_7_APPLICATION,
    "TCP": OSILayer.LAYER_4_TRANSPORT,
    "UDP": OSILayer.LAYER_4_TRANSPORT,
    "ICMP": OSILayer.LAYER_3_NETWORK,
    "ARP": OSILayer.LAYER_2_DATALINK,
    "IP": OSILayer.LAYER_3_NETWORK,
}


def _get_clean_protocol_name(proto: str) -> str:
    """Normalize protocol name for RAG queries."""
    for known in ["HTTP", "HTTPS", "DNS", "TLS", "TCP", "UDP", "ARP", "ICMP", "SSH", "FTP", "SMTP", "IMAP", "DHCP", "NTP"]:
        if known in proto.upper():
            return known
    return proto.split("-")[0]


async def protocol_agent_node(state: PacketAnalyzerState) -> dict:
    """Protocol Identification Agent: identifies protocols and retrieves RAG knowledge."""
    trace_entry = {
        "sender_agent": "protocol_agent",
        "recipient_agent": "orchestrator",
        "message_type": "task_result",
        "timestamp": time.time(),
        "summary": "",
        "payload": {},
        "confidence_score": 0.9,
    }

    try:
        stats_json = state.get("statistics_raw_json", "{}")
        stats_data = json.loads(stats_json)
        protocol_dist = stats_data.get("statistics", {}).get("protocol_distribution", {})
        total_packets = stats_data.get("statistics", {}).get("total_packets", 1)

        pcap_json = state.get("pcap_raw_json", '{"packets": []}')

        # Analyze TCP flags if TCP traffic present
        tcp_analysis = {}
        if "TCP" in protocol_dist or any("TCP" in k for k in protocol_dist):
            tcp_result_str = analyze_tcp_flags.invoke({"packets_json": pcap_json})
            tcp_analysis = json.loads(tcp_result_str).get("analysis", {})

        # Process each protocol
        protocol_analyses = []
        unique_protocols = set()
        for proto in protocol_dist:
            clean_proto = _get_clean_protocol_name(proto)
            unique_protocols.add(clean_proto)

        for proto in list(unique_protocols)[:8]:  # limit to top 8 protocols
            count = protocol_dist.get(proto, protocol_dist.get(f"TCP-{proto}", 0))
            percentage = round(count / max(total_packets, 1) * 100, 1)

            # RAG retrieval
            rag_result_str = query_rag_knowledge.invoke({
                "query": f"{proto} protocol purpose usage network",
                "category": "all",
            })
            rag_data = json.loads(rag_result_str)
            rag_context = [r["content"][:300] for r in rag_data.get("results", [])[:2]]

            # RFC lookup
            rfc_result_str = lookup_rfc_summary.invoke({"protocol_name": proto})
            rfc_data = json.loads(rfc_result_str)
            rfc_ref = rfc_data.get("rfc") if rfc_data.get("status") == "found" else None

            observations = [f"{count} packets ({percentage}% of traffic)"]
            if proto == "TCP" and tcp_analysis:
                obs_list = tcp_analysis.get("observations", [])
                observations.extend(obs_list[:2])
            if proto in ["TLS", "HTTPS"] and tcp_analysis.get("estimated_completed_handshakes", 0) > 0:
                observations.append(f"TLS handshake detected — encrypted traffic")

            analysis = ProtocolAnalysis(
                protocol_name=proto,
                osi_layer=LAYER_MAP.get(proto, OSILayer.UNKNOWN),
                rfc_reference=rfc_ref,
                packet_count=count,
                percentage_of_traffic=percentage,
                key_observations=observations,
                rag_retrieved_context=rag_context,
                handshake_detected=(proto == "TCP" and tcp_analysis.get("estimated_completed_handshakes", 0) > 0),
                handshake_type="tcp_3way" if proto == "TCP" else None,
            )
            protocol_analyses.append(analysis.model_dump())

        trace_entry["summary"] = f"Analyzed {len(protocol_analyses)} protocols: {list(unique_protocols)[:5]}"
        trace_entry["payload"] = {"protocols_analyzed": list(unique_protocols)}

        msg = AIMessage(content=f"[Protocol Agent] Identified and analyzed {len(protocol_analyses)} protocols: {', '.join(list(unique_protocols)[:6])}. RAG knowledge retrieved for each.")

        return {
            "protocol_analysis_json": json.dumps(protocol_analyses),
            "agent_statuses": {**state.get("agent_statuses", {}), "protocol_agent": "complete"},
            "current_agent": "protocol_agent",
            "messages": [msg],
            "agent_trace": state.get("agent_trace", []) + [trace_entry],
        }

    except Exception as e:
        trace_entry["message_type"] = "error"
        trace_entry["summary"] = f"Error: {e}"
        return {
            "error_message": str(e),
            "agent_statuses": {**state.get("agent_statuses", {}), "protocol_agent": "failed"},
            "agent_trace": state.get("agent_trace", []) + [trace_entry],
            "current_agent": "protocol_agent",
        }
