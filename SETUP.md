# Setup Guide

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL (optional, SQLite used by default)
- OpenAI API key or Anthropic API key

## Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
```

5. Edit `.env` and add your API keys:
```
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

6. Run the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## VS Code Extension Setup

1. Navigate to the extension directory:
```bash
cd extension
```

2. Install dependencies:
```bash
npm install
```

3. Compile the extension:
```bash
npm run compile
```

4. Press F5 in VS Code to launch the extension in a new window

5. Or package the extension:
```bash
vsce package
```

## Git Hooks Setup

1. Copy hooks to your repository:
```bash
cp hooks/pre-commit.sh .git/hooks/pre-commit
cp hooks/pre-push.sh .git/hooks/pre-push
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/pre-push
```

2. Set environment variables (optional):
```bash
export AI_CODE_REVIEW_API_URL=http://localhost:8000
export AI_CODE_REVIEW_MODEL=gpt-4
```

## CI/CD Setup

### GitHub Actions

1. Copy the workflow file to your repository:
```bash
cp ci-cd/github-actions.yml .github/workflows/code-review.yml
```

2. Add secrets to your GitHub repository:
   - `OPENAI_API_KEY`
   - `ANTHROPIC_API_KEY`

### GitLab CI

1. Copy the CI file to your repository:
```bash
cp ci-cd/gitlab-ci.yml .gitlab-ci.yml
```

2. Add CI/CD variables:
   - `GITLAB_TOKEN`
   - `OPENAI_API_KEY`
   - `ANTHROPIC_API_KEY`

## Configuration

1. Copy the example config:
```bash
cp config/config.example.yaml config/config.yaml
```

2. Edit `config/config.yaml` to customize review settings

## Usage

### Web Interface

1. Open `http://localhost:3000`
2. Paste code or upload a file
3. Click "Review Code"
4. View results and download HTML report

### API

```bash
# Review code
curl -X POST http://localhost:8000/api/v1/reviews/ \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def hello():\n    print(\"world\")",
    "language": "python",
    "model": "gpt-4"
  }'
```

### VS Code Extension

1. Open a file in VS Code
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
3. Type "Review Current File" or "Review Selection"
4. View results in the webview panel

## Troubleshooting

### Backend won't start
- Check that port 8000 is available
- Verify API keys are set in `.env`
- Ensure all dependencies are installed

### Frontend won't connect
- Verify backend is running on port 8000
- Check CORS settings in backend config

### Git hooks not working
- Ensure hooks are executable (`chmod +x`)
- Check that API URL is accessible
- Verify `jq` is installed (for JSON parsing)

## Production Deployment

1. Set `DEBUG=False` in backend `.env`
2. Use PostgreSQL instead of SQLite
3. Set proper `SECRET_KEY`
4. Configure proper CORS origins
5. Use a reverse proxy (nginx) for production
6. Set up SSL/TLS certificates

