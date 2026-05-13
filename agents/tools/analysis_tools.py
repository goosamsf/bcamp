import sys
sys.path.insert(0, '.')

import json
from langchain_core.tools import tool


PORT_PROTOCOL_MAP = {
    ("tcp", 20): "FTP-Data", ("tcp", 21): "FTP",
    ("tcp", 22): "SSH", ("tcp", 23): "Telnet",
    ("tcp", 25): "SMTP", ("tcp", 53): "DNS",
    ("tcp", 80): "HTTP", ("tcp", 110): "POP3",
    ("tcp", 143): "IMAP", ("tcp", 443): "HTTPS",
    ("tcp", 465): "SMTPS", ("tcp", 587): "SMTP-Submission",
    ("tcp", 993): "IMAPS", ("tcp", 995): "POP3S",
    ("tcp", 3306): "MySQL", ("tcp", 5432): "PostgreSQL",
    ("tcp", 6379): "Redis", ("tcp", 8080): "HTTP-Alt",
    ("tcp", 8443): "HTTPS-Alt", ("tcp", 27017): "MongoDB",
    ("udp", 53): "DNS", ("udp", 67): "DHCP-Server",
    ("udp", 68): "DHCP-Client", ("udp", 69): "TFTP",
    ("udp", 123): "NTP", ("udp", 161): "SNMP",
    ("udp", 162): "SNMP-Trap", ("udp", 514): "Syslog",
    ("udp", 1194): "OpenVPN", ("udp", 5353): "mDNS",
}


@tool
def identify_protocol_from_port(port: int, transport: str = "tcp") -> str:
    """Map a port number to its well-known application protocol.
    Args:
        port: Port number (0-65535)
        transport: 'tcp' or 'udp'
    Returns protocol name, common use cases, and security notes.
    Use to determine what application protocol is running on a given port."""
    transport_lower = transport.lower()
    protocol = PORT_PROTOCOL_MAP.get((transport_lower, port))

    if protocol:
        return json.dumps({
            "status": "found",
            "port": port,
            "transport": transport,
            "protocol": protocol,
            "is_well_known": port < 1024,
            "is_registered": 1024 <= port < 49152,
            "is_ephemeral": port >= 49152,
        })
    else:
        return json.dumps({
            "status": "unknown",
            "port": port,
            "transport": transport,
            "is_well_known": port < 1024,
            "is_registered": 1024 <= port < 49152,
            "is_ephemeral": port >= 49152,
            "note": f"Port {port}/{transport} not in well-known registry. May be application-specific or dynamic.",
        })


@tool
def analyze_tcp_flags(packets_json: str) -> str:
    """Analyze TCP flag patterns to identify handshakes, terminations, and anomalies.
    Detects: 3-way handshake sequences, graceful close (FIN), RST terminations, SYN scans.
    Args:
        packets_json: JSON string with 'packets' list from parse_pcap_file output
    Returns analysis of connection lifecycle events found in the capture."""
    try:
        data = json.loads(packets_json)
        packets = data.get("packets", [])

        tcp_packets = [p for p in packets if p.get("transport") == "TCP" and p.get("tcp_flags")]

        syn_only = [p for p in tcp_packets if p["tcp_flags"].get("syn") and not p["tcp_flags"].get("ack")]
        syn_ack = [p for p in tcp_packets if p["tcp_flags"].get("syn") and p["tcp_flags"].get("ack")]
        fin_packets = [p for p in tcp_packets if p["tcp_flags"].get("fin")]
        rst_packets = [p for p in tcp_packets if p["tcp_flags"].get("rst")]
        ack_only = [p for p in tcp_packets if p["tcp_flags"].get("ack") and not any([
            p["tcp_flags"].get("syn"), p["tcp_flags"].get("fin"),
            p["tcp_flags"].get("rst"), p["tcp_flags"].get("psh"),
        ])]

        handshakes_detected = len(syn_ack)
        completed_handshakes = min(len(syn_only), len(syn_ack))

        analysis = {
            "total_tcp_packets": len(tcp_packets),
            "syn_only_count": len(syn_only),
            "syn_ack_count": len(syn_ack),
            "fin_count": len(fin_packets),
            "rst_count": len(rst_packets),
            "ack_only_count": len(ack_only),
            "estimated_connections_initiated": len(syn_only),
            "estimated_connections_accepted": len(syn_ack),
            "estimated_completed_handshakes": completed_handshakes,
            "observations": [],
        }

        if len(syn_only) > len(syn_ack) * 2:
            analysis["observations"].append(
                "Many more SYN than SYN-ACK: possible port scan, SYN flood, or many refused connections"
            )
        if completed_handshakes > 0:
            analysis["observations"].append(
                f"Detected ~{completed_handshakes} TCP connection establishment(s) (3-way handshake)"
            )
        if len(fin_packets) > 0:
            analysis["observations"].append(
                f"{len(fin_packets)} FIN packets: graceful connection terminations present"
            )
        if len(rst_packets) > 0:
            analysis["observations"].append(
                f"{len(rst_packets)} RST packets: abrupt connection resets (rejected connections or errors)"
            )

        return json.dumps({"status": "success", "analysis": analysis})
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


@tool
def rank_by_educational_value(context_json: str) -> str:
    """Rank protocols and packets by their educational interest value.
    Prioritizes: handshakes > anomalies > diverse protocol mix > plain data transfer.
    Args:
        context_json: JSON with 'protocols' and 'anomalies' lists
    Returns ranked list with educational scores and top learning moments."""
    try:
        data = json.loads(context_json)
        protocols = data.get("protocols", [])
        anomalies = data.get("anomalies", [])

        # Score protocols by educational interest
        educational_priority = {
            "DNS": 9, "HTTP": 8, "HTTPS": 7, "TLS": 9,
            "ARP": 8, "ICMP": 7, "TCP": 10, "UDP": 7,
            "SSH": 6, "FTP": 7, "SMTP": 6, "DHCP": 7,
        }

        scored_protocols = []
        for proto in protocols:
            name = proto.upper() if isinstance(proto, str) else proto.get("protocol_name", "").upper()
            base_score = educational_priority.get(name, 5)
            scored_protocols.append({
                "protocol": name,
                "educational_score": base_score,
                "reason": f"{'Core protocol worth learning' if base_score >= 8 else 'Supporting protocol'}",
            })

        scored_protocols.sort(key=lambda x: x["educational_score"], reverse=True)

        top_moments = []
        if any(p["protocol"] == "TCP" for p in scored_protocols):
            top_moments.append("TCP 3-way handshake: observe how connections are established")
        if any(p["protocol"] in ["TLS", "HTTPS"] for p in scored_protocols):
            top_moments.append("TLS handshake: see how encryption is negotiated before any data flows")
        if any(p["protocol"] == "DNS" for p in scored_protocols):
            top_moments.append("DNS resolution: every web request starts with a name lookup")
        if anomalies:
            top_moments.append(f"Security insight: {anomalies[0].get('description', 'anomalous pattern detected')}")

        return json.dumps({
            "status": "success",
            "ranked_protocols": scored_protocols[:10],
            "top_learning_moments": top_moments[:3],
        })
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})
