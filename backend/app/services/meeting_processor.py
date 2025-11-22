"""
Background task processor for meetings
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Meeting, Task
from app.services.whisper_service import whisper_service
from app.services.llm_service import llm_service
from app.services.redaction_service import redaction_service
from app.config import settings
from datetime import datetime


def process_meeting_audio(meeting_id: int):
    """
    Background task to process meeting audio
    Should be called from a background worker (Celery, etc.)
    """
    db = SessionLocal()
    try:
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting:
            return
        
        meeting.status = "processing"
        db.commit()
        
        # Transcribe audio
        if whisper_service and meeting.audio_file_path:
            result = whisper_service.transcribe(meeting.audio_file_path)
            transcript = result["text"]
            meeting.transcript_json = result["full_result"]
            
            # Redact sensitive information if enabled
            if settings.ENABLE_DATA_REDACTION:
                transcript, redacted_items = redaction_service.redact(transcript)
                meeting.is_redacted = len(redacted_items) > 0
            
            meeting.transcript = transcript
            
            # Extract action items
            if llm_service:
                action_items = llm_service.extract_action_items(transcript)
                
                # Create task records
                for task_data in action_items.get("tasks", []):
                    deadline = None
                    if task_data.get("deadline"):
                        try:
                            deadline = datetime.fromisoformat(task_data["deadline"])
                        except:
                            pass
                    
                    task = Task(
                        description=task_data["description"],
                        owner_name=task_data.get("owner"),
                        deadline=deadline,
                        priority=task_data.get("priority", "medium"),
                        confidence=task_data.get("confidence", 0.0),
                        meeting_id=meeting.id,
                        status="pending"
                    )
                    db.add(task)
            
            meeting.status = "completed"
            meeting.processed_at = datetime.utcnow()
        else:
            meeting.status = "failed"
        
        db.commit()
    except Exception as e:
        print(f"Error processing meeting {meeting_id}: {e}")
        db.rollback()
        if meeting:
            meeting.status = "failed"
            db.commit()
    finally:
        db.close()

