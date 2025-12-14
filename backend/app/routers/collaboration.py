"""
Collaboration endpoints for team features
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.database import get_db
from app.core.models import Issue, IssueComment

router = APIRouter()

class CommentRequest(BaseModel):
    issue_id: int
    user_id: str
    comment: str

@router.post("/comments")
async def add_comment(
    request: CommentRequest,
    db: AsyncSession = Depends(get_db)
):
    """Add a comment to an issue"""
    # Verify issue exists
    result = await db.execute(select(Issue).where(Issue.id == request.issue_id))
    issue = result.scalar_one_or_none()
    
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    comment = IssueComment(
        issue_id=request.issue_id,
        user_id=request.user_id,
        comment=request.comment
    )
    
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    
    return {
        "id": comment.id,
        "issue_id": comment.issue_id,
        "user_id": comment.user_id,
        "comment": comment.comment,
        "created_at": comment.created_at.isoformat()
    }

@router.get("/issues/{issue_id}/comments")
async def get_comments(
    issue_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get comments for an issue"""
    result = await db.execute(
        select(IssueComment).where(IssueComment.issue_id == issue_id)
        .order_by(IssueComment.created_at)
    )
    comments = result.scalars().all()
    
    return [
        {
            "id": c.id,
            "user_id": c.user_id,
            "comment": c.comment,
            "created_at": c.created_at.isoformat()
        }
        for c in comments
    ]

@router.patch("/issues/{issue_id}/status")
async def update_issue_status(
    issue_id: int,
    status: str,
    db: AsyncSession = Depends(get_db)
):
    """Update issue status (open, resolved, ignored)"""
    if status not in ["open", "resolved", "ignored"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    result = await db.execute(select(Issue).where(Issue.id == issue_id))
    issue = result.scalar_one_or_none()
    
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    issue.status = status
    await db.commit()
    await db.refresh(issue)
    
    return {
        "id": issue.id,
        "status": issue.status
    }

