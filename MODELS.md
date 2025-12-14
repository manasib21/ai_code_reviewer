# AI Model Configuration Guide

## Available Models

### OpenAI Models (Require OpenAI API Key)

1. **gpt-3.5-turbo** (Default - Recommended for free tier)
   - Available to all OpenAI users
   - Fast and cost-effective
   - Good for most code reviews

2. **gpt-4o-mini** (Recommended for paid tier)
   - Latest GPT-4 variant
   - More capable than GPT-3.5
   - Lower cost than full GPT-4

3. **gpt-4o** (Latest GPT-4)
   - Most capable OpenAI model
   - Best for complex code reviews
   - Requires paid OpenAI account

4. **gpt-4** (Legacy)
   - Original GPT-4 model
   - Requires paid OpenAI account
   - May be deprecated

5. **gpt-4-turbo-preview** (Legacy)
   - Older GPT-4 variant
   - Requires paid OpenAI account

### Anthropic Models (Require Anthropic API Key)

1. **claude-3-sonnet-20240229** (Recommended)
   - Balanced performance and cost
   - Excellent for code reviews

2. **claude-3-opus-20240229**
   - Most capable Claude model
   - Best for complex reviews

3. **claude-3-haiku-20240307**
   - Fastest and cheapest
   - Good for simple reviews

## How to Change the Model

### Option 1: Web Interface
The web interface uses `gpt-3.5-turbo` by default. To change it, you'll need to modify the frontend code or use the API directly.

### Option 2: API Request
When making API requests, specify the model:

```bash
curl -X POST http://localhost:8000/api/v1/reviews/ \
  -H "Content-Type: application/json" \
  -d '{
    "code": "your code here",
    "model": "gpt-4o-mini"
  }'
```

### Option 3: Update Default in Code
Edit these files to change the default:

- `backend/app/routers/files.py` - Line 20: `model: str = Form("gpt-3.5-turbo")`
- `backend/app/routers/reviews.py` - Line 23: `model: str = "gpt-3.5-turbo"`
- `frontend/src/pages/Home.tsx` - Update model in FormData

## Model Access Requirements

- **Free Tier**: `gpt-3.5-turbo` only
- **Paid Tier**: All OpenAI models
- **Anthropic**: Requires separate API key and account

## Recommendations

- **Free Tier Users**: Use `gpt-3.5-turbo` (default)
- **Paid OpenAI Users**: Use `gpt-4o-mini` for best balance
- **Anthropic Users**: Use `claude-3-sonnet-20240229`

