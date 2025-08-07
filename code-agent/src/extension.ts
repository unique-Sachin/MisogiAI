// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';

// Interface for backend API response
interface BackendChatResponse {
	response: string;
	conversation_id: string;
	status: string;
}

class ChatViewProvider implements vscode.WebviewViewProvider {
	public static readonly viewType = 'code-agent.chatView';
	private _view?: vscode.WebviewView;
	private _conversationId?: string;

	constructor(private readonly _extensionUri: vscode.Uri) {}

	public resolveWebviewView(
		webviewView: vscode.WebviewView,
		context: vscode.WebviewViewResolveContext,
		_token: vscode.CancellationToken,
	) {
		this._view = webviewView;

		webviewView.webview.options = {
			enableScripts: true,
			localResourceRoots: [this._extensionUri]
		};

		// Set a proper title and description
		webviewView.title = "Code Agent Chat";
		webviewView.description = "AI-powered coding assistant";

		webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

		// Handle messages from the webview
		webviewView.webview.onDidReceiveMessage(
			message => {
				switch (message.type) {
					case 'sendMessage':
						this._handleUserMessage(message.text);
						break;
					case 'checkBackendStatus':
						this._checkBackendStatus();
						break;
				}
			},
			undefined,
		);

		// Check backend status when view loads
		setTimeout(() => this._checkBackendStatus(), 1000);
	}

	private async _handleUserMessage(message: string) {
		// Add user message to chat immediately
		this._view?.webview.postMessage({
			type: 'addMessage',
			message: {
				text: message,
				sender: 'user',
				timestamp: new Date().toLocaleTimeString()
			}
		});

		try {
			// Initialize streaming response
			const messageId = Date.now().toString();
			this._view?.webview.postMessage({
				type: 'initStreamingMessage',
				messageId: messageId,
				timestamp: new Date().toLocaleTimeString()
			});

			// Call the streaming backend API
			await this._callStreamingBackendAPI(message, messageId);
			
		} catch (error) {
			// Handle API errors
			console.error('Error calling backend API:', error);
			this._view?.webview.postMessage({
				type: 'addMessage',
				message: {
					text: 'Sorry, I encountered an error connecting to the backend service. Please make sure the backend is running on http://localhost:8000',
					sender: 'assistant',
					timestamp: new Date().toLocaleTimeString()
				}
			});
		}
	}

