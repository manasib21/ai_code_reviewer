"""
Review history endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.core.models import Review, ReviewHistory

router = APIRouter()

@router.get("/")
async def get_history(
    user_id: Optional[str] = None,
    repository: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Get review history"""
    query = select(Review).order_by(desc(Review.created_at))
    
    if user_id:
        query = query.where(Review.user_id == user_id)
    if repository:
        query = query.where(Review.repository == repository)
    
    query = query.limit(limit).offset(offset)
    
    result = await db.execute(query)
    reviews = result.scalars().all()
    
    return [
        {
            "id": r.id,
            "file_path": r.file_path,
            "language": r.language,
            "overall_score": r.overall_score,
            "model_used": r.model_used,
            "created_at": r.created_at.isoformat(),
            "repository": r.repository,
            "commit_hash": r.commit_hash
        }
        for r in reviews
    ]

@router.get("/{review_id}/history")
async def get_review_history(
    review_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get history for a specific review"""
    result = await db.execute(
        select(ReviewHistory).where(ReviewHistory.review_id == review_id)
        .order_by(desc(ReviewHistory.created_at))
    )
    history = result.scalars().all()
    
    return [
        {
            "id": h.id,
            "action": h.action,
            "user_id": h.user_id,
            "details": h.details,
            "created_at": h.created_at.isoformat()
        }
        for h in history
    ]

