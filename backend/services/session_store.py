import threading
from typing import Optional

# Thread-safe in-memory session store
_store: dict[str, dict] = {}
_lock = threading.Lock()


def save_result(session_id: str, report_json: str):
    with _lock:
        _store[session_id] = {"status": "complete", "report_json": report_json}


def save_error(session_id: str, error: str):
    with _lock:
        _store[session_id] = {"status": "failed", "error": error}


def set_pending(session_id: str):
    with _lock:
        _store[session_id] = {"status": "pending"}


def get_result(session_id: str) -> Optional[dict]:
    with _lock:
        return _store.get(session_id)


def delete_session(session_id: str) -> bool:
    with _lock:
        if session_id in _store:
            del _store[session_id]
            return True
        return False
