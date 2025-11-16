// deepseek-code/vscode_extension/src/extension.ts
import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { DeepSeekClient } from './deepseekClient';
import { ChatViewProvider } from './chatViewProvider';
import { CodeActionProvider } from './codeActionProvider';

export function activate(context: vscode.ExtensionContext) {
    console.log('DeepSeek-Code extension is now active!');

    // Initialize DeepSeek client
    const deepSeekClient = new DeepSeekClient();

    // Register Chat View Provider
    const chatViewProvider = new ChatViewProvider(context.extensionUri, deepSeekClient);
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider(
            ChatViewProvider.viewType,
            chatViewProvider
        )
    );

    // Register Code Action Provider
    const codeActionProvider = new CodeActionProvider(deepSeekClient);
    context.subscriptions.push(
        vscode.languages.registerCodeActionsProvider(
            { pattern: '**/*' },
            codeActionProvider
        )
    );

    // Register Commands
    context.subscriptions.push(
        vscode.commands.registerCommand('deepseek-code.startChat', () => {
            chatViewProvider.showChat();
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('deepseek-code.analyzeFile', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage('No active editor found');
                return;
            }

            const document = editor.document;
            const content = document.getText();
            const fileName = path.basename(document.fileName);

            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: `DeepSeek: Analyzing ${fileName}`,
                cancellable: false
            }, async (progress) => {
                try {
                    const analysis = await deepSeekClient.analyzeCode(content, document.languageId);
                    chatViewProvider.showAnalysis(analysis, fileName);
                } catch (error) {
                    vscode.window.showErrorMessage(`Analysis failed: ${error}`);
                }
            });
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('deepseek-code.refactorCode', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage('No active editor found');
                return;
            }

            const selection = editor.selection;
            const selectedText = editor.document.getText(selection);
            
            if (!selectedText) {
                vscode.window.showWarningMessage('Please select some code to refactor');
                return;
            }

            const instructions = await vscode.window.showInputBox({
                prompt: 'Enter refactoring instructions',
                placeHolder: 'e.g., Improve readability, optimize performance...'
            });

            if (!instructions) {
                return;
            }

            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'DeepSeek: Refactoring code',
                cancellable: false
            }, async (progress) => {
                try {
                    const refactored = await deepSeekClient.refactorCode(
                        selectedText, 
                        instructions, 
                        editor.document.languageId
                    );
                    
                    // Apply the refactored code
                    await editor.edit(editBuilder => {
                        editBuilder.replace(selection, refactored);
                    });
                    
                    vscode.window.showInformationMessage('Code refactored successfully!');
                } catch (error) {
                    vscode.window.showErrorMessage(`Refactoring failed: ${error}`);
                }
            });
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('deepseek-code.explainCode', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage('No active editor found');
                return;
            }

            const selection = editor.selection;
            const selectedText = editor.document.getText(selection);
            
            if (!selectedText) {
                vscode.window.showWarningMessage('Please select some code to explain');
                return;
            }

            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'DeepSeek: Explaining code',
                cancellable: false
            }, async (progress) => {
                try {
                    const explanation = await deepSeekClient.explainCode(
                        selectedText, 
                        editor.document.languageId
                    );
                    chatViewProvider.showExplanation(explanation, selectedText);
                } catch (error) {
                    vscode.window.showErrorMessage(`Explanation failed: ${error}`);
                }
            });
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('deepseek-code.generateTests', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage('No active editor found');
                return;
            }

            const document = editor.document;
            const content = document.getText();
            const fileName = path.basename(document.fileName);

            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: `DeepSeek: Generating tests for ${fileName}`,
                cancellable: false
            }, async (progress) => {
                try {
                    const tests = await deepSeekClient.generateTests(content, document.languageId);
                    
                    // Create a new document with the generated tests
                    const testDocument = await vscode.workspace.openTextDocument({
                        content: tests,
                        language: document.languageId
                    });
                    
                    await vscode.window.showTextDocument(testDocument, vscode.ViewColumn.Beside);
                    vscode.window.showInformationMessage('Tests generated successfully!');
                } catch (error) {
                    vscode.window.showErrorMessage(`Test generation failed: ${error}`);
                }
            });
        })
    );

    // Auto-completion provider
    context.subscriptions.push(
        vscode.languages.registerCompletionItemProvider(
            { pattern: '**/*' },
            {
                async provideCompletionItems(document, position, token, context) {
                    const config = vscode.workspace.getConfiguration('deepseek-code');
                    if (!config.get('autoSuggest')) {
                        return [];
                    }

                    // Get the current line up to cursor
                    const linePrefix = document.lineAt(position).text.substr(0, position.character);
                    
                    // Only trigger on certain patterns
                    if (linePrefix.endsWith('// ') || linePrefix.endsWith('# ')) {
                        return [new vscode.CompletionItem(
                            'Ask DeepSeek...',
                            vscode.CompletionItemKind.Text
                        )];
                    }

                    return [];
                }
            },
            ' ', '#' // Trigger characters
        )
    );
}

export function deactivate() {}