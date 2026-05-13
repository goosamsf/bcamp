from pydantic import BaseModel, Field
from typing import Optional, List
from .packet_schemas import OSILayer


class Anomaly(BaseModel):
    anomaly_type: str
    severity: str = "low"  # "low", "medium", "high"
    affected_packets: List[int] = Field(default_factory=list)
    description: str = ""
    educational_note: str = ""


class ProtocolAnalysis(BaseModel):
    protocol_name: str
    protocol_version: Optional[str] = None
    osi_layer: OSILayer = OSILayer.UNKNOWN
    rfc_reference: Optional[str] = None
    packet_count: int = 0
    percentage_of_traffic: float = 0.0
    key_observations: List[str] = Field(default_factory=list)
    rag_retrieved_context: List[str] = Field(default_factory=list)
    handshake_detected: Optional[bool] = None
    handshake_type: Optional[str] = None
    common_ports: List[int] = Field(default_factory=list)
    description: str = ""
