"""
Review API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.review_service import review_service
from app.core.ai_providers import AIModel
from app.services.code_analyzer import CodeAnalyzer
from app.services.report_generator import report_generator

router = APIRouter()
code_analyzer = CodeAnalyzer()

class ReviewRequest(BaseModel):
    code: str
    language: Optional[str] = None
    file_path: Optional[str] = None
    model: str = "gpt-3.5-turbo"
    config_name: Optional[str] = None
    context: Optional[str] = None
    user_id: Optional[str] = None
    repository: Optional[str] = None
    commit_hash: Optional[str] = None

class ReviewResponse(BaseModel):
    review_id: Optional[int]
    issues: List[dict]
    summary: dict
    overall_score: float
    model_used: str
    recommendations: List[str]

@router.post("/", response_model=ReviewResponse)
async def create_review(
    request: ReviewRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Create a new code review"""
    try:
        # Detect language if not provided
        language = request.language or code_analyzer.detect_language(
            request.code,
            request.file_path
        )
        
        # Get context
        context = request.context or code_analyzer.extract_context(
            request.code,
            request.file_path
        )
        
        # Parse model
        try:
            model = AIModel(request.model)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid model: {request.model}")
        
        # Perform review
        result = await review_service.review_code(
            code=request.code,
            language=language,
            file_path=request.file_path,
            model=model,
            config_name=request.config_name,
            context=context,
            user_id=request.user_id,
            repository=request.repository,
            commit_hash=request.commit_hash,
            db=db
        )
        
        return ReviewResponse(
            review_id=result.get("review_id"),
            issues=result.get("issues", []),
            summary=result.get("summary", {}),
            overall_score=result.get("overall_score", 100),
            model_used=result.get("model_used", request.model),
            recommendations=result.get("recommendations", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{review_id}")
async def get_review(review_id: int, db: AsyncSession = Depends(get_db)):
    """Get a review by ID"""
    from sqlalchemy import select
    from app.core.models import Review
    
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    return {
        "id": review.id,
        "file_path": review.file_path,
        "language": review.language,
        "review_results": review.review_results,
        "model_used": review.model_used,
        "overall_score": review.overall_score,
        "created_at": review.created_at.isoformat()
    }

@router.get("/{review_id}/report", response_class=HTMLResponse)
async def get_review_report(review_id: int, db: AsyncSession = Depends(get_db)):
    """Get HTML report for a review"""
    from sqlalchemy import select
    from app.core.models import Review
    
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    html_report = report_generator.generate_html(
        review.review_results,
        review.file_path,
        review.language
    )
    
    return HTMLResponse(content=html_report)

