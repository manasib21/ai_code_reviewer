"""
Configuration API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.config_service import config_service
from app.core.config import settings
from app.core.ai_providers import AIModel
from app.services.api_key_service import api_key_service

router = APIRouter()

class ConfigRequest(BaseModel):
    name: str
    config_data: Dict
    user_id: Optional[str] = None
    team_id: Optional[str] = None
    is_default: bool = False

@router.get("/available-models")
async def get_available_models():
    """Get list of available models based on configured API keys"""
    available_models = []
    
    # Check OpenAI models
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip():
        available_models.extend([
            {"value": "gpt-3.5-turbo", "label": "GPT-3.5 Turbo (Free Tier)", "provider": "OpenAI"},
            {"value": "gpt-4o-mini", "label": "GPT-4o Mini", "provider": "OpenAI"},
            {"value": "gpt-4o", "label": "GPT-4o", "provider": "OpenAI"},
            {"value": "gpt-4", "label": "GPT-4", "provider": "OpenAI"},
            {"value": "gpt-4-turbo-preview", "label": "GPT-4 Turbo Preview", "provider": "OpenAI"},
        ])
    
    # Check Anthropic models
    if settings.ANTHROPIC_API_KEY and settings.ANTHROPIC_API_KEY.strip():
        available_models.extend([
            {"value": "claude-3-haiku-20240307", "label": "Claude 3 Haiku", "provider": "Anthropic"},
            {"value": "claude-3-sonnet-20240229", "label": "Claude 3 Sonnet", "provider": "Anthropic"},
            {"value": "claude-3-opus-20240229", "label": "Claude 3 Opus", "provider": "Anthropic"},
        ])
    
    # If no keys configured, show a message
    if not available_models:
        return {
            "models": [],
            "message": "No API keys configured. Please add OPENAI_API_KEY or ANTHROPIC_API_KEY to your .env file."
        }
    
    return {
        "models": available_models,
        "default": available_models[0]["value"] if available_models else "gpt-3.5-turbo"
    }

@router.post("/")
async def create_config(
    request: ConfigRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create or update a configuration"""
    try:
        config = await config_service.save_config(
            name=request.name,
            config_data=request.config_data,
            user_id=request.user_id,
            team_id=request.team_id,
            is_default=request.is_default,
            db=db
        )
        return {
            "id": config.id,
            "name": config.name,
            "config_data": config.config_data,
            "is_default": config.is_default
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_configs(
    user_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all configurations"""
    from sqlalchemy import select
    from app.core.models import Configuration
    
    query = select(Configuration)
    if user_id:
        query = query.where(Configuration.user_id == user_id)
    
    result = await db.execute(query)
    configs = result.scalars().all()
    
    return [
        {
            "id": c.id,
            "name": c.name,
            "is_default": c.is_default,
            "created_at": c.created_at.isoformat()
        }
        for c in configs
    ]

class APIKeyUpdateRequest(BaseModel):
    openai_key: Optional[str] = None
    anthropic_key: Optional[str] = None

@router.get("/api-keys")
async def get_api_keys_status():
    """Get API keys status (masked)"""
    return api_key_service.get_api_keys_status()

@router.put("/api-keys")
async def update_api_keys(request: APIKeyUpdateRequest):
    """Update API keys"""
    try:
        result = api_key_service.update_api_keys(
            openai_key=request.openai_key,
            anthropic_key=request.anthropic_key
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update API keys: {str(e)}")

@router.get("/{config_name}")
async def get_config(
    config_name: str,
    user_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get a configuration by name"""
    config = await config_service.get_config(config_name, user_id, db)
    return config
