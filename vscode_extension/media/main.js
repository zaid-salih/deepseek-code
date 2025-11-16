// deepseek-code/vscode_extension/media/main.js
(function() {
    const vscode = acquireVsCodeApi();
    const chatMessages = document.getElementById('chat-messages');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const clearButton = document.getElementById('clear-chat');

    // Load previous state
    const previousState = vscode.getState();
    if (previousState && previousState.conversation) {
        displayConversation(previousState.conversation);
    }

    // Handle send message
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Handle clear chat
    clearButton.addEventListener('click', () => {
        vscode.postMessage({ type: 'clearChat' });
    });

    // Handle messages from extension
    window.addEventListener('message', (event) => {
        const message = event.data;
        switch (message.type) {
            case 'updateConversation':
                vscode.setState({ conversation: message.conversation });
                displayConversation(message.conversation);
                break;
            case 'showAnalysis':
                displayAnalysis(message.analysis, message.fileName);
                break;
            case 'showExplanation':
                displayExplanation(message.explanation, message.code);
                break;
        }
    });

    function sendMessage() {
        const message = messageInput.value.trim();
        if (message) {
            vscode.postMessage({ type: 'sendMessage', message });
            messageInput.value = '';
        }
    }

    function displayConversation(conversation) {
        chatMessages.innerHTML = '';
        conversation.forEach(msg => {
            addMessage(msg.role, msg.content, msg.timestamp, msg.isError);
        });
        scrollToBottom();
    }

    function displayAnalysis(analysis, fileName) {
        addMessage('system', `## Analysis of ${fileName}\n\n${analysis}`);
        scrollToBottom();
    }

    function displayExplanation(explanation, code) {
        addMessage('system', `## Code Explanation\n\n### Code:\n\`\`\`\n${code}\n\`\`\`\n\n### Explanation:\n${explanation}`);
        scrollToBottom();
    }

    function addMessage(role, content, timestamp, isError = false) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${role} ${isError ? 'error' : ''}`;
        
        const timestampText = timestamp ? new Date(timestamp).toLocaleTimeString() : '';
        
        messageElement.innerHTML = `
            <div class="message-header">
                <span class="message-role">${role === 'user' ? 'You' : 'DeepSeek'}</span>
                <span class="message-time">${timestampText}</span>
            </div>
            <div class="message-content">${formatContent(content)}</div>
        `;
        
        chatMessages.appendChild(messageElement);
    }

    function formatContent(content) {
        // Convert markdown-like formatting
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/```(\w+)?\s*(.*?)```/gs, (match, lang, code) => {
                return `<pre><code class="language-${lang || 'text'}">${escapeHtml(code)}</code></pre>`;
            })
            .replace(/\n/g, '<br>');
    }

    function escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
})();