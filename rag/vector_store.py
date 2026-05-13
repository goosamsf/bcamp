import os
import sys
sys.path.insert(0, '.')

from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from typing import List

from config import settings
from rag.document_loader import load_knowledge_base, chunk_documents
from rag.embeddings import get_embeddings


_vector_store: FAISS | None = None
INDEX_DIR = Path(settings.faiss_index_dir)


def build_vector_store() -> FAISS:
    print("[RAG] Loading knowledge base documents...")
    documents = load_knowledge_base()
    print(f"[RAG] Loaded {len(documents)} documents")

    chunks = chunk_documents(documents)
    print(f"[RAG] Split into {len(chunks)} chunks")

    embeddings = get_embeddings()
    store = FAISS.from_documents(chunks, embeddings)

    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    store.save_local(str(INDEX_DIR))
    print(f"[RAG] FAISS index saved to {INDEX_DIR}")

    return store


def load_vector_store() -> FAISS:
    embeddings = get_embeddings()
    store = FAISS.load_local(
        str(INDEX_DIR),
        embeddings,
        allow_dangerous_deserialization=True,
    )
    print(f"[RAG] FAISS index loaded from {INDEX_DIR}")
    return store


def get_vector_store() -> FAISS:
    global _vector_store

    if _vector_store is not None:
        return _vector_store

    if INDEX_DIR.exists() and any(INDEX_DIR.iterdir()):
        _vector_store = load_vector_store()
    else:
        _vector_store = build_vector_store()

    return _vector_store


def reset_vector_store():
    global _vector_store
    _vector_store = None
