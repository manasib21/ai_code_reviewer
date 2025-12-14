#!/usr/bin/env python3
"""
GitLab MR review script for CI/CD
"""
import argparse
import requests
import sys
import os

def review_mr(api_url, gitlab_token, project_id, mr_iid, gitlab_url="https://gitlab.com"):
    """Review a GitLab merge request"""
    
    headers = {
        "PRIVATE-TOKEN": gitlab_token
    }
    
    # Get MR info
    mr_url = f"{gitlab_url}/api/v4/projects/{project_id}/merge_requests/{mr_iid}"
    response = requests.get(mr_url, headers=headers)
    response.raise_for_status()
    mr_data = response.json()
    
    # Get MR changes
    changes_url = f"{mr_url}/changes"
    changes_response = requests.get(changes_url, headers=headers)
    changes_data = changes_response.json()
    
    # Review each changed file
    all_issues = []
    
    for change in changes_data.get("changes", []):
        file_path = change["new_path"]
        diff = change["diff"]
        
        # Review the diff
        review_url = f"{api_url}/api/v1/reviews/"
        review_data = {
            "code": diff,
            "language": "diff",
            "file_path": file_path,
            "model": "gpt-4",
            "context": f"MR !{mr_iid}: {mr_data['title']}"
        }
        
        review_response = requests.post(review_url, json=review_data)
        review_response.raise_for_status()
        review_result = review_response.json()
        
        all_issues.extend(review_result.get("issues", []))
    
    # Post comments to MR
    for issue in all_issues:
        comment_body = f"""**{issue['type'].upper()} - {issue['severity'].upper()}** (Line {issue['line']})
        
{issue['description']}

"""
        if issue.get("suggestion"):
            comment_body += f"💡 **Suggestion:** {issue['suggestion']}\n\n"
        if issue.get("explanation"):
            comment_body += f"📚 **Learning:** {issue['explanation']}\n"
        
        notes_url = f"{gitlab_url}/api/v4/projects/{project_id}/merge_requests/{mr_iid}/notes"
        note_data = {"body": comment_body}
        
        requests.post(notes_url, headers=headers, json=note_data)
    
    # Generate summary
    total_issues = len(all_issues)
    print(f"Review complete: {total_issues} issues found")
    
    # Generate HTML report (simplified)
    with open("review-report.html", "w") as f:
        f.write(f"<html><body><h1>Code Review Report</h1><p>Total Issues: {total_issues}</p></body></html>")
    
    return total_issues

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Review GitLab MR")
    parser.add_argument("--api-url", required=True)
    parser.add_argument("--gitlab-token", required=True)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--mr-iid", type=int, required=True)
    parser.add_argument("--gitlab-url", default="https://gitlab.com")
    
    args = parser.parse_args()
    
    try:
        issues = review_mr(
            args.api_url,
            args.gitlab_token,
            args.project_id,
            args.mr_iid,
            args.gitlab_url
        )
        
        if issues > 20:
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

