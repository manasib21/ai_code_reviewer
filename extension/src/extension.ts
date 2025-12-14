import * as vscode from 'vscode';
import axios from 'axios';
import { ReviewPanel } from './reviewPanel';

export function activate(context: vscode.ExtensionContext) {
    const config = vscode.workspace.getConfiguration('aiCodeReview');
    const apiUrl = config.get<string>('apiUrl', 'http://localhost:8000');
    const model = config.get<string>('model', 'gpt-4');

    const reviewFile = async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor');
            return;
        }

        const document = editor.document;
        const code = document.getText();
        const filePath = document.fileName;

        await performReview(code, filePath, model, apiUrl);
    };

    const reviewSelection = async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor');
            return;
        }

        const selection = editor.selection;
        if (selection.isEmpty) {
            vscode.window.showWarningMessage('No text selected');
            return;
        }

        const code = editor.document.getText(selection);
        const filePath = editor.document.fileName;

        await performReview(code, filePath, model, apiUrl);
    };

    const reviewWorkspace = async () => {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            vscode.window.showErrorMessage('No workspace folder open');
            return;
        }

        vscode.window.showInformationMessage('Reviewing workspace... This may take a while.');

        // This would need to be implemented to review all files
        // For now, just show a message
        vscode.window.showInformationMessage('Workspace review feature coming soon');
    };

    const performReview = async (code: string, filePath: string, model: string, apiUrl: string) => {
        try {
            vscode.window.showInformationMessage('Reviewing code...');

            const response = await axios.post(`${apiUrl}/api/v1/reviews/`, {
                code,
                file_path: filePath,
                model,
            });

            const reviewResult = response.data;
            
            // Show results in a webview panel
            ReviewPanel.createOrShow(context.extensionUri, reviewResult);

            // Show summary in status bar
            const totalIssues = reviewResult.summary?.total_issues || 0;
            const score = reviewResult.overall_score || 100;
            
            if (totalIssues > 0) {
                vscode.window.showWarningMessage(
                    `Review complete: ${totalIssues} issues found (Score: ${score.toFixed(0)}/100)`
                );
            } else {
                vscode.window.showInformationMessage(
                    `Review complete: No issues found! (Score: ${score.toFixed(0)}/100)`
                );
            }
        } catch (error: any) {
            vscode.window.showErrorMessage(
                `Review failed: ${error.response?.data?.detail || error.message}`
            );
        }
    };

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('aiCodeReview.reviewFile', reviewFile),
        vscode.commands.registerCommand('aiCodeReview.reviewSelection', reviewSelection),
        vscode.commands.registerCommand('aiCodeReview.reviewWorkspace', reviewWorkspace)
    );

    // Auto-review on save if enabled
    if (config.get<boolean>('autoReview', false)) {
        context.subscriptions.push(
            vscode.workspace.onDidSaveTextDocument(async (document) => {
                if (document.languageId !== 'plaintext') {
                    const code = document.getText();
                    await performReview(code, document.fileName, model, apiUrl);
                }
            })
        );
    }
}

export function deactivate() {}

