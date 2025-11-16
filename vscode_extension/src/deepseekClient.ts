// deepseek-code/vscode_extension/src/deepseekClient.ts
import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import axios from 'axios';

export interface DeepSeekResponse {
    choices: Array<{
        message: {
            content: string;
        };
    }>;
}

export class DeepSeekClient {
    private apiKey: string = '';
    private baseUrl: string = 'https://api.deepseek.com/v1';
    private configPath: string;

    constructor() {
        this.configPath = path.join(os.homedir(), '.deepseek-code', 'team_config.json');
        this.loadApiKey();
    }

    private loadApiKey(): void {
        try {
            // First try VS Code configuration
            const config = vscode.workspace.getConfiguration('deepseek-code');
            const configApiKey = config.get<string>('apiKey');
            
            if (configApiKey) {
                this.apiKey = configApiKey;
                return;
            }

            // Then try CLI configuration
            if (fs.existsSync(this.configPath)) {
                const configData = JSON.parse(fs.readFileSync(this.configPath, 'utf8'));
                // Note: In real implementation, we'd decrypt the API key
                this.apiKey = configData.apiKey || '';
            }
        } catch (error) {
            console.error('Failed to load API key:', error);
        }
    }

    async chatCompletion(messages: any[], model: string = 'deepseek-coder'): Promise<string> {
        if (!this.apiKey) {
            throw new Error('DeepSeek API key not configured. Please set it in VS Code settings or run the CLI setup.');
        }

        try {
            const response = await axios.post(`${this.baseUrl}/chat/completions`, {
                model,
                messages,
                max_tokens: 2048,
                temperature: 0.7
            }, {
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`,
                    'Content-Type': 'application/json'
                },
                timeout: 30000
            });

            return response.data.choices[0].message.content;
        } catch (error: any) {
            throw new Error(`API request failed: ${error.response?.data?.error?.message || error.message}`);
        }
    }

    async analyzeCode(code: string, language: string): Promise<string> {
        const messages = [
            {
                role: 'system',
                content: `You are an expert code analyzer. Provide detailed analysis of the given ${language} code including complexity, potential issues, improvements, and best practices.`
            },
            {
                role: 'user',
                content: `Please analyze this ${language} code:\n\`\`\`${language}\n${code}\n\`\`\``
            }
        ];

        return await this.chatCompletion(messages);
    }

    async refactorCode(code: string, instructions: string, language: string): Promise<string> {
        const messages = [
            {
                role: 'system',
                content: `You are a ${language} refactoring expert. Refactor the code according to the instructions while maintaining functionality and improving code quality.`
            },
            {
                role: 'user',
                content: `Original code:\n\`\`\`${language}\n${code}\n\`\`\`\n\nInstructions: ${instructions}\n\nRefactored code:`
            }
        ];

        const response = await this.chatCompletion(messages);
        return this.extractCodeFromResponse(response, language);
    }

    async explainCode(code: string, language: string): Promise<string> {
        const messages = [
            {
                role: 'system',
                content: 'You are a code explanation expert. Explain the given code in simple terms, covering what it does, how it works, and key concepts.'
            },
            {
                role: 'user',
                content: `Please explain this ${language} code:\n\`\`\`${language}\n${code}\n\`\`\``
            }
        ];

        return await this.chatCompletion(messages);
    }

    async generateTests(code: string, language: string): Promise<string> {
        const messages = [
            {
                role: 'system',
                content: `You are a testing expert. Generate comprehensive unit tests for the given ${language} code using appropriate testing frameworks.`
            },
            {
                role: 'user',
                content: `Generate tests for this ${language} code:\n\`\`\`${language}\n${code}\n\`\`\``
            }
        ];

        const response = await this.chatCompletion(messages);
        return this.extractCodeFromResponse(response, this.getTestLanguage(language));
    }

    private extractCodeFromResponse(response: string, language: string): string {
        // Look for code blocks in the response
        const codeBlockRegex = new RegExp(`\\\`\\\`\\\`${language}(.*?)\\\`\\\`\\\``, 's');
        const match = response.match(codeBlockRegex);
        
        if (match && match[1]) {
            return match[1].trim();
        }

        // Fallback: look for any code block
        const genericCodeBlockRegex = /```(?:\w+)?\s*(.*?)```/s;
        const genericMatch = response.match(genericCodeBlockRegex);
        
        if (genericMatch && genericMatch[1]) {
            return genericMatch[1].trim();
        }

        // Return the entire response if no code blocks found
        return response.trim();
    }

    private getTestLanguage(language: string): string {
        const testLanguageMap: { [key: string]: string } = {
            'python': 'python',
            'javascript': 'javascript',
            'typescript': 'typescript',
            'java': 'java',
            'csharp': 'csharp',
            'cpp': 'cpp',
            'go': 'go',
            'rust': 'rust'
        };
        
        return testLanguageMap[language] || language;
    }
}