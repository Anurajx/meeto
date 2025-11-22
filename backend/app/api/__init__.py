"""
API routes
"""
from fastapi import APIRouter
from app.api import auth, meetings, tasks, integrations

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["authentication"])
router.include_router(meetings.router, prefix="/meetings", tags=["meetings"])
router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
router.include_router(integrations.router, prefix="/integrations", tags=["integrations"])

