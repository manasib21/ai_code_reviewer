import * as vscode from 'vscode';

export class ReviewPanel {
    public static currentPanel: ReviewPanel | undefined;
    public static readonly viewType = 'aiCodeReview';

    private readonly _panel: vscode.WebviewPanel;
    private readonly _extensionUri: vscode.Uri;
    private _disposables: vscode.Disposable[] = [];

    public static createOrShow(extensionUri: vscode.Uri, reviewResult: any) {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;

        if (ReviewPanel.currentPanel) {
            ReviewPanel.currentPanel._panel.reveal(column);
            ReviewPanel.currentPanel._update(reviewResult);
            return;
        }

        const panel = vscode.window.createWebviewPanel(
            ReviewPanel.viewType,
            'Code Review Results',
            column || vscode.ViewColumn.One,
            {
                enableScripts: true,
                localResourceRoots: [extensionUri]
            }
        );

        ReviewPanel.currentPanel = new ReviewPanel(panel, extensionUri, reviewResult);
    }

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri, reviewResult: any) {
        this._panel = panel;
        this._extensionUri = extensionUri;

        this._update(reviewResult);

        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
    }

    private _update(reviewResult: any) {
        const webview = this._panel.webview;
        this._panel.webview.html = this._getHtmlForWebview(webview, reviewResult);
    }

    private _getHtmlForWebview(webview: vscode.Webview, reviewResult: any): string {
        const issues = reviewResult.issues || [];
        const summary = reviewResult.summary || {};
        const score = reviewResult.overall_score || 100;

        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Review Results</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            padding: 20px;
            color: var(--vscode-foreground);
        }
        .score {
            text-align: center;
            padding: 20px;
            background: var(--vscode-editor-background);
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .score-value {
            font-size: 48px;
            font-weight: bold;
            color: var(--vscode-textLink-foreground);
        }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
            gap: 10px;
            margin-bottom: 20px;
        }
        .summary-item {
            padding: 10px;
            background: var(--vscode-editor-background);
            border-radius: 4px;
            text-align: center;
        }
        .issue {
            border: 1px solid var(--vscode-panel-border);
            border-radius: 4px;
            padding: 15px;
            margin-bottom: 15px;
            background: var(--vscode-editor-background);
        }
        .issue-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        .issue-type {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }
        .severity-critical { background: #c0392b; color: white; }
        .severity-high { background: #e74c3c; color: white; }
        .severity-medium { background: #f39c12; color: white; }
        .severity-low { background: #95a5a6; color: white; }
    </style>
</head>
<body>
    <div class="score">
        <div class="score-value">${score.toFixed(0)}/100</div>
        <div>Overall Score</div>
    </div>
    
    <div class="summary">
        <div class="summary-item">
            <div style="font-size: 24px; font-weight: bold;">${summary.total_issues || 0}</div>
            <div>Total Issues</div>
        </div>
        <div class="summary-item">
            <div style="font-size: 24px; font-weight: bold;">${summary.by_type?.bug || 0}</div>
            <div>Bugs</div>
        </div>
        <div class="summary-item">
            <div style="font-size: 24px; font-weight: bold;">${summary.by_type?.security || 0}</div>
            <div>Security</div>
        </div>
        <div class="summary-item">
            <div style="font-size: 24px; font-weight: bold;">${summary.by_type?.style || 0}</div>
            <div>Style</div>
        </div>
        <div class="summary-item">
            <div style="font-size: 24px; font-weight: bold;">${summary.by_type?.documentation || 0}</div>
            <div>Documentation</div>
        </div>
    </div>
    
    <h2>Issues Found</h2>
    ${issues.length === 0 
        ? '<p>No issues found! Great job!</p>'
        : issues.map((issue: any) => `
            <div class="issue">
                <div class="issue-header">
                    <span class="issue-type">${issue.type}</span>
                    <span class="severity-${issue.severity}">${issue.severity}</span>
                </div>
                <div><strong>Line ${issue.line}${issue.column ? `, Column ${issue.column}` : ''}</strong></div>
                <div style="margin-top: 10px;">${issue.description}</div>
                ${issue.suggestion ? `<div style="margin-top: 10px; padding: 10px; background: var(--vscode-textBlockQuote-background); border-left: 3px solid var(--vscode-textLink-foreground);"><strong>Suggestion:</strong> ${issue.suggestion}</div>` : ''}
                ${issue.explanation ? `<div style="margin-top: 10px; padding: 10px; background: var(--vscode-textBlockQuote-background);"><strong>Learning:</strong> ${issue.explanation}</div>` : ''}
            </div>
        `).join('')
    }
</body>
</html>`;
    }

    public dispose() {
        ReviewPanel.currentPanel = undefined;
        this._panel.dispose();
        while (this._disposables.length) {
            const x = this._disposables.pop();
            if (x) {
                x.dispose();
            }
        }
    }
}

