"""
Git integration service for diff-based reviews
"""
import subprocess
from typing import List, Dict, Optional
from pathlib import Path

class GitService:
    """Service for Git operations"""
    
    def get_diff(self, repo_path: str, base_ref: Optional[str] = None, head_ref: Optional[str] = None) -> str:
        """Get git diff"""
        try:
            if base_ref and head_ref:
                cmd = ["git", "diff", base_ref, head_ref]
            elif base_ref:
                cmd = ["git", "diff", base_ref]
            else:
                cmd = ["git", "diff", "HEAD"]
            
            result = subprocess.run(
                cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise Exception(f"Git diff failed: {e.stderr}")
    
    def get_changed_files(self, repo_path: str, base_ref: Optional[str] = None, head_ref: Optional[str] = None) -> List[str]:
        """Get list of changed files"""
        try:
            if base_ref and head_ref:
                cmd = ["git", "diff", "--name-only", base_ref, head_ref]
            elif base_ref:
                cmd = ["git", "diff", "--name-only", base_ref]
            else:
                cmd = ["git", "diff", "--name-only", "HEAD"]
            
            result = subprocess.run(
                cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return [f.strip() for f in result.stdout.split("\n") if f.strip()]
        except subprocess.CalledProcessError as e:
            raise Exception(f"Git diff failed: {e.stderr}")
    
    def get_file_content(self, repo_path: str, file_path: str, ref: Optional[str] = None) -> str:
        """Get file content at specific ref"""
        try:
            if ref:
                cmd = ["git", "show", f"{ref}:{file_path}"]
            else:
                cmd = ["cat", str(Path(repo_path) / file_path)]
            
            result = subprocess.run(
                cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to get file content: {e.stderr}")
    
    def get_commit_hash(self, repo_path: str, ref: str = "HEAD") -> str:
        """Get commit hash for ref"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", ref],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to get commit hash: {e.stderr}")

git_service = GitService()

