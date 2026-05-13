import sys
sys.path.insert(0, '.')

from fastapi import APIRouter
from pathlib import Path
from config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    faiss_loaded = Path(settings.faiss_index_dir).exists()
    return {
        "status": "ok",
        "version": "1.0.0",
        "service": "Educational Packet Analyzer",
        "rag_index_exists": faiss_loaded,
    }
