"""
Configuration settings for the QA Automation Platform backend.
Loads configuration from environment variables using Pydantic Settings.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    API_TITLE: str = "QA Automation Platform API"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # CORS Configuration
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]

    # Google Cloud Configuration
    GOOGLE_API_KEY: Optional[str] = None
    GOOGLE_PROJECT_ID: Optional[str] = None
    GOOGLE_CLOUD_CREDENTIALS: Optional[str] = None

    # Gemini Configuration
    GEMINI_MODEL: str = "gemini-1.5-pro-vision"
    GEMINI_MAX_TOKENS: int = 4096
    GEMINI_TEMPERATURE: float = 0.7

    # Document AI Configuration
    DOCAI_PROCESSOR_ID: Optional[str] = None
    DOCAI_LOCATION: str = "us"

    # File Upload Configuration
    MAX_UPLOAD_SIZE: int = 500 * 1024 * 1024  # 500MB
    UPLOAD_DIR: str = "/tmp/qa-automation-uploads"
    ALLOWED_VIDEO_EXTENSIONS: list = ["mp4", "avi", "mov", "mkv", "webm"]
    ALLOWED_IMAGE_EXTENSIONS: list = ["jpg", "jpeg", "png", "gif", "webp"]

    # Database Configuration
    DATABASE_URL: Optional[str] = None
    DATABASE_ECHO: bool = False

    # Video Processing
    VIDEO_FRAME_EXTRACTION_INTERVAL: int = 5  # Extract frame every 5 seconds
    VIDEO_MAX_DURATION: int = 3600  # Max 1 hour

    # Validation Configuration
    VALIDATION_TOLERANCE: float = 0.95  # 95% match threshold
    VALIDATION_TIMEOUT: int = 300  # 5 minutes

    # System Detection Confidence Threshold
    SYSTEM_DETECTION_THRESHOLD: float = 0.7

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create global settings instance
settings = Settings()