	private async _callStreamingBackendAPI(message: string, messageId: string): Promise<void> {
		const apiUrl = 'http://localhost:8000/chat/stream';
		
		const requestBody = {
			message: message,
			conversation_id: this._conversationId || null
		};

		const response = await fetch(apiUrl, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify(requestBody)
		});

		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}

		if (!response.body) {
			throw new Error('No response body for streaming');
		}

		const reader = response.body.getReader();
		const decoder = new TextDecoder();
		let buffer = '';

		try {
			while (true) {
				const { done, value } = await reader.read();
				
				if (done) {
					break;
				}

				buffer += decoder.decode(value, { stream: true });
				const lines = buffer.split('\n');
				buffer = lines.pop() || ''; // Keep incomplete line in buffer

				for (const line of lines) {
					if (line.trim() === '') {
						continue;
					}
					
					if (line.startsWith('data: ')) {
						const data = line.slice(6);
						
						if (data === '[DONE]') {
							// Streaming complete
							this._view?.webview.postMessage({
								type: 'completeStreamingMessage',
								messageId: messageId
							});
							return;
						}

						try {
							const parsed = JSON.parse(data);
							
							// Update conversation ID if provided
							if (parsed.conversation_id) {
								this._conversationId = parsed.conversation_id;
							}

							// Send chunk to webview
							if (parsed.content) {
								this._view?.webview.postMessage({
									type: 'appendToStreamingMessage',
									messageId: messageId,
									content: parsed.content
								});
							}
						} catch (parseError) {
							console.error('Error parsing streaming data:', parseError);
						}
					}
				}
			}
		} finally {
			reader.releaseLock();
		}
	}

	private async _callBackendAPI(message: string): Promise<string> {
		const apiUrl = 'http://localhost:8000/chat';
		
		const requestBody = {
			message: message,
			conversation_id: this._conversationId || null
		};

		const response = await fetch(apiUrl, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify(requestBody)
		});

		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}

		const data = await response.json() as BackendChatResponse;
		
		// Store conversation ID for future requests
		if (data.conversation_id) {
			this._conversationId = data.conversation_id;
		}
		
		return data.response || 'Sorry, I received an empty response.';
	}

	private async _checkBackendStatus() {
		try {
			const response = await fetch('http://localhost:8000/health', {
				method: 'GET',
			});

			if (response.ok) {
				const healthData = await response.json();
				this._view?.webview.postMessage({
					type: 'backendStatus',
					status: 'connected',
					details: healthData
				});
			} else {
				throw new Error('Backend health check failed');
			}
		} catch (error) {
			this._view?.webview.postMessage({
				type: 'backendStatus',
				status: 'disconnected',
				error: error instanceof Error ? error.message : 'Unknown error'
			});
		}
	}

	private _getHtmlForWebview(webview: vscode.Webview) {
		return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Agent Chat</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            font-weight: var(--vscode-font-weight);
            color: var(--vscode-foreground);
            background-color: var(--vscode-editor-background);
            margin: 0;
            padding: 0;
            height: 100vh;
            display: flex;
            flex-direction: column;
            min-width: 350px;
            width: 100%;
        }
        
        .chat-container {
            display: flex;
            flex-direction: column;
            height: 100%;
        }
        
        .chat-header {
            padding: 12px 16px;
            border-bottom: 1px solid var(--vscode-panel-border);
            background-color: var(--vscode-sideBar-background);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header-content {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .chat-icon {
            font-size: 16px;
        }
        
        .chat-title {
            font-weight: 600;
            margin: 0;
            font-size: 14px;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 11px;
            color: var(--vscode-descriptionForeground);
        }
        
        .status-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background-color: var(--vscode-charts-green);
            animation: pulse 2s infinite;
        }
        
        .status-dot.disconnected {
            background-color: var(--vscode-errorForeground);
            animation: none;
        }
        
        .status-dot.connecting {
            background-color: var(--vscode-charts-yellow);
            animation: pulse 1s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .messages-container {
            flex: 1;
            overflow-y: auto;
            padding: 16px 12px;
            display: flex;
            flex-direction: column;
            gap: 16px;
            min-height: 0;
        }
        
        .message {
            display: flex;
            flex-direction: column;
            max-width: 85%;
            animation: fadeIn 0.3s ease-in;
            margin: 0;
        }
        
        .message.user {
            align-self: flex-end;
            margin-left: auto;
        }
        
        .message.assistant {
            align-self: flex-start;
        }
        
        .message-bubble {
            padding: 12px 16px;
            border-radius: 12px;
            word-wrap: break-word;
            white-space: pre-wrap;
            line-height: 1.4;
            margin: 0;
            display: block;
            width: fit-content;
        }
        
        .message.user .message-bubble {
            background-color: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            margin-left: auto;
        }
        
        .message.assistant .message-bubble {
            background-color: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
        }
        
        .message-info {
            font-size: 11px;
            color: var(--vscode-descriptionForeground);
            margin-top: 4px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .message.user .message-info {
            justify-content: flex-end;
        }
        
        .sender-label {
            font-weight: 500;
        }
        
        .input-container {
            padding: 16px;
            border-top: 1px solid var(--vscode-panel-border);
            background-color: var(--vscode-panel-background);
        }
        
        .input-wrapper {
            display: flex;
            gap: 8px;
            align-items: flex-end;
        }
        
        .message-input {
            flex: 1;
            min-height: 36px;
            max-height: 120px;
            padding: 8px 12px;
            border: 1px solid var(--vscode-input-border);
            border-radius: 6px;
            background-color: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
            font-family: inherit;
            font-size: inherit;
            resize: none;
            outline: none;
        }
        
        .message-input:focus {
            border-color: var(--vscode-focusBorder);
        }
        
        .send-button {
            padding: 8px 16px;
            background-color: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-family: inherit;
            font-size: inherit;
            font-weight: 500;
            transition: background-color 0.2s;
        }
        
        .send-button:hover {
            background-color: var(--vscode-button-hoverBackground);
        }
        
        .send-button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .empty-state {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            color: var(--vscode-descriptionForeground);
            padding: 32px;
        }
        
        .empty-state-icon {
            font-size: 48px;
            margin-bottom: 16px;
            opacity: 0.6;
        }
        
        .empty-state-title {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        .empty-state-description {
            font-size: 14px;
            line-height: 1.4;
            margin-bottom: 24px;
        }
        
        .example-prompts {
            display: flex;
            flex-direction: column;
            gap: 8px;
            width: 100%;
            max-width: 280px;
        }
        
        .example-prompt {
            padding: 8px 12px;
            background-color: var(--vscode-button-secondaryBackground);
            border: 1px solid var(--vscode-button-border);
            border-radius: 6px;
            font-size: 12px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .example-prompt:hover {
            background-color: var(--vscode-button-secondaryHoverBackground);
            transform: translateY(-1px);
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .typing-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            color: var(--vscode-descriptionForeground);
            font-style: italic;
        }
        
        .typing-dots {
            display: flex;
            gap: 2px;
        }
        
        .typing-dot {
            width: 4px;
            height: 4px;
            border-radius: 50%;
            background-color: var(--vscode-descriptionForeground);
            animation: typing 1.4s infinite ease-in-out;
        }
        
        .typing-dot:nth-child(1) { animation-delay: -0.32s; }
        .typing-dot:nth-child(2) { animation-delay: -0.16s; }
        
        @keyframes typing {
            0%, 80%, 100% { opacity: 0.3; }
            40% { opacity: 1; }
        }
        
        .streaming-cursor {
            animation: blink 1s infinite;
            color: var(--vscode-editorCursor-foreground);
            font-weight: bold;
        }
        
        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
        }
        .streaming-content {
			display: inline-block;
			white-space: pre-wrap;
			word-break: break-word;
			
		}
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <div class="header-content">
                <span class="chat-icon">🤖</span>
                <h3 class="chat-title">Code Agent</h3>
            </div>
            <div class="status-indicator">
                <span class="status-dot connecting" id="statusDot"></span>
                <span class="status-text" id="statusText">Connecting...</span>
            </div>
        </div>
        
        <div class="messages-container" id="messagesContainer">
            <div class="empty-state" id="emptyState">
                <div class="empty-state-icon">�</div>
                <div class="empty-state-title">Welcome to Code Agent</div>
                <div class="empty-state-description">
                    I'm here to help you write, understand, and improve your code.<br>
                    Try asking me about your project or request help with coding tasks!<br><br>
                </div>
                <div class="example-prompts">
                    <div class="example-prompt">"Explain this function"</div>
                    <div class="example-prompt">"Help me debug this code"</div>
                    <div class="example-prompt">"Write a unit test"</div>
                </div>
            </div>
        </div>
        
        <div class="input-container">
            <div class="input-wrapper">
                <textarea 
                    class="message-input" 
                    id="messageInput" 
                    placeholder="Type your message here..."
                    rows="1"
                ></textarea>
                <button class="send-button" id="sendButton">Send</button>
            </div>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        const messagesContainer = document.getElementById('messagesContainer');
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        const emptyState = document.getElementById('emptyState');
        const statusDot = document.getElementById('statusDot');
        const statusText = document.getElementById('statusText');
        
        let messages = [];
        let backendConnected = false;

        // Handle example prompt clicks
        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('example-prompt')) {
                messageInput.value = e.target.textContent;
                messageInput.focus();
            }
        });

        // Check backend status on load
        setTimeout(() => {
            vscode.postMessage({ type: 'checkBackendStatus' });
        }, 500);

        // Auto-resize textarea
        messageInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });

        // Send message on button click
        sendButton.addEventListener('click', sendMessage);
        
        // Send message on Enter (Shift+Enter for new line)
        messageInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        function sendMessage() {
            const text = messageInput.value.trim();
            if (!text) return;

            if (!backendConnected) {
                // Show warning if backend is not connected
                addMessage({
                    text: 'Warning: Backend is not connected. Please make sure the backend server is running on http://localhost:8000',
                    sender: 'system',
                    timestamp: new Date().toLocaleTimeString()
                });
                return;
            }

            // Clear input
            messageInput.value = '';
            messageInput.style.height = 'auto';

            // Hide empty state
            if (emptyState) {
                emptyState.style.display = 'none';
            }

            // Send to extension
            vscode.postMessage({
                type: 'sendMessage',
                text: text
            });

            // Show typing indicator
            showTypingIndicator();
        }

        function addMessage(message) {
            // Remove typing indicator
            hideTypingIndicator();
            
            messages.push(message);
            
            const messageElement = document.createElement('div');
            messageElement.className = \`message \${message.sender}\`;
            
            // Special styling for system messages
            if (message.sender === 'system') {
                messageElement.className += ' system';
                messageElement.innerHTML = \`
                    <div class="message-bubble" style="background-color: var(--vscode-editorWarning-background); border: 1px solid var(--vscode-editorWarning-border); color: var(--vscode-editorWarning-foreground);">
                        ⚠️ \${escapeHtml(message.text)}
                    </div>
                    <div class="message-info">
                        <span class="sender-label">System</span>
                        <span class="timestamp">\${message.timestamp}</span>
                    </div>
                \`;
            } else {
                messageElement.innerHTML = \`
                    <div class="message-bubble">\${escapeHtml(message.text)}</div>
                    <div class="message-info">
                        <span class="sender-label">\${message.sender === 'user' ? 'You' : 'Assistant'}</span>
                        <span class="timestamp">\${message.timestamp}</span>
                    </div>
                \`;
            }
            
            messagesContainer.appendChild(messageElement);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        function showTypingIndicator() {
            hideTypingIndicator(); // Remove any existing indicator
            
            const typingElement = document.createElement('div');
            typingElement.className = 'message assistant';
            typingElement.id = 'typingIndicator';
            
            typingElement.innerHTML = \`
                <div class="typing-indicator">
                    <span>Assistant is typing</span>
                    <div class="typing-dots">
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                    </div>
                </div>
            \`;
            
            messagesContainer.appendChild(typingElement);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        function hideTypingIndicator() {
            const typingIndicator = document.getElementById('typingIndicator');
            if (typingIndicator) {
                typingIndicator.remove();
            }
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        function initStreamingMessage(messageId, timestamp) {
            // Remove typing indicator
            hideTypingIndicator();
            
            const messageElement = document.createElement('div');
            messageElement.className = 'message assistant';
            messageElement.id = \`streaming-\${messageId}\`;
            
            messageElement.innerHTML = \`
                <div class="message-bubble">
                    <span class="streaming-content" id="content-\${messageId}"></span>
                    <span class="streaming-cursor">|</span>
                </div>
                <div class="message-info">
                    <span class="sender-label">Assistant</span>
                    <span class="timestamp">\${timestamp}</span>
                </div>
            \`;
            
            messagesContainer.appendChild(messageElement);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        function appendToStreamingMessage(messageId, content) {
            const contentElement = document.getElementById(\`content-\${messageId}\`);
            if (contentElement) {
                contentElement.textContent += content;
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
        }

        function completeStreamingMessage(messageId) {
            const messageElement = document.getElementById(\`streaming-\${messageId}\`);
            if (messageElement) {
                // Remove streaming cursor
                const cursor = messageElement.querySelector('.streaming-cursor');
                if (cursor) {
                    cursor.remove();
                }
                
                // Remove streaming ID
                messageElement.id = '';
            }
        }

        function updateBackendStatus(status, details) {
            backendConnected = status === 'connected';
            
            if (statusDot && statusText) {
                statusDot.className = 'status-dot';
                
                if (status === 'connected') {
                    statusDot.classList.add('connected');
                    statusText.textContent = 'Connected';
                } else {
                    statusDot.classList.add('disconnected');
                    statusText.textContent = 'Disconnected';
                    
                    // Show connection failure message
                    addMessage({
                        text: '❌ Backend connection failed. Please start the backend server:\\n\\ncd backend\\n./start.sh\\n\\nThen refresh this panel.',
                        sender: 'system',
                        timestamp: new Date().toLocaleTimeString()
                    });
                }
            }
        }

        // Listen for messages from the extension
        window.addEventListener('message', event => {
            const message = event.data;
            switch (message.type) {
                case 'addMessage':
                    addMessage(message.message);
                    break;
                case 'initStreamingMessage':
                    initStreamingMessage(message.messageId, message.timestamp);
                    break;
                case 'appendToStreamingMessage':
                    appendToStreamingMessage(message.messageId, message.content);
                    break;
                case 'completeStreamingMessage':
                    completeStreamingMessage(message.messageId);
                    break;
                case 'backendStatus':
                    updateBackendStatus(message.status, message.details);
                    break;
            }
        });
    </script>
</body>
</html>`;
	}
}

// This method is called when your extension is activated
export function activate(context: vscode.ExtensionContext) {
	console.log('Code Agent extension is now active!');

	// Register the chat view provider
	const chatProvider = new ChatViewProvider(context.extensionUri);
	context.subscriptions.push(
		vscode.window.registerWebviewViewProvider(ChatViewProvider.viewType, chatProvider)
	);

	// Register command to open chat
	const openChatCommand = vscode.commands.registerCommand('code-agent.openChat', () => {
		vscode.commands.executeCommand('workbench.view.extension.code-agent');
	});

	// Register command to optimize chat panel width
	const optimizeWidthCommand = vscode.commands.registerCommand('code-agent.optimizeWidth', () => {
		vscode.window.showInformationMessage(
			'To optimize the chat panel width:\n\n1. Drag the panel border to approximately 350-400px wide\n2. This provides the best balance for reading messages and code\n3. VS Code will remember this width for future sessions',
			'Got it!'
		);
	});

	context.subscriptions.push(openChatCommand, optimizeWidthCommand);
}

// This method is called when your extension is deactivated
export function deactivate() {}

