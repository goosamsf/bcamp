import sys
sys.path.insert(0, '.')

import json
import time
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage

from agents.graph.state import PacketAnalyzerState
from agents.tools.analysis_tools import rank_by_educational_value
from agents.prompts.summary_prompts import SUMMARY_AGENT_SYSTEM_PROMPT
from schemas.agent_schemas import FullAnalysisReport
from schemas.packet_schemas import PCAPStatistics, NetworkFlow, RawPacket
from schemas.analysis_schemas import ProtocolAnalysis, Anomaly
from schemas.education_schemas import EducationalContent, QuizQuestion
from config import settings


def _get_llm():
    if settings.llm_provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=settings.model_name, temperature=0.2, openai_api_key=settings.openai_api_key)
    else:
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model=settings.model_name, temperature=0.2, anthropic_api_key=settings.anthropic_api_key)


async def summary_agent_node(state: PacketAnalyzerState) -> dict:
    """Summary Agent: synthesizes all findings into the final FullAnalysisReport."""
    complexity = state.get("user_complexity_level", "beginner")

    trace_entry = {
        "sender_agent": "summary_agent",
        "recipient_agent": "orchestrator",
        "message_type": "task_result",
        "timestamp": time.time(),
        "summary": "",
        "payload": {},
        "confidence_score": 0.95,
    }

    try:
        # Parse all upstream outputs
        stats_data = json.loads(state.get("statistics_raw_json", "{}"))
        stats_dict = stats_data.get("statistics", {})
        flows_data = json.loads(state.get("flows_raw_json", '{"flows": []}'))
        anomalies_data = json.loads(state.get("anomalies_raw_json", '{"anomalies": []}'))
        protocols_data = json.loads(state.get("protocol_analysis_json", "[]"))
        edu_data = json.loads(state.get("educational_content_json", "[]"))
        pcap_data = json.loads(state.get("pcap_raw_json", '{"packets": []}'))

        # Build Pydantic objects
        pcap_stats = PCAPStatistics(**stats_dict) if stats_dict else PCAPStatistics()

        protocol_analyses = []
        for pd in protocols_data:
            try:
                protocol_analyses.append(ProtocolAnalysis(**pd))
            except Exception:
                pass

        anomalies = []
        for a in anomalies_data.get("anomalies", []):
            try:
                anomalies.append(Anomaly(**a))
            except Exception:
                pass

        educational_contents = []
        all_quiz_questions = []
        for ed in edu_data:
            try:
                ec = EducationalContent(**ed)
                educational_contents.append(ec)
                all_quiz_questions.extend(ec.quiz_questions)
            except Exception:
                pass

        # Rank educational value and get learning moments
        rank_context = json.dumps({
            "protocols": [p.protocol_name for p in protocol_analyses],
            "anomalies": [a.model_dump() for a in anomalies],
        })
        rank_result_str = rank_by_educational_value.invoke({"context_json": rank_context})
        rank_result = json.loads(rank_result_str)
        top_learning_moments = rank_result.get("top_learning_moments", [])

        # Generate narrative summary with LLM
        summary_prompt = f"""Write a concise narrative summary (3-4 sentences) of this network capture at {complexity} level.

Statistics:
- Total packets: {pcap_stats.total_packets}
- Duration: {pcap_stats.capture_duration_seconds}s
- Protocols found: {', '.join([p.protocol_name for p in protocol_analyses[:6]])}
- Anomalies detected: {len(anomalies)}

Top observations:
{chr(10).join(top_learning_moments)}

Write the summary so a {complexity} student can understand what happened in this capture.
Be specific about the data. Do not use markdown, just plain text."""

        llm = _get_llm()
        sys_prompt = SUMMARY_AGENT_SYSTEM_PROMPT.format(complexity_level=complexity)
        response = llm.invoke([
            SystemMessage(content=sys_prompt),
            HumanMessage(content=summary_prompt),
        ])
        overall_summary = response.content.strip()

        # Build network flows list (top 20)
        network_flows = []
        for f in flows_data.get("flows", [])[:20]:
            try:
                network_flows.append(NetworkFlow(**f))
            except Exception:
                pass

        # Build raw packets list (first 50)
        raw_packets = []
        for p in pcap_data.get("packets", [])[:50]:
            try:
                raw_packets.append(RawPacket(**p))
            except Exception:
                pass

        # Assemble FullAnalysisReport
        report = FullAnalysisReport(
            session_id=state["session_id"],
            file_name=state.get("file_name", "upload.pcap"),
            pcap_statistics=pcap_stats,
            detected_protocols=[p.protocol_name for p in protocol_analyses],
            protocol_analyses=protocol_analyses,
            anomalies=anomalies,
            educational_contents=educational_contents,
            top_learning_moments=top_learning_moments,
            overall_summary=overall_summary,
            agent_execution_trace=state.get("agent_trace", []),
            quiz_questions=all_quiz_questions,
            network_flows=network_flows,
            raw_packets=raw_packets,
            is_complete=True,
        )

        trace_entry["summary"] = f"Final report assembled: {pcap_stats.total_packets} packets, {len(protocol_analyses)} protocols, {len(educational_contents)} educational sections"

        msg = AIMessage(content=f"[Summary Agent] Analysis complete. Report covers {pcap_stats.total_packets} packets across {len(protocol_analyses)} protocols with {len(all_quiz_questions)} quiz questions.")

        return {
            "final_report_json": report.model_dump_json(),
            "is_complete": True,
            "agent_statuses": {**state.get("agent_statuses", {}), "summary_agent": "complete"},
            "current_agent": "summary_agent",
            "messages": [msg],
            "agent_trace": state.get("agent_trace", []) + [trace_entry],
        }

    except Exception as e:
        trace_entry["message_type"] = "error"
        trace_entry["summary"] = f"Error: {e}"
        return {
            "error_message": str(e),
            "is_complete": False,
            "agent_statuses": {**state.get("agent_statuses", {}), "summary_agent": "failed"},
            "agent_trace": state.get("agent_trace", []) + [trace_entry],
            "current_agent": "summary_agent",
        }
