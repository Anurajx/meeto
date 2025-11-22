"""
Application configuration
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    # Database (Supabase PostgreSQL)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:[YOUR-PASSWORD]@[YOUR-PROJECT-REF].supabase.co:5432/postgres"
    )
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    ALLOWED_HOSTS: Optional[List[str]] = None
    
    # OAuth
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI: str = os.getenv(
        "GOOGLE_REDIRECT_URI",
        "http://localhost:8000/api/v1/auth/google/callback"
    )
    
    # Email (SMTP)
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    EMAIL_FROM: Optional[str] = os.getenv("EMAIL_FROM")
    
    # Jira Integration
    JIRA_BASE_URL: Optional[str] = os.getenv("JIRA_BASE_URL")
    JIRA_EMAIL: Optional[str] = os.getenv("JIRA_EMAIL")
    JIRA_API_TOKEN: Optional[str] = os.getenv("JIRA_API_TOKEN")
    
    # Trello Integration
    TRELLO_API_KEY: Optional[str] = os.getenv("TRELLO_API_KEY")
    TRELLO_API_TOKEN: Optional[str] = os.getenv("TRELLO_API_TOKEN")
    TRELLO_BOARD_ID: Optional[str] = os.getenv("TRELLO_BOARD_ID")
    
    # Groq/LLM (for action item extraction)
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama-3.1-70b-versatile")
    
    # Legacy OpenAI support (optional, kept for backward compatibility)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Whisper
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")
    USE_LOCAL_WHISPER: bool = os.getenv("USE_LOCAL_WHISPER", "true").lower() == "true"
    
    # Privacy & Security
    ENABLE_LOCAL_MODE: bool = os.getenv("ENABLE_LOCAL_MODE", "false").lower() == "true"
    ENABLE_DATA_REDACTION: bool = os.getenv("ENABLE_DATA_REDACTION", "true").lower() == "true"
    
    # File upload
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_AUDIO_FORMATS: List[str] = [".mp3", ".wav", ".m4a", ".ogg", ".flac"]
    
    # Storage
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    TRANSCRIPT_DIR: str = os.getenv("TRANSCRIPT_DIR", "./transcripts")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

