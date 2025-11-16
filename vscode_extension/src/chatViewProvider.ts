// deepseek-code/vscode_extension/src/chatViewProvider.ts
import * as vscode from 'vscode';
import { DeepSeekClient } from './deepseekClient';

export class ChatViewProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'deepseek-code.chatView';

    private _view?: vscode.WebviewView;
    private _conversationHistory: any[] = [];

    constructor(
        private readonly _extensionUri: vscode.Uri,
        private readonly _deepSeekClient: DeepSeekClient
    ) { }

    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken,
    ) {
        this._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [
                this._extensionUri
            ]
        };

        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

        webviewView.webview.onDidReceiveMessage(async data => {
            switch (data.type) {
                case 'sendMessage':
                    await this._handleUserMessage(data.message);
                    break;
                case 'clearChat':
                    this._conversationHistory = [];
                    this._updateWebview();
                    break;
            }
        });
    }

    public showChat(): void {
        if (this._view) {
            this._view.show?.(true);
        }
    }

    public showAnalysis(analysis: string, fileName: string): void {
        if (this._view) {
            this._view.show?.(true);
            this._view.webview.postMessage({
                type: 'showAnalysis',
                analysis,
                fileName
            });
        }
    }

    public showExplanation(explanation: string, code: string): void {
        if (this._view) {
            this._view.show?.(true);
            this._view.webview.postMessage({
                type: 'showExplanation',
                explanation,
                code
            });
        }
    }

    private async _handleUserMessage(message: string): Promise<void> {
        if (!this._view) {
            return;
        }

        // Add user message to history
        this._conversationHistory.push({
            role: 'user',
            content: message,
            timestamp: new Date().toISOString()
        });

        this._updateWebview();

        try {
            // Get AI response
            const response = await this._deepSeekClient.chatCompletion([
                {
                    role: 'system',
                    content: 'You are DeepSeek-Code, an AI assistant for software development. Provide helpful, concise, and practical coding assistance.'
                },
                ...this._conversationHistory.slice(-10).map((msg: any) => ({
                    role: msg.role,
                    content: msg.content
                }))
            ]);

            // Add AI response to history
            this._conversationHistory.push({
                role: 'assistant',
                content: response,
                timestamp: new Date().toISOString()
            });

            this._updateWebview();
        } catch (error: any) {
            this._conversationHistory.push({
                role: 'assistant',
                content: `Error: ${error.message}`,
                timestamp: new Date().toISOString(),
                isError: true
            });

            this._updateWebview();
        }
    }

    private _updateWebview(): void {
        if (this._view) {
            this._view.webview.postMessage({
                type: 'updateConversation',
                conversation: this._conversationHistory
            });
        }
    }

    private _getHtmlForWebview(webview: vscode.Webview): string {
        const scriptUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'media', 'main.js'));
        const styleUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'media', 'main.css'));

        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="${styleUri}" rel="stylesheet">
            <title>DeepSeek-Code Chat</title>
        </head>
        <body>
            <div class="chat-container">
                <div class="chat-header">
                    <h2>DeepSeek-Code Chat</h2>
                    <button id="clear-chat">Clear</button>
                </div>
                <div id="chat-messages" class="chat-messages"></div>
                <div class="chat-input-container">
                    <textarea id="message-input" placeholder="Ask DeepSeek about your code..."></textarea>
                    <button id="send-button">Send</button>
                </div>
            </div>
            <script src="${scriptUri}"></script>
        </body>
        </html>`;
    }
}