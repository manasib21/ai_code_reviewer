# AI Code Review Tool - Backend

FastAPI backend for the AI Code Review Tool.

## Features

- RESTful API for code reviews
- Support for OpenAI GPT and Anthropic Claude models
- Database persistence with SQLAlchemy
- HTML report generation
- Git integration
- GitHub/GitLab integration
- Configuration management
- History tracking
- API usage audit

## API Endpoints

### Reviews
- `POST /api/v1/reviews/` - Create a new review
- `GET /api/v1/reviews/{review_id}` - Get review by ID
- `GET /api/v1/reviews/{review_id}/report` - Get HTML report

### Files
- `POST /api/v1/files/review` - Review a single file
- `POST /api/v1/files/review-batch` - Review multiple files

### Git
- `POST /api/v1/git/review-diff` - Review git diff
- `POST /api/v1/git/review-files` - Review changed files

### Configuration
- `GET /api/v1/config/` - List configurations
- `GET /api/v1/config/{config_name}` - Get configuration
- `POST /api/v1/config/` - Create/update configuration

### History
- `GET /api/v1/history/` - Get review history
- `GET /api/v1/history/{review_id}/history` - Get review history details

### Collaboration
- `POST /api/v1/collaboration/comments` - Add comment to issue
- `GET /api/v1/collaboration/issues/{issue_id}/comments` - Get issue comments
- `PATCH /api/v1/collaboration/issues/{issue_id}/status` - Update issue status

### Audit
- `GET /api/v1/audit/usage` - Get API usage statistics
- `GET /api/v1/audit/usage/detailed` - Get detailed usage log

## Development

See main SETUP.md for installation instructions.

## Environment Variables

- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic API key
- `DATABASE_URL` - Database connection string
- `GITHUB_TOKEN` - GitHub token for PR integration
- `GITLAB_TOKEN` - GitLab token for MR integration

