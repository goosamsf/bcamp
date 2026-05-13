import sys
sys.path.insert(0, '.')

from config import settings


def get_embeddings():
    """
    Returns embedding model. Uses HuggingFace local model (free, no API key needed)
    regardless of LLM provider, since Anthropic has no native embeddings API.
    """
    from langchain_huggingface import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
