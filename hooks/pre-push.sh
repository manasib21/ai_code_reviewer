#!/bin/bash

# Pre-push hook for AI Code Review
# This hook reviews commits before pushing

set -e

API_URL="${AI_CODE_REVIEW_API_URL:-http://localhost:8000}"
MODEL="${AI_CODE_REVIEW_MODEL:-gpt-4}"

echo "Running AI Code Review on commits to be pushed..."

# Get commits to be pushed
LOCAL_REF="$1"
REMOTE_REF="$2"

if [ -z "$LOCAL_REF" ] || [ -z "$REMOTE_REF" ]; then
    echo "No commits to review"
    exit 0
fi

# Get diff between local and remote
DIFF=$(git diff "$REMOTE_REF".."$LOCAL_REF" --name-only)

if [ -z "$DIFF" ]; then
    echo "No changes to review"
    exit 0
fi

echo "Reviewing changes in:"
echo "$DIFF"

# Get full diff
FULL_DIFF=$(git diff "$REMOTE_REF".."$LOCAL_REF")

# Call API to review diff
RESPONSE=$(curl -s -X POST "$API_URL/api/v1/git/review-diff" \
    -H "Content-Type: application/json" \
    -d "{
        \"repo_path\": \"$(pwd)\",
        \"base_ref\": \"$REMOTE_REF\",
        \"head_ref\": \"$LOCAL_REF\",
        \"model\": \"$MODEL\"
    }" 2>/dev/null || echo "{}")

ISSUES_COUNT=$(echo "$RESPONSE" | jq -r '.review.summary.total_issues // 0' 2>/dev/null || echo "0")
SCORE=$(echo "$RESPONSE" | jq -r '.review.overall_score // 100' 2>/dev/null || echo "100")

echo ""
echo "Review Summary:"
echo "  Total Issues: $ISSUES_COUNT"
echo "  Overall Score: $SCORE/100"

# Optionally block push if issues found
# Uncomment the following lines to block pushes with issues:
# if [ "$ISSUES_COUNT" -gt 10 ]; then
#     echo ""
#     echo "Code review found $ISSUES_COUNT issues. Push blocked."
#     echo "Review the issues or use --no-verify to skip."
#     exit 1
# fi

exit 0

