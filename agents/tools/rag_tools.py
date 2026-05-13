import sys
sys.path.insert(0, '.')

import json
from langchain_core.tools import tool


@tool
def query_rag_knowledge(query: str, category: str = "all") -> str:
    """Query the network protocol knowledge base to retrieve educational content.
    Args:
        query: Natural language question about a protocol or networking concept
        category: Filter results by 'protocol', 'concept', 'security', or 'all'
    Returns relevant documentation with source information.
    Use this to retrieve educational explanations about any network protocol or concept."""
    try:
        from rag.retriever import query_knowledge_base
        docs = query_knowledge_base(query, category if category != "all" else None)

        results = []
        for doc in docs:
            results.append({
                "content": doc.page_content,
                "source": doc.metadata.get("source_file", "unknown"),
                "protocol": doc.metadata.get("protocol_name", ""),
                "category": doc.metadata.get("category", ""),
                "difficulty": doc.metadata.get("difficulty_level", "beginner"),
            })

        return json.dumps({
            "status": "success",
            "query": query,
            "results": results,
            "count": len(results),
        })
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e), "query": query})


@tool
def lookup_rfc_summary(protocol_name: str) -> str:
    """Look up the RFC number and summary for a given network protocol.
    Args:
        protocol_name: Protocol name (e.g., 'TCP', 'DNS', 'HTTP', 'TLS')
    Returns RFC number, description, and key characteristics.
    Use to provide authoritative references in educational content."""
    rfc_database = {
        "TCP": {"rfc": "RFC 793", "year": 1981, "title": "Transmission Control Protocol", "layer": "Transport (L4)"},
        "IP": {"rfc": "RFC 791", "year": 1981, "title": "Internet Protocol", "layer": "Network (L3)"},
        "UDP": {"rfc": "RFC 768", "year": 1980, "title": "User Datagram Protocol", "layer": "Transport (L4)"},
        "DNS": {"rfc": "RFC 1035", "year": 1987, "title": "Domain Names - Implementation and Specification", "layer": "Application (L7)"},
        "HTTP": {"rfc": "RFC 7230-7235", "year": 2014, "title": "Hypertext Transfer Protocol/1.1", "layer": "Application (L7)"},
        "HTTPS": {"rfc": "RFC 2818", "year": 2000, "title": "HTTP Over TLS", "layer": "Application (L7)"},
        "TLS": {"rfc": "RFC 8446", "year": 2018, "title": "The Transport Layer Security (TLS) Protocol Version 1.3", "layer": "Presentation (L6)"},
        "SSL": {"rfc": "RFC 6101", "year": 2011, "title": "The Secure Sockets Layer (SSL) Protocol Version 3.0", "layer": "Presentation (L6)"},
        "ICMP": {"rfc": "RFC 792", "year": 1981, "title": "Internet Control Message Protocol", "layer": "Network (L3)"},
        "ARP": {"rfc": "RFC 826", "year": 1982, "title": "An Ethernet Address Resolution Protocol", "layer": "DataLink/Network"},
        "DHCP": {"rfc": "RFC 2131", "year": 1997, "title": "Dynamic Host Configuration Protocol", "layer": "Application (L7)"},
        "FTP": {"rfc": "RFC 959", "year": 1985, "title": "File Transfer Protocol", "layer": "Application (L7)"},
        "SMTP": {"rfc": "RFC 5321", "year": 2008, "title": "Simple Mail Transfer Protocol", "layer": "Application (L7)"},
        "SSH": {"rfc": "RFC 4253", "year": 2006, "title": "The Secure Shell (SSH) Transport Layer Protocol", "layer": "Application (L7)"},
        "NTP": {"rfc": "RFC 5905", "year": 2010, "title": "Network Time Protocol Version 4", "layer": "Application (L7)"},
        "SNMP": {"rfc": "RFC 3416", "year": 2002, "title": "Simple Network Management Protocol", "layer": "Application (L7)"},
    }

    name_upper = protocol_name.upper()
    info = rfc_database.get(name_upper)

    if info:
        return json.dumps({"status": "success", "protocol": name_upper, **info})
    else:
        return json.dumps({
            "status": "not_found",
            "protocol": protocol_name,
            "message": f"RFC info not in local database for {protocol_name}. Protocol may be proprietary or use a different name.",
        })
