import sys
sys.path.insert(0, '.')

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import upload_router, analysis_router, health_router
from config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources at startup."""
    print("[Startup] Building FAISS index (or loading existing)...")
    try:
        from rag.vector_store import get_vector_store
        get_vector_store()
        print("[Startup] RAG vector store ready.")
    except Exception as e:
        print(f"[Startup] WARNING: RAG init failed: {e}")

    print("[Startup] Compiling LangGraph StateGraph...")
    try:
        from agents.graph.graph_builder import get_graph
        get_graph()
        print("[Startup] LangGraph graph compiled and ready.")
    except Exception as e:
        print(f"[Startup] WARNING: Graph compilation failed: {e}")

    yield

    print("[Shutdown] Cleaning up resources...")


app = FastAPI(
    title="Educational Packet Analyzer",
    description="AI-powered PCAP analysis and educational tool using Multi-Agent LangGraph pipeline",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(upload_router, prefix="/api", tags=["upload"])
app.include_router(analysis_router, prefix="/api", tags=["analysis"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=False,
    )
