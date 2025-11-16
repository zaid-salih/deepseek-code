// deepseek-code/vscode_extension/src/codeActionProvider.ts
import * as vscode from 'vscode';
import { DeepSeekClient } from './deepseekClient';

export class CodeActionProvider implements vscode.CodeActionProvider {
    constructor(private deepSeekClient: DeepSeekClient) {}

    provideCodeActions(
        document: vscode.TextDocument,
        range: vscode.Range | vscode.Selection,
        context: vscode.CodeActionContext,
        token: vscode.CancellationToken
    ): vscode.CodeAction[] {
        const actions: vscode.CodeAction[] = [];

        // Add refactor action
        const refactorAction = new vscode.CodeAction(
            'DeepSeek: Refactor selection',
            vscode.CodeActionKind.Refactor
        );
        refactorAction.command = {
            command: 'deepseek-code.refactorCode',
            title: 'Refactor with DeepSeek',
            arguments: []
        };
        actions.push(refactorAction);

        // Add explain action
        const explainAction = new vscode.CodeAction(
            'DeepSeek: Explain selection',
            vscode.CodeActionKind.Empty
        );
        explainAction.command = {
            command: 'deepseek-code.explainCode',
            title: 'Explain with DeepSeek',
            arguments: []
        };
        actions.push(explainAction);

        return actions;
    }
}