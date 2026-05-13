import sys
sys.path.insert(0, '.')

import json
import asyncio
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

from backend.models.request_models import AnalyzeRequest, AnalysisStatusResponse
from backend.services import session_store
from config import settings

router = APIRouter()


async def _run_analysis_stream(session_id: str, complexity_level: str):
    """Run LangGraph analysis and yield SSE events."""
    from agents.graph.graph_builder import get_graph

    file_path = str(Path(settings.upload_dir) / f"{session_id}.pcap")
    if not Path(file_path).exists():
        yield {"event": "error", "data": json.dumps({"error": f"File not found for session {session_id}"})}
        return

    session_store.set_pending(session_id)

    initial_state = {
        "session_id": session_id,
        "file_path": file_path,
        "file_name": f"{session_id}.pcap",
        "user_complexity_level": complexity_level,
        "messages": [],
        "agent_statuses": {},
        "pcap_raw_json": None,
        "flows_raw_json": None,
        "statistics_raw_json": None,
        "anomalies_raw_json": None,
        "protocol_analysis_json": None,
        "educational_content_json": None,
        "final_report_json": None,
        "current_agent": "start",
        "error_message": None,
        "retry_count": 0,
        "is_complete": False,
        "agent_trace": [],
    }

    config = {"configurable": {"thread_id": session_id}}
    graph, _ = get_graph()

    try:
        async for event in graph.astream_events(initial_state, config=config, version="v2"):
            event_name = event.get("event", "")
            event_data = event.get("data", {})

            if event_name == "on_chain_start":
                node_name = event.get("name", "")
                if node_name in ["pcap_agent", "protocol_agent", "education_agent", "summary_agent", "orchestrator"]:
                    yield {
                        "event": "agent_start",
                        "data": json.dumps({"agent": node_name, "status": "running"}),
                    }

            elif event_name == "on_chain_end":
                node_name = event.get("name", "")
                if node_name in ["pcap_agent", "protocol_agent", "education_agent", "summary_agent", "orchestrator"]:
                    output = event_data.get("output", {})
                    # Extract agent message if any
                    messages = output.get("messages", [])
                    msg_text = messages[-1].content if messages else ""
                    yield {
                        "event": "agent_complete",
                        "data": json.dumps({"agent": node_name, "status": "complete", "message": msg_text}),
                    }

                    # If final report is ready, send it
                    if output.get("final_report_json"):
                        session_store.save_result(session_id, output["final_report_json"])
                        yield {
                            "event": "analysis_complete",
                            "data": output["final_report_json"],
                        }

            elif event_name == "on_chain_error":
                err = str(event_data.get("error", "Unknown error"))
                session_store.save_error(session_id, err)
                yield {"event": "error", "data": json.dumps({"error": err})}
                return

    except Exception as e:
        session_store.save_error(session_id, str(e))
        yield {"event": "error", "data": json.dumps({"error": str(e)})}


@router.post("/analyze")
async def analyze_pcap(request: AnalyzeRequest):
    async def event_generator():
        async for event in _run_analysis_stream(request.session_id, request.complexity_level):
            if isinstance(event, dict):
                event_type = event.get("event", "message")
                data = event.get("data", "")
                yield f"event: {event_type}\ndata: {data}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/analysis/{session_id}", response_model=AnalysisStatusResponse)
async def get_analysis_result(session_id: str):
    result = session_store.get_result(session_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Session not found")

    return AnalysisStatusResponse(
        session_id=session_id,
        status=result.get("status", "pending"),
        report_json=result.get("report_json"),
        error=result.get("error"),
    )


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    deleted = session_store.delete_session(session_id)
    file_path = Path(settings.upload_dir) / f"{session_id}.pcap"
    if file_path.exists():
        file_path.unlink()
    return {"deleted": deleted, "session_id": session_id}
