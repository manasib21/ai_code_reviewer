"""
File-based review endpoints
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import aiofiles

from app.database import get_db
from app.services.review_service import review_service
from app.core.ai_providers import AIModel
from app.services.code_analyzer import CodeAnalyzer

router = APIRouter()
code_analyzer = CodeAnalyzer()

@router.post("/review")
async def review_file(
    file: UploadFile = File(...),
    model: str = Form("gpt-3.5-turbo"),  # Default to gpt-3.5-turbo (available to free tier)
    config_name: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Review a single file"""
    try:
        # Read file content
        content = await file.read()
        
        # Try to decode as UTF-8, fallback to other encodings if needed
        try:
            code = content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                code = content.decode("latin-1")
            except UnicodeDecodeError:
                raise HTTPException(
                    status_code=400, 
                    detail="File encoding not supported. Please use UTF-8 encoded files."
                )
        
        if not code.strip():
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Detect language
        language = code_analyzer.detect_language(code, file.filename)
        
        if language == "unknown":
            # Try to detect from file extension
            if file.filename:
                ext = file.filename.split('.')[-1].lower()
                lang_map = {
                    'py': 'python', 'js': 'javascript', 'ts': 'typescript',
                    'java': 'java', 'go': 'go', 'rs': 'rust',
                    'cpp': 'cpp', 'cc': 'cpp', 'cxx': 'cpp', 'c': 'c',
                    'jsx': 'javascript', 'tsx': 'typescript'
                }
                language = lang_map.get(ext, 'unknown')
        
        # Get context
        context = code_analyzer.extract_context(code, file.filename)
        
        # Parse model
        try:
            ai_model = AIModel(model)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid model: {model}. Valid models: gpt-4, gpt-4o, gpt-4o-mini, gpt-3.5-turbo, claude-3-sonnet-20240229")
        
        # Perform review
        result = await review_service.review_code(
            code=code,
            language=language,
            file_path=file.filename,
            model=ai_model,
            config_name=config_name,
            context=context,
            user_id=user_id,
            db=db
        )
        
        return result
    except HTTPException:
        raise
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be text-based")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error reviewing file: {str(e)}")

@router.post("/review-batch")
async def review_files(
    files: List[UploadFile] = File(...),
    model: str = "gpt-3.5-turbo",
    config_name: str = None,
    user_id: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Review multiple files"""
    results = []
    
    try:
        ai_model = AIModel(model)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid model: {model}")
    
    for file in files:
        try:
            content = await file.read()
            code = content.decode("utf-8")
            language = code_analyzer.detect_language(code, file.filename)
            context = code_analyzer.extract_context(code, file.filename)
            
            result = await review_service.review_code(
                code=code,
                language=language,
                file_path=file.filename,
                model=ai_model,
                config_name=config_name,
                context=context,
                user_id=user_id,
                db=db
            )
            
            results.append({
                "file": file.filename,
                "result": result
            })
        except Exception as e:
            results.append({
                "file": file.filename,
                "error": str(e)
            })
    
    return {"results": results}

