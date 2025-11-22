"""
Task management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.database import get_db
from app.models import User, Task
from app.api.auth import get_current_user
from app.services.jira_service import get_jira_service_for_user
from app.services.trello_service import get_trello_service_for_user
from app.models import Integration

router = APIRouter()


class TaskUpdate(BaseModel):
    description: Optional[str] = None
    owner_name: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: Optional[str] = None
    status: Optional[str] = None


class TaskResponse(BaseModel):
    id: int
    description: str
    owner_name: Optional[str]
    owner_id: Optional[int]
    deadline: Optional[datetime]
    priority: str
    confidence: float
    status: str
    jira_issue_key: Optional[str]
    trello_card_id: Optional[str]
    meeting_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class TaskSyncRequest(BaseModel):
    service: str  # "jira" or "trello"
    project_key: Optional[str] = None  # For Jira
    list_id: Optional[str] = None  # For Trello


@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    meeting_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List tasks for current user"""
    query = db.query(Task).join(Task.meeting).filter(
        Task.meeting.has(owner_id=current_user.id)
    )
    
    if meeting_id:
        query = query.filter(Task.meeting_id == meeting_id)
    
    if status_filter:
        query = query.filter(Task.status == status_filter)
    
    tasks = query.order_by(Task.created_at.desc()).all()
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get task details"""
    task = db.query(Task).join(Task.meeting).filter(
        Task.id == task_id,
        Task.meeting.has(owner_id=current_user.id)
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a task"""
    task = db.query(Task).join(Task.meeting).filter(
        Task.id == task_id,
        Task.meeting.has(owner_id=current_user.id)
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a task"""
    task = db.query(Task).join(Task.meeting).filter(
        Task.id == task_id,
        Task.meeting.has(owner_id=current_user.id)
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    db.delete(task)
    db.commit()
    
    return None


@router.post("/{task_id}/confirm", response_model=TaskResponse)
async def confirm_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Confirm a task (mark as confirmed status)"""
    task = db.query(Task).join(Task.meeting).filter(
        Task.id == task_id,
        Task.meeting.has(owner_id=current_user.id)
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    task.status = "confirmed"
    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    
    return task


@router.post("/{task_id}/sync", response_model=TaskResponse)
async def sync_task_to_external(
    task_id: int,
    sync_request: TaskSyncRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync task to Jira or Trello"""
    task = db.query(Task).join(Task.meeting).filter(
        Task.id == task_id,
        Task.meeting.has(owner_id=current_user.id)
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Get user's integration config
    integration = db.query(Integration).filter(
        Integration.user_id == current_user.id,
        Integration.service_type == sync_request.service,
        Integration.is_active == True
    ).first()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{sync_request.service.capitalize()} integration not configured"
        )
    
    try:
        if sync_request.service == "jira":
            jira_service = get_jira_service_for_user(integration.config)
            
            # Map priority
            priority_map = {
                "low": "Lowest",
                "medium": "Medium",
                "high": "High",
                "critical": "Highest"
            }
            
            issue = jira_service.create_issue(
                summary=task.description[:255],  # Jira summary limit
                description=task.description,
                project_key=sync_request.project_key or integration.config.get("project_key"),
                priority=priority_map.get(task.priority, "Medium"),
                due_date=task.deadline.strftime("%Y-%m-%d") if task.deadline else None
            )
            
            task.jira_issue_key = issue["key"]
            task.status = "confirmed"
        
        elif sync_request.service == "trello":
            trello_service = get_trello_service_for_user(integration.config)
            
            due_date = None
            if task.deadline:
                due_date = task.deadline.isoformat()
            
            card = trello_service.create_card(
                name=task.description[:16384],  # Trello name limit
                desc=task.description,
                list_id=sync_request.list_id or integration.config.get("default_list_id"),
                due_date=due_date
            )
            
            task.trello_card_id = card["id"]
            task.status = "confirmed"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid service. Use 'jira' or 'trello'"
            )
        
        task.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(task)
        
        return task
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error syncing to {sync_request.service}: {str(e)}"
        )

