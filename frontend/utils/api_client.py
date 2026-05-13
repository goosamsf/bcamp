import requests
import json
from typing import Iterator, Optional


BACKEND_URL = "http://localhost:8000/api"


def upload_pcap(file_bytes: bytes, filename: str) -> dict:
    """Upload a PCAP file and return session info."""
    response = requests.post(
        f"{BACKEND_URL}/upload",
        files={"file": (filename, file_bytes, "application/octet-stream")},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def stream_analysis(session_id: str, complexity_level: str = "beginner") -> Iterator[dict]:
    """Stream analysis events via SSE. Yields event dicts."""
    with requests.post(
        f"{BACKEND_URL}/analyze",
        json={"session_id": session_id, "complexity_level": complexity_level},
        stream=True,
        timeout=300,
    ) as resp:
        resp.raise_for_status()
        event_type = "message"
        for line in resp.iter_lines(decode_unicode=True):
            if not line:
                continue
            if line.startswith("event: "):
                event_type = line[7:].strip()
            elif line.startswith("data: "):
                data_str = line[6:].strip()
                try:
                    data = json.loads(data_str)
                except json.JSONDecodeError:
                    data = {"raw": data_str}
                yield {"event": event_type, "data": data}
                event_type = "message"


def get_analysis_result(session_id: str) -> Optional[dict]:
    """Fetch cached analysis result."""
    response = requests.get(f"{BACKEND_URL}/analysis/{session_id}", timeout=10)
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()


def delete_session(session_id: str) -> bool:
    response = requests.delete(f"{BACKEND_URL}/session/{session_id}", timeout=10)
    return response.ok


def check_health() -> dict:
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.json()
    except Exception as e:
        return {"status": "error", "error": str(e)}
