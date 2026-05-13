import sys
sys.path.insert(0, '.')

import json
import hashlib
from typing import Any
from langchain_core.tools import tool

from schemas.packet_schemas import (
    RawPacket, NetworkFlow, PCAPStatistics, OSILayer, TCPFlags,
)
from schemas.analysis_schemas import Anomaly


def _scapy_to_raw_packet(pkt: Any, index: int) -> RawPacket:
    """Convert a Scapy packet to RawPacket schema."""
    try:
        from scapy.all import IP, TCP, UDP, ICMP, ARP, Ether, IPv6

        src_ip = dst_ip = src_mac = dst_mac = None
        src_port = dst_port = ttl = None
        protocol = "Unknown"
        transport = None
        tcp_flags_obj = None
        osi_layer = OSILayer.UNKNOWN
        length = len(pkt)
        payload_size = 0

        if pkt.haslayer(Ether):
            src_mac = pkt[Ether].src
            dst_mac = pkt[Ether].dst
            osi_layer = OSILayer.LAYER_2_DATALINK

        if pkt.haslayer(ARP):
            src_ip = pkt[ARP].psrc
            dst_ip = pkt[ARP].pdst
            protocol = "ARP"
            osi_layer = OSILayer.LAYER_3_NETWORK

        elif pkt.haslayer(IP):
            src_ip = pkt[IP].src
            dst_ip = pkt[IP].dst
            ttl = pkt[IP].ttl
            osi_layer = OSILayer.LAYER_3_NETWORK

            if pkt.haslayer(TCP):
                transport = "TCP"
                src_port = pkt[TCP].sport
                dst_port = pkt[TCP].dport
                flags = pkt[TCP].flags
                tcp_flags_obj = TCPFlags(
                    syn=bool(flags & 0x02),
                    ack=bool(flags & 0x10),
                    fin=bool(flags & 0x01),
                    rst=bool(flags & 0x04),
                    psh=bool(flags & 0x08),
                    urg=bool(flags & 0x20),
                )
                protocol = _guess_app_protocol(src_port, dst_port, "tcp")
                osi_layer = OSILayer.LAYER_4_TRANSPORT
                payload_size = len(pkt[TCP].payload) if pkt[TCP].payload else 0

            elif pkt.haslayer(UDP):
                transport = "UDP"
                src_port = pkt[UDP].sport
                dst_port = pkt[UDP].dport
                protocol = _guess_app_protocol(src_port, dst_port, "udp")
                osi_layer = OSILayer.LAYER_4_TRANSPORT
                payload_size = len(pkt[UDP].payload) if pkt[UDP].payload else 0

            elif pkt.haslayer(ICMP):
                transport = "ICMP"
                protocol = "ICMP"
                osi_layer = OSILayer.LAYER_3_NETWORK

            else:
                transport = str(pkt[IP].proto)
                protocol = f"IP-{pkt[IP].proto}"

        elif pkt.haslayer(IPv6):
            src_ip = str(pkt[IPv6].src)
            dst_ip = str(pkt[IPv6].dst)
            protocol = "IPv6"
            osi_layer = OSILayer.LAYER_3_NETWORK

        return RawPacket(
            packet_index=index,
            timestamp=float(pkt.time),
            src_ip=src_ip,
            dst_ip=dst_ip,
            src_mac=src_mac,
            dst_mac=dst_mac,
            src_port=src_port,
            dst_port=dst_port,
            protocol=protocol,
            transport=transport,
            length=length,
            ttl=ttl,
            tcp_flags=tcp_flags_obj,
            payload_size=payload_size,
            osi_layer=osi_layer,
            raw_summary=pkt.summary(),
        )
    except Exception as e:
        return RawPacket(
            packet_index=index,
            timestamp=0.0,
            protocol="Unknown",
            length=0,
            osi_layer=OSILayer.UNKNOWN,
            raw_summary=f"Parse error: {e}",
        )


