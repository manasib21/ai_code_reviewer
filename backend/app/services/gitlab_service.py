"""
GitLab integration service
"""
import httpx
from typing import List, Dict, Optional
from app.core.config import settings

class GitLabService:
    """Service for GitLab API integration"""
    
    def __init__(self):
        self.token = settings.GITLAB_TOKEN
        self.base_url = settings.GITLAB_URL if hasattr(settings, "GITLAB_URL") else "https://gitlab.com/api/v4"
        self.headers = {
            "PRIVATE-TOKEN": self.token
        } if self.token else {}
    
    async def create_mr_comment(
        self,
        project_id: str,
        mr_iid: int,
        body: str
    ) -> Dict:
        """Create a comment on a merge request"""
        if not self.token:
            raise ValueError("GitLab token not configured")
        
        url = f"{self.base_url}/projects/{project_id}/merge_requests/{mr_iid}/notes"
        
        data = {"body": body}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
    
    async def post_review_comment(
        self,
        project_id: str,
        mr_iid: int,
        body: str,
        position: Dict
    ) -> Dict:
        """Post a review comment on a specific position"""
        if not self.token:
            raise ValueError("GitLab token not configured")
        
        url = f"{self.base_url}/projects/{project_id}/merge_requests/{mr_iid}/discussions"
        
        data = {
            "body": body,
            "position": position
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()

gitlab_service = GitLabService()

