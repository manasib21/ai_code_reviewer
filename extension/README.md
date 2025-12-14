# AI Code Review - VS Code Extension

VS Code extension for AI-powered code reviews.

## Features

- Review current file
- Review selected code
- Review entire workspace
- View review results in webview
- Auto-review on save (optional)

## Installation

1. Open VS Code
2. Press `F5` to run in development mode
3. Or package and install: `vsce package` then install the `.vsix` file

## Usage

1. Open a code file
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
3. Select "Review Current File" or "Review Selection"
4. View results in the webview panel

## Configuration

- `aiCodeReview.apiUrl` - API URL (default: http://localhost:8000)
- `aiCodeReview.model` - AI model to use
- `aiCodeReview.autoReview` - Auto-review on save

## Development

```bash
npm install
npm run compile
```

Press F5 in VS Code to launch extension development host.