def _guess_app_protocol(src_port: int, dst_port: int, transport: str) -> str:
    port_map = {
        ("tcp", 80): "HTTP",
        ("tcp", 443): "HTTPS",
        ("tcp", 22): "SSH",
        ("tcp", 21): "FTP",
        ("tcp", 25): "SMTP",
        ("tcp", 110): "POP3",
        ("tcp", 143): "IMAP",
        ("tcp", 3306): "MySQL",
        ("tcp", 5432): "PostgreSQL",
        ("tcp", 6379): "Redis",
        ("tcp", 8080): "HTTP-Alt",
        ("tcp", 8443): "HTTPS-Alt",
        ("tcp", 23): "Telnet",
        ("udp", 53): "DNS",
        ("udp", 67): "DHCP",
        ("udp", 68): "DHCP",
        ("udp", 123): "NTP",
        ("udp", 161): "SNMP",
        ("udp", 514): "Syslog",
        ("udp", 1194): "OpenVPN",
    }
    for port in [src_port, dst_port]:
        key = (transport, port)
        if key in port_map:
            return port_map[key]
    return f"TCP-{dst_port}" if transport == "tcp" else f"UDP-{dst_port}"


@tool
def parse_pcap_file(file_path: str) -> str:
    """Parse a PCAP file and extract structured packet data.
    Returns JSON with list of packets and basic statistics.
    Use this when you receive a PCAP file path and need to analyze its contents."""
    try:
        from scapy.all import rdpcap
        packets = rdpcap(file_path)

        raw_packets = []
        for i, pkt in enumerate(packets):
            raw_pkt = _scapy_to_raw_packet(pkt, i)
            raw_packets.append(raw_pkt.model_dump())

        result = {
            "status": "success",
            "total_packets": len(raw_packets),
            "file_path": file_path,
            "packets": raw_packets[:500],  # cap to avoid context overflow
        }
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


@tool
def extract_flows(packets_json: str) -> str:
    """Group packets into bidirectional network flows by 5-tuple (src_ip, dst_ip, src_port, dst_port, protocol).
    Returns list of NetworkFlow objects with statistics per conversation.
    Use after parse_pcap_file to understand network conversations."""
    try:
        data = json.loads(packets_json)
        packets = data.get("packets", [])

        flows: dict[str, dict] = {}

        for pkt in packets:
            src_ip = pkt.get("src_ip") or "?"
            dst_ip = pkt.get("dst_ip") or "?"
            src_port = pkt.get("src_port")
            dst_port = pkt.get("dst_port")
            protocol = pkt.get("protocol", "Unknown")
            ts = pkt.get("timestamp", 0)
            length = pkt.get("length", 0)

            # Normalize direction (smaller IP first for bidirectionality)
            key_parts = sorted([f"{src_ip}:{src_port}", f"{dst_ip}:{dst_port}"])
            flow_key = f"{key_parts[0]}-{key_parts[1]}-{protocol}"
            flow_id = hashlib.md5(flow_key.encode()).hexdigest()[:8]

            if flow_id not in flows:
                flows[flow_id] = {
                    "flow_id": flow_id,
                    "src_ip": src_ip,
                    "dst_ip": dst_ip,
                    "src_port": src_port,
                    "dst_port": dst_port,
                    "protocol": protocol,
                    "packet_count": 0,
                    "total_bytes": 0,
                    "start_time": ts,
                    "end_time": ts,
                }
            flows[flow_id]["packet_count"] += 1
            flows[flow_id]["total_bytes"] += length
            flows[flow_id]["end_time"] = max(flows[flow_id]["end_time"], ts)
            flows[flow_id]["start_time"] = min(flows[flow_id]["start_time"], ts)

        flow_list = []
        for f in flows.values():
            duration = (f["end_time"] - f["start_time"]) * 1000
            f["duration_ms"] = round(duration, 2)
            flow_list.append(f)

        flow_list.sort(key=lambda x: x["packet_count"], reverse=True)

        return json.dumps({
            "status": "success",
            "total_flows": len(flow_list),
            "flows": flow_list[:100],
        })
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


