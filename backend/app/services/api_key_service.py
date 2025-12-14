"""
Service for managing API keys
"""
import os
from pathlib import Path
from typing import Dict, Optional
from app.core.config import settings

class APIKeyService:
    """Service for managing API keys in .env file"""
    
    def __init__(self):
        # Default to backend/.env
        backend_dir = Path(__file__).parent.parent.parent
        self.env_file = backend_dir / ".env"
    
    def get_api_keys_status(self) -> Dict:
        """Get status of API keys (without revealing actual keys)"""
        return {
            "openai_configured": bool(settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip()),
            "anthropic_configured": bool(settings.ANTHROPIC_API_KEY and settings.ANTHROPIC_API_KEY.strip()),
            "openai_preview": self._mask_key(settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None,
            "anthropic_preview": self._mask_key(settings.ANTHROPIC_API_KEY) if settings.ANTHROPIC_API_KEY else None,
        }
    
    def _mask_key(self, key: str) -> str:
        """Mask API key for display (show first 7 and last 4 characters)"""
        if not key or len(key) < 12:
            return "***"
        return f"{key[:7]}...{key[-4:]}"
    
    def update_api_keys(self, openai_key: Optional[str] = None, anthropic_key: Optional[str] = None) -> Dict:
        """Update API keys in .env file"""
        if not self.env_file.exists():
            # Create .env file if it doesn't exist
            self.env_file.parent.mkdir(parents=True, exist_ok=True)
            self.env_file.touch()
        
        # Read existing .env file
        env_lines = []
        if self.env_file.exists():
            with open(self.env_file, 'r') as f:
                env_lines = f.readlines()
        
        # Track which keys we've updated
        openai_updated = False
        anthropic_updated = False
        
        # Update or add keys
        new_lines = []
        for line in env_lines:
            line_stripped = line.strip()
            if line_stripped.startswith('OPENAI_API_KEY='):
                if openai_key is not None:
                    new_lines.append(f'OPENAI_API_KEY={openai_key}\n')
                    openai_updated = True
                else:
                    new_lines.append(line)  # Keep existing
            elif line_stripped.startswith('ANTHROPIC_API_KEY='):
                if anthropic_key is not None:
                    new_lines.append(f'ANTHROPIC_API_KEY={anthropic_key}\n')
                    anthropic_updated = True
                else:
                    new_lines.append(line)  # Keep existing
            elif line_stripped and not line_stripped.startswith('#'):
                # Keep other non-comment lines
                new_lines.append(line)
            elif line_stripped.startswith('#'):
                # Keep comments
                new_lines.append(line)
        
        # Add keys that weren't in the file
        if openai_key is not None and not openai_updated:
            new_lines.append(f'OPENAI_API_KEY={openai_key}\n')
        if anthropic_key is not None and not anthropic_updated:
            new_lines.append(f'ANTHROPIC_API_KEY={anthropic_key}\n')
        
        # Write back to .env file
        with open(self.env_file, 'w') as f:
            f.writelines(new_lines)
        
        # Reload settings (note: this won't affect already-running processes)
        # The user will need to restart the backend for changes to take effect
        return {
            "success": True,
            "message": "API keys updated. Please restart the backend for changes to take effect.",
            "openai_updated": openai_key is not None,
            "anthropic_updated": anthropic_key is not None
        }

api_key_service = APIKeyService()

