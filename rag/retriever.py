import sys
sys.path.insert(0, '.')

from typing import List, Optional
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever

from rag.vector_store import get_vector_store
from config import settings


def get_retriever(category_filter: Optional[str] = None) -> VectorStoreRetriever:
    store = get_vector_store()

    search_kwargs = {"k": settings.top_k_results}

    if category_filter and category_filter != "all":
        search_kwargs["filter"] = {"category": category_filter}

    return store.as_retriever(search_type="similarity", search_kwargs=search_kwargs)


def query_knowledge_base(query: str, category: str = "all") -> List[Document]:
    retriever = get_retriever(category_filter=category)
    return retriever.invoke(query)


def format_docs(docs: List[Document]) -> str:
    parts = []
    for doc in docs:
        source = doc.metadata.get("source_file", "unknown")
        parts.append(f"[Source: {source}]\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)
