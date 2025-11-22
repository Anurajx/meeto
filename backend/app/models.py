"""
Database models
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)  # For email/password auth
    provider = Column(String, nullable=False, default="email")  # email, google
    provider_id = Column(String, nullable=True)  # OAuth provider user ID
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    meetings = relationship("Meeting", back_populates="owner")
    tasks = relationship("Task", back_populates="owner")


class Meeting(Base):
    """Meeting recording and transcript"""
    __tablename__ = "meetings"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=True)
    audio_file_path = Column(String, nullable=True)
    transcript = Column(Text, nullable=True)
    transcript_json = Column(JSON, nullable=True)  # Full Whisper output
    status = Column(String, default="pending")  # pending, processing, completed, failed
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Privacy settings
    is_local_only = Column(Boolean, default=False)
    is_redacted = Column(Boolean, default=False)
    
    # Relationships
    owner = relationship("User", back_populates="meetings")
    tasks = relationship("Task", back_populates="meeting", cascade="all, delete-orphan")


class Task(Base):
    """Extracted action items/tasks"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    owner_name = Column(String, nullable=True)  # Person responsible (from transcript)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Assigned user
    deadline = Column(DateTime(timezone=True), nullable=True)
    priority = Column(String, default="medium")  # low, medium, high, critical
    confidence = Column(Float, default=0.0)
    status = Column(String, default="pending")  # pending, confirmed, completed, cancelled
    
    # External integrations
    jira_issue_key = Column(String, nullable=True)
    trello_card_id = Column(String, nullable=True)
    
    # Metadata
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    meeting = relationship("Meeting", back_populates="tasks")
    owner = relationship("User", back_populates="tasks")


class Integration(Base):
    """User's external service integrations (Jira, Trello)"""
    __tablename__ = "integrations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_type = Column(String, nullable=False)  # jira, trello
    is_active = Column(Boolean, default=True)
    config = Column(JSON, nullable=False)  # Store API keys, URLs, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

