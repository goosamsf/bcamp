from pydantic import BaseModel
from typing import Literal


class AnalyzeRequest(BaseModel):
    session_id: str
    complexity_level: Literal["beginner", "intermediate", "advanced"] = "beginner"


class UploadResponse(BaseModel):
    session_id: str
    file_name: str
    file_size_bytes: int
    status: str = "uploaded"


class AnalysisStatusResponse(BaseModel):
    session_id: str
    status: str  # "pending" | "complete" | "failed"
    report_json: str | None = None
    error: str | None = None
