# Quick Start Guide

Get up and running with the AI Code Review Tool in 5 minutes!

## 1. Backend Setup (2 minutes)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your API keys
python main.py
```

Backend will run on `http://localhost:8000`

## 2. Frontend Setup (1 minute)

```bash
cd frontend
npm install
npm run dev
```

Frontend will run on `http://localhost:3000`

## 3. Test It Out!

1. Open `http://localhost:3000` in your browser
2. Paste some code or upload a file
3. Click "Review Code"
4. View the results!

## Example API Call

```bash
curl -X POST http://localhost:8000/api/v1/reviews/ \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def add(a, b):\n    return a + b\n    print(\"done\")",
    "language": "python",
    "model": "gpt-4"
  }'
```

## VS Code Extension

1. Open the `extension` folder in VS Code
2. Press `F5` to launch extension development host
3. Open a code file
4. Press `Ctrl+Shift+P` → "Review Current File"

## Git Hooks (Optional)

```bash
cp hooks/pre-commit.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

Now reviews will run automatically before commits!

## Next Steps

- Read [SETUP.md](SETUP.md) for detailed configuration
- Check [FEATURES.md](FEATURES.md) for all features
- Configure custom rules in the web UI
- Set up CI/CD integration

## Troubleshooting

**Backend won't start?**
- Check port 8000 is free
- Verify API keys in `.env`

**Frontend can't connect?**
- Ensure backend is running
- Check browser console for errors

**API errors?**
- Verify API keys are valid
- Check API service status

