# .env File Creation Guide

## How the .env File is Created

The `.env` file can be created in **three ways**:

### Method 1: Manual Creation (Recommended for First Setup)

1. **Copy from example:**
   ```bash
   cd backend
   cp .env.example .env
   ```

2. **Or create manually:**
   ```bash
   cd backend
   touch .env
   ```

3. **Edit the file** and add your API keys:
   ```env
   OPENAI_API_KEY=sk-your-key-here
   ANTHROPIC_API_KEY=your-key-here
   ```

### Method 2: Automatic Creation via API Key Service

The `.env` file is **automatically created** when you:
- Use the web interface to update API keys in the Config/Settings tab
- The `APIKeyService.update_api_keys()` method creates the file if it doesn't exist

**Code location:** `backend/app/services/api_key_service.py` (lines 34-37)

```python
if not self.env_file.exists():
    # Create .env file if it doesn't exist
    self.env_file.parent.mkdir(parents=True, exist_ok=True)
    self.env_file.touch()
```

### Method 3: Automatic Creation on First API Key Update

When you update API keys through the web interface:
1. If `.env` doesn't exist, it's created automatically
2. The API keys are written to the file
3. Other configuration values use defaults from `Settings` class

## File Location

- **Path:** `backend/.env`
- **Full path:** `/Users/manasi/code review tool/backend/.env`
- **Note:** The file is in `.gitignore` and will NOT be committed to git

## How Settings are Loaded

The `Settings` class in `backend/app/core/config.py` automatically loads from `.env`:

```python
class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    # ... other settings
    
    class Config:
        env_file = ".env"  # Loads from backend/.env
```

**How it works:**
1. `pydantic-settings` looks for `.env` in the current working directory
2. When the backend starts, it reads from `backend/.env`
3. Environment variables take precedence over `.env` file values
4. If `.env` doesn't exist, it uses default values (empty strings for API keys)

## Current .env File Status

To check if your `.env` file exists:
```bash
cd backend
ls -la .env
```

To view current API key status (masked):
```bash
curl http://localhost:8000/api/v1/config/api-keys
```

## Best Practices

1. **Never commit `.env` to git** (already in `.gitignore`)
2. **Use `.env.example`** as a template for other developers
3. **Update via web UI** - The Settings tab provides a safe way to update keys
4. **Restart backend** after updating keys for changes to take effect

## Troubleshooting

**File not found?**
- Check you're in the `backend` directory
- The file might be hidden (starts with `.`)
- Use `ls -la` to see hidden files

**Keys not loading?**
- Verify the file is named exactly `.env` (not `env` or `.env.txt`)
- Check file permissions: `chmod 600 .env` (read/write for owner only)
- Restart the backend after creating/updating the file

**Keys updated but not working?**
- Backend must be restarted to reload environment variables
- Check the file format (no spaces around `=`)
- Verify keys are on separate lines