@tool
def compute_statistics(packets_json: str) -> str:
    """Compute aggregate statistics from parsed packets: total bytes, protocol distribution, top talkers.
    Returns PCAPStatistics as JSON.
    Use to summarize overall traffic characteristics of a PCAP file."""
    try:
        data = json.loads(packets_json)
        packets = data.get("packets", [])

        if not packets:
            return json.dumps({"status": "error", "error": "No packets provided"})

        timestamps = [p.get("timestamp", 0) for p in packets if p.get("timestamp")]
        total_bytes = sum(p.get("length", 0) for p in packets)
        src_ips = list(set(p["src_ip"] for p in packets if p.get("src_ip")))
        dst_ips = list(set(p["dst_ip"] for p in packets if p.get("dst_ip")))

        protocol_dist: dict[str, int] = {}
        ip_byte_count: dict[str, int] = {}
        for p in packets:
            proto = p.get("protocol", "Unknown")
            protocol_dist[proto] = protocol_dist.get(proto, 0) + 1
            for ip_key in ["src_ip", "dst_ip"]:
                ip = p.get(ip_key)
                if ip:
                    ip_byte_count[ip] = ip_byte_count.get(ip, 0) + p.get("length", 0)

        top_talkers = sorted(
            [{"ip": ip, "total_bytes": b} for ip, b in ip_byte_count.items()],
            key=lambda x: x["total_bytes"],
            reverse=True,
        )[:10]

        duration = max(timestamps) - min(timestamps) if len(timestamps) > 1 else 0
        tcp_count = protocol_dist.get("TCP", 0)
        udp_count = sum(v for k, v in protocol_dist.items() if "UDP" in k or k == "DNS")
        icmp_count = protocol_dist.get("ICMP", 0)

        stats = PCAPStatistics(
            total_packets=len(packets),
            total_bytes=total_bytes,
            capture_duration_seconds=round(duration, 3),
            unique_src_ips=src_ips[:50],
            unique_dst_ips=dst_ips[:50],
            protocol_distribution=protocol_dist,
            top_talkers=top_talkers,
            avg_packet_size=round(total_bytes / max(len(packets), 1), 2),
            packets_per_second=round(len(packets) / max(duration, 0.001), 2),
            tcp_count=tcp_count,
            udp_count=udp_count,
            icmp_count=icmp_count,
            other_count=len(packets) - tcp_count - udp_count - icmp_count,
        )

        return json.dumps({"status": "success", "statistics": stats.model_dump()})
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


@tool
def detect_packet_anomalies(packets_json: str) -> str:
    """Detect anomalous patterns in packets: port scans, SYN floods, ARP spoofing, malformed packets.
    Returns list of Anomaly objects with severity and educational notes.
    Use after parse_pcap_file to find security-relevant behaviors for educational discussion."""
    try:
        data = json.loads(packets_json)
        packets = data.get("packets", [])
        anomalies = []

        # Check for SYN flood: many SYN-only from same source to same dst port
        syn_packets: dict[str, list] = {}
        for p in packets:
            if p.get("tcp_flags") and p["tcp_flags"].get("syn") and not p["tcp_flags"].get("ack"):
                key = f"{p.get('src_ip')}->{p.get('dst_ip')}:{p.get('dst_port')}"
                syn_packets.setdefault(key, []).append(p["packet_index"])
        for key, indices in syn_packets.items():
            if len(indices) > 20:
                anomalies.append(Anomaly(
                    anomaly_type="syn_flood_candidate",
                    severity="high",
                    affected_packets=indices[:10],
                    description=f"High rate of SYN-only packets: {key} ({len(indices)} SYNs)",
                    educational_note="Many SYN packets without completion of 3-way handshake may indicate a SYN flood DoS attack or an aggressive port scanner.",
                ).model_dump())

        # Check for port scan: one src IP → many dst ports
        src_ports: dict[str, set] = {}
        for p in packets:
            src = p.get("src_ip")
            dst_port = p.get("dst_port")
            if src and dst_port:
                src_ports.setdefault(src, set()).add(dst_port)
        for src, ports in src_ports.items():
            if len(ports) > 15:
                anomalies.append(Anomaly(
                    anomaly_type="port_scan_candidate",
                    severity="medium",
                    affected_packets=[],
                    description=f"Source {src} contacted {len(ports)} different destination ports",
                    educational_note="Contacting many different ports from one source is a classic port scan signature — used to discover open services on a target.",
                ).model_dump())

        # Check for ARP conflicts: same IP with multiple MACs
        ip_mac: dict[str, set] = {}
        for p in packets:
            if p.get("protocol") == "ARP":
                ip = p.get("src_ip")
                mac = p.get("src_mac")
                if ip and mac:
                    ip_mac.setdefault(ip, set()).add(mac)
        for ip, macs in ip_mac.items():
            if len(macs) > 1:
                anomalies.append(Anomaly(
                    anomaly_type="arp_conflict",
                    severity="high",
                    affected_packets=[],
                    description=f"IP {ip} seen with {len(macs)} different MAC addresses: {list(macs)}",
                    educational_note="Multiple MAC addresses for the same IP can indicate ARP spoofing — a man-in-the-middle attack technique.",
                ).model_dump())

        return json.dumps({
            "status": "success",
            "total_anomalies": len(anomalies),
            "anomalies": anomalies,
        })
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})
