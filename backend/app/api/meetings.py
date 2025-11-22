"""
Meeting endpoints for uploading and processing audio
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import os
import shutil
from pathlib import Path
from datetime import datetime

from app.database import get_db
from app.models import User, Meeting, Task
from app.api.auth import get_current_user
from app.config import settings
from app.services.meeting_processor import process_meeting_audio as process_meeting_task

router = APIRouter()

# Ensure upload directories exist
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.TRANSCRIPT_DIR).mkdir(parents=True, exist_ok=True)


class MeetingResponse(BaseModel):
    id: int
    title: Optional[str]
    status: str
    created_at: datetime
    processed_at: Optional[datetime]
    is_local_only: bool
    is_redacted: bool
    
    class Config:
        from_attributes = True


class MeetingDetailResponse(MeetingResponse):
    transcript: Optional[str]
    tasks: List[dict]




@router.post("/upload", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
async def upload_meeting(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: Optional[str] = None,
    is_local_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload meeting audio file for processing"""
    # Validate file type
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_AUDIO_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(settings.ALLOWED_AUDIO_FORMATS)}"
        )
    
    # Check file size
    file_content = await file.read()
    if len(file_content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
        )
    
    # Save file
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{current_user.id}_{timestamp}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Create meeting record
    meeting = Meeting(
        title=title or file.filename,
        audio_file_path=file_path,
        owner_id=current_user.id,
        status="pending",
        is_local_only=is_local_only or settings.ENABLE_LOCAL_MODE
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    
    # Process in background
    background_tasks.add_task(process_meeting_task, meeting.id)
    
    return meeting


@router.get("/", response_model=List[MeetingResponse])
async def list_meetings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all meetings for current user"""
    meetings = db.query(Meeting).filter(Meeting.owner_id == current_user.id).order_by(Meeting.created_at.desc()).all()
    return meetings


@router.get("/{meeting_id}", response_model=MeetingDetailResponse)
async def get_meeting(
    meeting_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get meeting details with transcript and tasks"""
    meeting = db.query(Meeting).filter(
        Meeting.id == meeting_id,
        Meeting.owner_id == current_user.id
    ).first()
    
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )
    
    tasks = db.query(Task).filter(Task.meeting_id == meeting_id).all()
    
    return {
        **meeting.__dict__,
        "tasks": [
            {
                "id": task.id,
                "description": task.description,
                "owner_name": task.owner_name,
                "deadline": task.deadline.isoformat() if task.deadline else None,
                "priority": task.priority,
                "confidence": task.confidence,
                "status": task.status
            }
            for task in tasks
        ]
    }


@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meeting(
    meeting_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a meeting and its associated files"""
    meeting = db.query(Meeting).filter(
        Meeting.id == meeting_id,
        Meeting.owner_id == current_user.id
    ).first()
    
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )
    
    # Delete audio file if exists
    if meeting.audio_file_path and os.path.exists(meeting.audio_file_path):
        os.remove(meeting.audio_file_path)
    
    db.delete(meeting)
    db.commit()
    
    return None

