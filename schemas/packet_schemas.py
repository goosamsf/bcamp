from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class OSILayer(str, Enum):
    LAYER_2_DATALINK = "L2_DataLink"
    LAYER_3_NETWORK = "L3_Network"
    LAYER_4_TRANSPORT = "L4_Transport"
    LAYER_7_APPLICATION = "L7_Application"
    UNKNOWN = "Unknown"


class TCPFlags(BaseModel):
    syn: bool = False
    ack: bool = False
    fin: bool = False
    rst: bool = False
    psh: bool = False
    urg: bool = False

    def to_str(self) -> str:
        flags = []
        if self.syn:
            flags.append("SYN")
        if self.ack:
            flags.append("ACK")
        if self.fin:
            flags.append("FIN")
        if self.rst:
            flags.append("RST")
        if self.psh:
            flags.append("PSH")
        if self.urg:
            flags.append("URG")
        return "+".join(flags) if flags else "NONE"


class RawPacket(BaseModel):
    packet_index: int
    timestamp: float
    src_ip: Optional[str] = None
    dst_ip: Optional[str] = None
    src_mac: Optional[str] = None
    dst_mac: Optional[str] = None
    src_port: Optional[int] = None
    dst_port: Optional[int] = None
    protocol: str = "Unknown"
    transport: Optional[str] = None  # "TCP", "UDP", "ICMP", etc.
    length: int = 0
    ttl: Optional[int] = None
    tcp_flags: Optional[TCPFlags] = None
    payload_size: int = 0
    osi_layer: OSILayer = OSILayer.UNKNOWN
    raw_summary: str = ""


class NetworkFlow(BaseModel):
    flow_id: str
    src_ip: str
    dst_ip: str
    src_port: Optional[int] = None
    dst_port: Optional[int] = None
    protocol: str
    packet_count: int = 0
    total_bytes: int = 0
    start_time: float = 0.0
    end_time: float = 0.0
    duration_ms: float = 0.0


class PCAPStatistics(BaseModel):
    total_packets: int = 0
    total_bytes: int = 0
    capture_duration_seconds: float = 0.0
    unique_src_ips: List[str] = Field(default_factory=list)
    unique_dst_ips: List[str] = Field(default_factory=list)
    protocol_distribution: dict = Field(default_factory=dict)
    top_talkers: List[dict] = Field(default_factory=list)
    avg_packet_size: float = 0.0
    packets_per_second: float = 0.0
    tcp_count: int = 0
    udp_count: int = 0
    icmp_count: int = 0
    other_count: int = 0
