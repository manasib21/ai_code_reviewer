#!/bin/bash

# Pre-commit hook for AI Code Review
# This hook reviews staged files before commit

set -e

API_URL="${AI_CODE_REVIEW_API_URL:-http://localhost:8000}"
MODEL="${AI_CODE_REVIEW_MODEL:-gpt-4}"

echo "Running AI Code Review on staged files..."

# Get list of staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

if [ -z "$STAGED_FILES" ]; then
    echo "No files staged for commit"
    exit 0
fi

REVIEW_FAILED=false
REVIEW_RESULTS=""

for FILE in $STAGED_FILES; do
    # Skip binary files
    if git diff --cached --numstat "$FILE" | grep -q '^-'; then
        continue
    fi
    
    # Get file content
    FILE_CONTENT=$(git show ":$FILE" 2>/dev/null || cat "$FILE")
    
    if [ -z "$FILE_CONTENT" ]; then
        continue
    fi
    
    echo "Reviewing $FILE..."
    
    # Call API to review file
    RESPONSE=$(curl -s -X POST "$API_URL/api/v1/reviews/" \
        -H "Content-Type: application/json" \
        -d "{
            \"code\": $(echo "$FILE_CONTENT" | jq -Rs .),
            \"file_path\": \"$FILE\",
            \"model\": \"$MODEL\"
        }" 2>/dev/null || echo "{}")
    
    # Check for issues
    ISSUES_COUNT=$(echo "$RESPONSE" | jq -r '.summary.total_issues // 0' 2>/dev/null || echo "0")
    SCORE=$(echo "$RESPONSE" | jq -r '.overall_score // 100' 2>/dev/null || echo "100")
    
    if [ "$ISSUES_COUNT" -gt 0 ]; then
        REVIEW_FAILED=true
        REVIEW_RESULTS="$REVIEW_RESULTS\n$FILE: $ISSUES_COUNT issues found (Score: $SCORE/100)"
    else
        REVIEW_RESULTS="$REVIEW_RESULTS\n$FILE: No issues found (Score: $SCORE/100)"
    fi
done

echo -e "$REVIEW_RESULTS"

# Optionally block commit if issues found
# Uncomment the following lines to block commits with issues:
# if [ "$REVIEW_FAILED" = true ]; then
#     echo ""
#     echo "Code review found issues. Commit blocked."
#     echo "Review the issues above or use --no-verify to skip."
#     exit 1
# fi

exit 0

