#!/usr/bin/env python3
"""
GitHub PR review script for CI/CD
"""
import argparse
import requests
import sys
from pathlib import Path

def review_pr(api_url, github_token, pr_number, repo_owner, repo_name):
    """Review a GitHub pull request"""
    
    # Get PR diff
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3.diff"
    }
    
    diff_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}"
    response = requests.get(diff_url, headers=headers)
    response.raise_for_status()
    pr_data = response.json()
    
    # Get diff
    diff_response = requests.get(pr_data["diff_url"], headers=headers)
    diff = diff_response.text
    
    # Review the diff
    review_url = f"{api_url}/api/v1/reviews/"
    review_data = {
        "code": diff,
        "language": "diff",
        "file_path": "PR diff",
        "model": "gpt-4",
        "context": f"PR #{pr_number}: {pr_data['title']}"
    }
    
    review_response = requests.post(review_url, json=review_data)
    review_response.raise_for_status()
    review_result = review_response.json()
    
    # Post comments to PR
    comments_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/comments"
    
    for issue in review_result.get("issues", []):
        comment_body = f"""**{issue['type'].upper()} - {issue['severity'].upper()}** (Line {issue['line']})
        
{issue['description']}

"""
        if issue.get("suggestion"):
            comment_body += f"💡 **Suggestion:** {issue['suggestion']}\n\n"
        if issue.get("explanation"):
            comment_body += f"📚 **Learning:** {issue['explanation']}\n"
        
        comment_data = {
            "body": comment_body,
            "commit_id": pr_data["head"]["sha"],
            "path": issue.get("file_path", ""),
            "line": issue["line"]
        }
        
        requests.post(comments_url, headers=headers, json=comment_data)
    
    # Generate HTML report
    report_url = f"{api_url}/api/v1/reviews/{review_result['review_id']}/report"
    report_response = requests.get(report_url)
    
    with open("review-report.html", "w") as f:
        f.write(report_response.text)
    
    # Summary
    total_issues = review_result["summary"]["total_issues"]
    score = review_result["overall_score"]
    
    print(f"Review complete: {total_issues} issues found, Score: {score}/100")
    
    return total_issues, score

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Review GitHub PR")
    parser.add_argument("--api-url", required=True)
    parser.add_argument("--github-token", required=True)
    parser.add_argument("--pr-number", type=int, required=True)
    parser.add_argument("--repo-owner", default="")
    parser.add_argument("--repo-name", default="")
    
    args = parser.parse_args()
    
    # Try to get repo info from environment if not provided
    repo_owner = args.repo_owner or ""
    repo_name = args.repo_name or ""
    
    if not repo_owner or not repo_name:
        print("Error: repo-owner and repo-name required")
        sys.exit(1)
    
    try:
        issues, score = review_pr(
            args.api_url,
            args.github_token,
            args.pr_number,
            repo_owner,
            repo_name
        )
        
        # Exit with error if too many issues
        if issues > 20:
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

