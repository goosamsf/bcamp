from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
import time

from .packet_schemas import PCAPStatistics, NetworkFlow, RawPacket
from .analysis_schemas import ProtocolAnalysis, Anomaly
from .education_schemas import EducationalContent, QuizQuestion


class AgentStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"


class AgentMessage(BaseModel):
    sender_agent: str
    recipient_agent: str
    message_type: str  # "task_result", "validation_request", "error", "info"
    payload: dict = Field(default_factory=dict)
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    timestamp: float = Field(default_factory=time.time)
    summary: str = ""


class FullAnalysisReport(BaseModel):
    session_id: str
    file_name: str
    analysis_timestamp: float = Field(default_factory=time.time)
    pcap_statistics: Optional[PCAPStatistics] = None
    detected_protocols: List[str] = Field(default_factory=list)
    protocol_analyses: List[ProtocolAnalysis] = Field(default_factory=list)
    anomalies: List[Anomaly] = Field(default_factory=list)
    educational_contents: List[EducationalContent] = Field(default_factory=list)
    top_learning_moments: List[str] = Field(default_factory=list)
    overall_summary: str = ""
    agent_execution_trace: List[AgentMessage] = Field(default_factory=list)
    quiz_questions: List[QuizQuestion] = Field(default_factory=list)
    network_flows: List[NetworkFlow] = Field(default_factory=list)
    raw_packets: List[RawPacket] = Field(default_factory=list)
    error: Optional[str] = None
    is_complete: bool = False
