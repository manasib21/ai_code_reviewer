"""
Code review service - orchestrates the review process
"""
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.ai_providers import ai_provider, AIModel
from app.core.models import Review, Issue, APIAudit
from app.services.code_analyzer import CodeAnalyzer
from app.services.config_service import ConfigService
from datetime import datetime
import json

class ReviewService:
    """Service for performing code reviews"""
    
    def __init__(self):
        self.code_analyzer = CodeAnalyzer()
        self.config_service = ConfigService()
    
    async def review_code(
        self,
        code: str,
        language: str,
        file_path: Optional[str] = None,
        model: AIModel = AIModel.GPT_3_5_TURBO,
        config_name: Optional[str] = None,
        context: Optional[str] = None,
        user_id: Optional[str] = None,
        repository: Optional[str] = None,
        commit_hash: Optional[str] = None,
        db: Optional[AsyncSession] = None
    ) -> Dict:
        """
        Perform comprehensive code review
        
        Returns:
            Review results with issues and metadata
        """
        # Load configuration
        config = await self.config_service.get_config(config_name, user_id, db)
        
        # Check ignore patterns
        if file_path and self._should_ignore(file_path, config):
            return {
                "issues": [],
                "summary": {"total_issues": 0},
                "overall_score": 100,
                "ignored": True,
                "reason": "File matches ignore pattern"
            }
        
        # Get custom prompt from config
        custom_prompt = config.get("custom_prompt") if config else None
        
        # Perform AI review
        ai_result = await ai_provider.review_code(
            code=code,
            language=language,
            model=model,
            custom_prompt=custom_prompt,
            context=context
        )
        
        # Apply severity filters from config
        if config:
            ai_result = self._apply_severity_filters(ai_result, config)
        
        # Track API usage
        if db:
            await self._track_api_usage(
                model=model,
                user_id=user_id,
                db=db
            )
        
        # Save review to database
        review_record = None
        if db:
            review_record = await self._save_review(
                code=code,
                language=language,
                file_path=file_path,
                ai_result=ai_result,
                model=model,
                user_id=user_id,
                repository=repository,
                commit_hash=commit_hash,
                db=db
            )
        
        # Add review ID to result
        if review_record:
            ai_result["review_id"] = review_record.id
        
        return ai_result
    
    def _should_ignore(self, file_path: str, config: Optional[Dict]) -> bool:
        """Check if file should be ignored based on patterns"""
        if not config:
            return False
        
        ignore_patterns = config.get("ignore_patterns", [])
        for pattern in ignore_patterns:
            # Simple pattern matching (can be enhanced with glob/fnmatch)
            if pattern in file_path or file_path.endswith(pattern):
                return True
        
        return False
    
    def _apply_severity_filters(self, result: Dict, config: Dict) -> Dict:
        """Filter issues based on configured severity levels"""
        min_severity = config.get("min_severity", "low")
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        min_level = severity_order.get(min_severity, 3)
        
        filtered_issues = [
            issue for issue in result.get("issues", [])
            if severity_order.get(issue.get("severity", "low"), 3) <= min_level
        ]
        
        result["issues"] = filtered_issues
        result["summary"]["total_issues"] = len(filtered_issues)
        
        return result
    
    async def _track_api_usage(
        self,
        model: AIModel,
        user_id: Optional[str],
        db: AsyncSession
    ):
        """Track API usage for audit"""
        audit = APIAudit(
            user_id=user_id,
            model_used=model.value,
            created_at=datetime.utcnow()
        )
        db.add(audit)
        await db.commit()
    
    async def _save_review(
        self,
        code: str,
        language: str,
        file_path: Optional[str],
        ai_result: Dict,
        model: AIModel,
        user_id: Optional[str],
        repository: Optional[str],
        commit_hash: Optional[str],
        db: AsyncSession
    ) -> Review:
        """Save review to database"""
        review = Review(
            file_path=file_path,
            language=language,
            code_content=code,
            review_results=ai_result,
            model_used=model.value,
            overall_score=ai_result.get("overall_score", 100),
            user_id=user_id,
            repository=repository,
            commit_hash=commit_hash,
            created_at=datetime.utcnow()
        )
        
        db.add(review)
        await db.flush()
        
        # Save individual issues
        for issue_data in ai_result.get("issues", []):
            issue = Issue(
                review_id=review.id,
                issue_type=issue_data.get("type"),
                severity=issue_data.get("severity"),
                line=issue_data.get("line"),
                column=issue_data.get("column"),
                description=issue_data.get("description"),
                suggestion=issue_data.get("suggestion"),
                explanation=issue_data.get("explanation"),
                status="open",
                created_at=datetime.utcnow()
            )
            db.add(issue)
        
        await db.commit()
        await db.refresh(review)
        
        return review

review_service = ReviewService()

