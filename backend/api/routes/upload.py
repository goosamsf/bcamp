import sys
sys.path.insert(0, '.')

import uuid
import os
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException

from backend.models.request_models import UploadResponse
from config import settings

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_pcap(file: UploadFile = File(...)):
    # Validate extension
    filename = file.filename or "upload.pcap"
    if not filename.lower().endswith((".pcap", ".pcapng")):
        raise HTTPException(status_code=400, detail="Only .pcap and .pcapng files are supported")

    # Validate size
    content = await file.read()
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(status_code=413, detail=f"File too large. Max {settings.max_file_size_mb}MB")
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Empty file")

    # Save to disk
    session_id = str(uuid.uuid4())
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / f"{session_id}.pcap"
    file_path.write_bytes(content)

    return UploadResponse(
        session_id=session_id,
        file_name=filename,
        file_size_bytes=len(content),
        status="uploaded",
    )
