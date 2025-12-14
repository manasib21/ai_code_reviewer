"""
Configuration service for managing custom rules and settings
"""
from typing import Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.models import Configuration

class ConfigService:
    """Service for managing review configurations"""
    
    DEFAULT_CONFIG = {
        "min_severity": "low",
        "ignore_patterns": [
            "node_modules",
            ".git",
            "__pycache__",
            "*.pyc",
            "*.min.js",
            "dist",
            "build"
        ],
        "custom_prompt": None,
        "coding_standards": {},
        "custom_rules": []
    }
    
    async def get_config(
        self,
        config_name: Optional[str],
        user_id: Optional[str],
        db: Optional[AsyncSession]
    ) -> Dict:
        """Get configuration by name or user default"""
        if not db:
            return self.DEFAULT_CONFIG.copy()
        
        if config_name:
            result = await db.execute(
                select(Configuration).where(Configuration.name == config_name)
            )
            config = result.scalar_one_or_none()
            if config:
                return {**self.DEFAULT_CONFIG, **config.config_data}
        
        # Try to get user's default config
        if user_id:
            result = await db.execute(
                select(Configuration).where(
                    Configuration.user_id == user_id,
                    Configuration.is_default == True
                )
            )
            config = result.scalar_one_or_none()
            if config:
                return {**self.DEFAULT_CONFIG, **config.config_data}
        
        return self.DEFAULT_CONFIG.copy()
    
    async def save_config(
        self,
        name: str,
        config_data: Dict,
        user_id: Optional[str] = None,
        team_id: Optional[str] = None,
        is_default: bool = False,
        db: Optional[AsyncSession] = None
    ) -> Configuration:
        """Save or update configuration"""
        if not db:
            raise ValueError("Database session required")
        
        result = await db.execute(
            select(Configuration).where(Configuration.name == name)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            existing.config_data = config_data
            existing.is_default = is_default
            if user_id:
                existing.user_id = user_id
            if team_id:
                existing.team_id = team_id
            await db.commit()
            await db.refresh(existing)
            return existing
        else:
            new_config = Configuration(
                name=name,
                user_id=user_id,
                team_id=team_id,
                config_data=config_data,
                is_default=is_default
            )
            db.add(new_config)
            await db.commit()
            await db.refresh(new_config)
            return new_config

config_service = ConfigService()

