import os
from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


KNOWLEDGE_BASE_DIR = Path(__file__).parent / "knowledge_base"

CATEGORY_MAP = {
    "protocols": "protocol",
    "concepts": "concept",
    "security": "security",
}


def _get_difficulty(content: str, category: str) -> str:
    if "Difficulty**: Beginner" in content:
        return "beginner"
    elif "Difficulty**: Intermediate" in content:
        return "intermediate"
    elif "Difficulty**: Advanced" in content:
        return "advanced"
    return "beginner" if category == "concept" else "intermediate"


def load_knowledge_base() -> List[Document]:
    documents = []

    for category_dir in KNOWLEDGE_BASE_DIR.iterdir():
        if not category_dir.is_dir():
            continue
        category = CATEGORY_MAP.get(category_dir.name, category_dir.name)

        for md_file in category_dir.glob("*.md"):
            content = md_file.read_text(encoding="utf-8")
            protocol_name = md_file.stem.replace("_", " ").upper()

            doc = Document(
                page_content=content,
                metadata={
                    "source_file": md_file.name,
                    "protocol_name": protocol_name,
                    "category": category,
                    "difficulty_level": _get_difficulty(content, category),
                },
            )
            documents.append(doc)

    return documents


def chunk_documents(documents: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=50,
        separators=["\n## ", "\n### ", "\n\n", "\n", " "],
    )
    chunks = splitter.split_documents(documents)

    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = i

    return chunks
