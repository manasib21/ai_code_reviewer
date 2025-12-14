"""
GitHub integration service
"""
import httpx
from typing import List, Dict, Optional
from app.core.config import settings

class GitHubService:
    """Service for GitHub API integration"""
    
    def __init__(self):
        self.token = settings.GITHUB_TOKEN
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        } if self.token else {}
    
    async def create_pr_comment(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        body: str,
        commit_id: Optional[str] = None,
        path: Optional[str] = None,
        line: Optional[int] = None
    ) -> Dict:
        """Create a comment on a pull request"""
        if not self.token:
            raise ValueError("GitHub token not configured")
        
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/comments"
        
        data = {"body": body}
        if commit_id and path and line:
            data["commit_id"] = commit_id
            data["path"] = path
            data["line"] = line
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
    
    async def post_review_comment(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        body: str,
        commit_id: str,
        path: str,
        line: int
    ) -> Dict:
        """Post a review comment on a specific line"""
        if not self.token:
            raise ValueError("GitHub token not configured")
        
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/comments"
        
        data = {
            "body": body,
            "commit_id": commit_id,
            "path": path,
            "line": line
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
    
    async def create_review(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        body: str,
        event: str = "COMMENT",
        comments: Optional[List[Dict]] = None
    ) -> Dict:
        """Create a PR review with comments"""
        if not self.token:
            raise ValueError("GitHub token not configured")
        
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        
        data = {
            "body": body,
            "event": event  # APPROVE, REQUEST_CHANGES, COMMENT
        }
        
        if comments:
            data["comments"] = comments
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()

github_service = GitHubService()

