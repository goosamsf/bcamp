import sys
sys.path.insert(0, '.')

from typing import TypedDict, List, Optional, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class PacketAnalyzerState(TypedDict):
    # Session info
    session_id: str
    file_path: str
    file_name: str
    user_complexity_level: str  # "beginner" | "intermediate" | "advanced"

    # A2A message history (append-only via LangGraph)
    messages: Annotated[List[BaseMessage], add_messages]

    # Agent status tracking
    agent_statuses: dict

    # PCAP Agent outputs (raw JSON strings to avoid heavy serialization)
    pcap_raw_json: Optional[str]       # parse_pcap_file output
    flows_raw_json: Optional[str]      # extract_flows output
    statistics_raw_json: Optional[str] # compute_statistics output
    anomalies_raw_json: Optional[str]  # detect_packet_anomalies output

    # Protocol Agent outputs
    protocol_analysis_json: Optional[str]  # list of ProtocolAnalysis as JSON

    # Education Agent outputs
    educational_content_json: Optional[str]  # list of EducationalContent as JSON

    # Final output
    final_report_json: Optional[str]  # FullAnalysisReport as JSON

    # Control flow
    current_agent: Optional[str]
    error_message: Optional[str]
    retry_count: int
    is_complete: bool
    agent_trace: List[dict]  # list of AgentMessage dicts for A2A history
