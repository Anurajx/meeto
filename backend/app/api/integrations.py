"""
Integration management endpoints (Jira, Trello)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

from app.database import get_db
from app.models import User, Integration
from app.api.auth import get_current_user

router = APIRouter()


class IntegrationCreate(BaseModel):
    service_type: str  # "jira" or "trello"
    config: Dict[str, Any]


class IntegrationResponse(BaseModel):
    id: int
    service_type: str
    is_active: bool
    config: Dict[str, Any]
    
    class Config:
        from_attributes = True


@router.post("/", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED)
async def create_integration(
    integration_data: IntegrationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update an integration"""
    if integration_data.service_type not in ["jira", "trello"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid service_type. Use 'jira' or 'trello'"
        )
    
    # Check if integration exists
    existing = db.query(Integration).filter(
        Integration.user_id == current_user.id,
        Integration.service_type == integration_data.service_type
    ).first()
    
    if existing:
        existing.config = integration_data.config
        existing.is_active = True
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new integration
    integration = Integration(
        user_id=current_user.id,
        service_type=integration_data.service_type,
        config=integration_data.config,
        is_active=True
    )
    db.add(integration)
    db.commit()
    db.refresh(integration)
    
    return integration


@router.get("/", response_model=List[IntegrationResponse])
async def list_integrations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all integrations for current user"""
    integrations = db.query(Integration).filter(
        Integration.user_id == current_user.id
    ).all()
    
    # Don't return full config for security
    return [
        IntegrationResponse(
            id=i.id,
            service_type=i.service_type,
            is_active=i.is_active,
            config={k: ("***" if "key" in k.lower() or "token" in k.lower() or "password" in k.lower() else v) 
                   for k, v in i.config.items()}
        )
        for i in integrations
    ]


@router.get("/{integration_id}", response_model=IntegrationResponse)
async def get_integration(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get integration details"""
    integration = db.query(Integration).filter(
        Integration.id == integration_id,
        Integration.user_id == current_user.id
    ).first()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    # Mask sensitive config
    masked_config = {
        k: ("***" if "key" in k.lower() or "token" in k.lower() or "password" in k.lower() else v)
        for k, v in integration.config.items()
    }
    
    return IntegrationResponse(
        id=integration.id,
        service_type=integration.service_type,
        is_active=integration.is_active,
        config=masked_config
    )


@router.delete("/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_integration(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an integration"""
    integration = db.query(Integration).filter(
        Integration.id == integration_id,
        Integration.user_id == current_user.id
    ).first()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    db.delete(integration)
    db.commit()
    
    return None


@router.patch("/{integration_id}/toggle", response_model=IntegrationResponse)
async def toggle_integration(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle integration active status"""
    integration = db.query(Integration).filter(
        Integration.id == integration_id,
        Integration.user_id == current_user.id
    ).first()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    integration.is_active = not integration.is_active
    db.commit()
    db.refresh(integration)
    
    masked_config = {
        k: ("***" if "key" in k.lower() or "token" in k.lower() or "password" in k.lower() else v)
        for k, v in integration.config.items()
    }
    
    return IntegrationResponse(
        id=integration.id,
        service_type=integration.service_type,
        is_active=integration.is_active,
        config=masked_config
    )

