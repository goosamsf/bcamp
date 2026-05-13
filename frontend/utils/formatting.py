PROTOCOL_COLORS = {
    "HTTP": "#4CAF50",
    "HTTPS": "#2196F3",
    "TLS": "#2196F3",
    "DNS": "#FF9800",
    "TCP": "#9C27B0",
    "UDP": "#00BCD4",
    "ICMP": "#F44336",
    "ARP": "#795548",
    "SSH": "#607D8B",
    "FTP": "#E91E63",
    "SMTP": "#FF5722",
    "DHCP": "#009688",
}

SEVERITY_COLORS = {
    "high": "#F44336",
    "medium": "#FF9800",
    "low": "#4CAF50",
}

OSI_LAYER_LABELS = {
    "L7_Application": "Application (L7)",
    "L4_Transport": "Transport (L4)",
    "L3_Network": "Network (L3)",
    "L2_DataLink": "Data Link (L2)",
    "Unknown": "Unknown",
}


def get_protocol_color(protocol: str) -> str:
    for key, color in PROTOCOL_COLORS.items():
        if key in protocol.upper():
            return color
    return "#757575"


def bytes_to_human(n: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def seconds_to_human(s: float) -> str:
    if s < 1:
        return f"{s*1000:.0f}ms"
    elif s < 60:
        return f"{s:.1f}s"
    else:
        return f"{int(s//60)}m {int(s%60)}s"
