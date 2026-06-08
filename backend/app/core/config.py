"""
应用配置
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """环境变量配置"""

    # 环境
    env: str = "development"

    # 数据库
    database_url: str = "postgresql://user:password@localhost:5432/education_services"

    # MinIO / S3
    s3_endpoint: str = "localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket: str = "education-services"

    # LLM
    anthropic_api_key: str = ""

    # MCP servers
    textbook_mcp_url: str = "http://localhost:8001"
    vector_index_mcp_url: str = "http://localhost:8002"
    student_profile_mcp_url: str = "http://localhost:8003"
    homework_store_mcp_url: str = "http://localhost:8004"
    question_bank_mcp_url: str = "http://localhost:8005"

    # CORS
    allowed_origins: List[str] = ["*"]

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
