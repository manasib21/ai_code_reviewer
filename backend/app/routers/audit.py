"""
API usage audit endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.core.models import APIAudit

router = APIRouter()

@router.get("/usage")
async def get_usage_stats(
    user_id: Optional[str] = None,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """Get API usage statistics"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = select(APIAudit).where(APIAudit.created_at >= start_date)
    
    if user_id:
        query = query.where(APIAudit.user_id == user_id)
    
    result = await db.execute(query)
    audits = result.scalars().all()
    
    # Aggregate statistics
    total_requests = len(audits)
    by_model = {}
    total_cost = 0.0
    
    for audit in audits:
        model = audit.model_used
        by_model[model] = by_model.get(model, 0) + 1
        if audit.cost:
            total_cost += audit.cost
    
    return {
        "period_days": days,
        "total_requests": total_requests,
        "by_model": by_model,
        "total_cost": total_cost,
        "average_per_day": total_requests / days if days > 0 else 0
    }

@router.get("/usage/detailed")
async def get_detailed_usage(
    user_id: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed API usage log"""
    query = select(APIAudit).order_by(desc(APIAudit.created_at))
    
    if user_id:
        query = query.where(APIAudit.user_id == user_id)
    
    query = query.limit(limit).offset(offset)
    
    result = await db.execute(query)
    audits = result.scalars().all()
    
    return [
        {
            "id": a.id,
            "user_id": a.user_id,
            "model_used": a.model_used,
            "tokens_used": a.tokens_used,
            "cost": a.cost,
            "review_id": a.review_id,
            "created_at": a.created_at.isoformat()
        }
        for a in audits
    ]

