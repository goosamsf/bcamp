from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Literal


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM provider
    llm_provider: Literal["openai", "anthropic"] = "openai"
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")

    # Model settings
    model_name: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"

    # Server settings
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    frontend_port: int = 8501

    # File upload settings
    upload_dir: str = "/tmp/pcap_uploads"
    max_file_size_mb: int = 50

    # RAG settings
    faiss_index_dir: str = "rag/faiss_index"
    top_k_results: int = 5


settings = Settings()
