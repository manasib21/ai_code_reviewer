"""
Git-based review endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.review_service import review_service
from app.services.git_service import git_service
from app.core.ai_providers import AIModel
from app.services.code_analyzer import CodeAnalyzer

router = APIRouter()
code_analyzer = CodeAnalyzer()

class GitReviewRequest(BaseModel):
    repo_path: str
    base_ref: Optional[str] = None
    head_ref: Optional[str] = None
    model: str = "gpt-3.5-turbo"
    config_name: Optional[str] = None
    user_id: Optional[str] = None

@router.post("/review-diff")
async def review_git_diff(
    request: GitReviewRequest,
    db: AsyncSession = Depends(get_db)
):
    """Review git diff"""
    try:
        # Get diff
        diff = git_service.get_diff(request.repo_path, request.base_ref, request.head_ref)
        
        if not diff:
            return {"message": "No changes to review", "issues": []}
        
        # Get changed files
        changed_files = git_service.get_changed_files(
            request.repo_path,
            request.base_ref,
            request.head_ref
        )
        
        # Parse model
        try:
            ai_model = AIModel(request.model)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid model: {request.model}")
        
        # Review the diff
        result = await review_service.review_code(
            code=diff,
            language="diff",
            file_path="git diff",
            model=ai_model,
            config_name=request.config_name,
            context=f"Changed files: {', '.join(changed_files)}",
            user_id=request.user_id,
            repository=request.repo_path,
            commit_hash=git_service.get_commit_hash(request.repo_path, request.head_ref or "HEAD"),
            db=db
        )
        
        return {
            "changed_files": changed_files,
            "review": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/review-files")
async def review_changed_files(
    request: GitReviewRequest,
    db: AsyncSession = Depends(get_db)
):
    """Review all changed files individually"""
    try:
        # Get changed files
        changed_files = git_service.get_changed_files(
            request.repo_path,
            request.base_ref,
            request.head_ref
        )
        
        if not changed_files:
            return {"message": "No files to review", "results": []}
        
        # Parse model
        try:
            ai_model = AIModel(request.model)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid model: {request.model}")
        
        results = []
        
        for file_path in changed_files:
            try:
                # Get file content
                content = git_service.get_file_content(
                    request.repo_path,
                    file_path,
                    request.head_ref
                )
                
                # Detect language
                language = code_analyzer.detect_language(content, file_path)
                
                # Get context
                context = code_analyzer.extract_context(content, file_path)
                
                # Review file
                result = await review_service.review_code(
                    code=content,
                    language=language,
                    file_path=file_path,
                    model=ai_model,
                    config_name=request.config_name,
                    context=context,
                    user_id=request.user_id,
                    repository=request.repo_path,
                    commit_hash=git_service.get_commit_hash(request.repo_path, request.head_ref or "HEAD"),
                    db=db
                )
                
                results.append({
                    "file": file_path,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "file": file_path,
                    "error": str(e)
                })
        
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

