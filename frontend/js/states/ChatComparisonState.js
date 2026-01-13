/**
 * Chat Comparison State Handler
 * Manages the chat interface and real-time AI responses
 */

class ChatComparisonState {
    constructor() {
        this.sessionData = {};
        this.messageHistory = [];
        this.isProcessing = false;
        this.init();
    }

    /**
     * Initialize the chat comparison state
     */
    init() {
        this.bindEvents();
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        // Message form submission
        const messageForm = document.getElementById('message-form');
        if (messageForm) {
            messageForm.addEventListener('submit', (e) => this.handleMessageSubmit(e));
        }

        // Enter key in message input
        const messageInput = document.getElementById('message-input');
        if (messageInput) {
            messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    messageForm.dispatchEvent(new Event('submit'));
                }
            });
        }
    }

    /**
     * Initialize chat interface with session data
     * @param {Object} sessionData - Session data including user info and selected agents
     */
    initializeChat(sessionData) {
        this.sessionData = sessionData;
        
        // Update AI headers
        this.updateAIHeaders();
        
        // Clear previous messages
        this.clearMessages();
        
        // Reset processing state
        this.isProcessing = false;
        this.updateSendButton();
    }

    /**
     * Update AI headers with agent information
     */
    updateAIHeaders() {
        const agents = this.sessionData.selectedAgents || [];
        
        if (agents.length >= 2) {
            // Update first AI
            const ai1Name = document.getElementById('ai-1-name');
            const ai1Status = document.getElementById('ai-1-status');
            
            if (ai1Name) ai1Name.textContent = agents[0].display_name;
            if (ai1Status) {
                ai1Status.className = 'ai-status ready';
                ai1Status.textContent = 'Ready';
            }

            // Update second AI
            const ai2Name = document.getElementById('ai-2-name');
            const ai2Status = document.getElementById('ai-2-status');
            
            if (ai2Name) ai2Name.textContent = agents[1].display_name;
            if (ai2Status) {
                ai2Status.className = 'ai-status ready';
                ai2Status.textContent = 'Ready';
            }
        }
    }

    /**
     * Handle message form submission
     * @param {Event} event - Form submission event
     */
    async handleMessageSubmit(event) {
        event.preventDefault();
        
        if (this.isProcessing) return;

        const messageInput = document.getElementById('message-input');
        const message = messageInput.value.trim();
        
        if (!message) return;

        // Clear input and disable form
        messageInput.value = '';
        this.isProcessing = true;
        this.updateSendButton();

        // Add user message to both columns
        this.addUserMessage(message);

        // Set AI status to processing
        UIUtils.updateAIStatus('ai-1', 'processing', 'Processing...');
        UIUtils.updateAIStatus('ai-2', 'processing', 'Processing...');

        try {
            // Send message to backend and handle streaming responses
            await this.sendMessageWithStreaming(message);
            
        } catch (error) {
            console.error('Error sending message:', error);
            UIUtils.showError('Error sending message: ' + error.message);
            
            // Set error status
            UIUtils.updateAIStatus('ai-1', 'error', 'Error');
            UIUtils.updateAIStatus('ai-2', 'error', 'Error');
        } finally {
            this.isProcessing = false;
            this.updateSendButton();
        }
    }

    /**
     * Send message with streaming response handling
     * @param {string} message - Message to send
     */
    async sendMessageWithStreaming(message) {
        const agents = this.sessionData.selectedAgents || [];
        
        // Create placeholder messages for both AIs
        const ai1Placeholder = this.createPlaceholderMessage('ai-1');
        const ai2Placeholder = this.createPlaceholderMessage('ai-2');
        
        try {
            // Start message processing
            const startResponse = await apiClient.startChatMessage(this.sessionData.session_id, message);
            const requestId = startResponse.request_id;
            
            console.log('Started chat processing with request ID:', requestId);
            
            // Poll for responses
            const responsesReceived = new Set();
            const startTime = Date.now();
            const maxWaitTime = 60000; // 60 seconds max
            const pollInterval = 200; // Poll every 200ms for faster response
            
            const pollForResponses = async () => {
                try {
                    const status = await apiClient.getChatStatus(requestId);
                    
                    console.log('Poll status:', {
                        completed: status.completed_agents?.length || 0,
                        total: status.total_agents || 0,
                        responses: Object.keys(status.responses || {}),
                        status: status.status
                    });
                    
                    if (status.responses && status.metadata) {
                        // Check first AI response
                        if (agents[0] && 
                            status.responses[agents[0].key] && 
                            !responsesReceived.has('ai-1')) {
                            
                            console.log('Received response from first AI:', agents[0].key);
                            responsesReceived.add('ai-1');
                            this.replaceWithActualResponse(
                                ai1Placeholder,
                                'ai-1',
                                status.responses[agents[0].key],
                                status.metadata[agents[0].key]
                            );
                        }

                        // Check second AI response
                        if (agents[1] && 
                            status.responses[agents[1].key] && 
                            !responsesReceived.has('ai-2')) {
                            
                            console.log('Received response from second AI:', agents[1].key);
                            responsesReceived.add('ai-2');
                            this.replaceWithActualResponse(
                                ai2Placeholder,
                                'ai-2',
                                status.responses[agents[1].key],
                                status.metadata[agents[1].key]
                            );
                        }
                    }
                    
                    // Continue polling if not all responses received and within time limit
                    if (responsesReceived.size < 2 && 
                        status.status !== 'completed' && 
                        (Date.now() - startTime) < maxWaitTime) {
                        setTimeout(pollForResponses, pollInterval);
                    } else if (responsesReceived.size < 2) {
                        // Timeout or completion - mark remaining as error/timeout
                        console.log('Timeout or completion, handling remaining responses');
                        if (!responsesReceived.has('ai-1')) {
                            this.handleResponseTimeout(ai1Placeholder, 'ai-1');
                        }
                        if (!responsesReceived.has('ai-2')) {
                            this.handleResponseTimeout(ai2Placeholder, 'ai-2');
                        }
                    }
                    
                } catch (error) {
                    console.error('Error polling for responses:', error);
                    // Handle error for remaining AIs
                    if (!responsesReceived.has('ai-1')) {
                        this.handleResponseError(ai1Placeholder, 'ai-1', error);
                    }
                    if (!responsesReceived.has('ai-2')) {
                        this.handleResponseError(ai2Placeholder, 'ai-2', error);
                    }
                }
            };
            
            // Start polling immediately
            pollForResponses();
            
        } catch (error) {
            console.error('Error starting message processing:', error);
            // Handle error for both AIs
            this.handleResponseError(ai1Placeholder, 'ai-1', error);
            this.handleResponseError(ai2Placeholder, 'ai-2', error);
        }
    }

    /**
     * Create placeholder message while waiting for response
     * @param {string} aiId - AI identifier
     * @returns {HTMLElement} Placeholder message element
     */
    createPlaceholderMessage(aiId) {
        const messagesContainer = document.getElementById(`${aiId}-messages`);
        if (!messagesContainer) return null;

        const placeholder = document.createElement('div');
        placeholder.className = 'message assistant placeholder';
        placeholder.innerHTML = `
            <div class="message-content">
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
                Generating response...
            </div>
        `;
        
        messagesContainer.appendChild(placeholder);
        UIUtils.scrollToBottom(`${aiId}-messages`);
        
        return placeholder;
    }

    /**
     * Replace placeholder with actual response
     * @param {HTMLElement} placeholder - Placeholder element
     * @param {string} aiId - AI identifier
     * @param {string} content - Response content
     * @param {Object} metadata - Response metadata
     */
    replaceWithActualResponse(placeholder, aiId, content, metadata) {
        if (!placeholder) return;
        
        // Create actual message
        const messageEl = UIUtils.createMessage(content, 'assistant', metadata);
        
        // Replace placeholder with actual message
        placeholder.parentNode.replaceChild(messageEl, placeholder);
        
        // Update status to ready
        UIUtils.updateAIStatus(aiId, 'ready', 'Ready');
        
        // Scroll to bottom
        UIUtils.scrollToBottom(`${aiId}-messages`);
        
        // Add animation
        messageEl.style.opacity = '0';
        messageEl.style.transform = 'translateY(20px)';
        setTimeout(() => {
            messageEl.style.transition = 'all 0.3s ease';
            messageEl.style.opacity = '1';
            messageEl.style.transform = 'translateY(0)';
        }, 50);
    }

    /**
     * Handle response timeout
     * @param {HTMLElement} placeholder - Placeholder element
     * @param {string} aiId - AI identifier
     */
    handleResponseTimeout(placeholder, aiId) {
        this.handleResponseFailure(placeholder, aiId, 'Request timeout', {
            processing_time_seconds: 30,
            cost_usd: 0,
            error: true
        }, 'Timeout');
    }

    /**
     * Handle response error
     * @param {HTMLElement} placeholder - Placeholder element
     * @param {string} aiId - AI identifier
     * @param {Error} error - Error object
     */
    handleResponseError(placeholder, aiId, error) {
        this.handleResponseFailure(placeholder, aiId, `Error: ${error.message}`, {
            processing_time_seconds: 0,
            cost_usd: 0,
            error: true
        }, 'Error');
    }

    /**
     * Generic handler for response failures
     * @param {HTMLElement} placeholder - Placeholder element
     * @param {string} aiId - AI identifier
     * @param {string} message - Error message
     * @param {Object} metadata - Error metadata
     * @param {string} status - Status text
     */
    handleResponseFailure(placeholder, aiId, message, metadata, status) {
        if (!placeholder) return;
        
        const errorMessage = UIUtils.createMessage(message, 'assistant', metadata);
        placeholder.parentNode.replaceChild(errorMessage, placeholder);
        UIUtils.updateAIStatus(aiId, 'error', status);
        UIUtils.scrollToBottom(`${aiId}-messages`);
    }

    /**
     * Add user message to chat interface
     * @param {string} message - User message
     */
    addUserMessage(message) {
        const agents = this.sessionData.selectedAgents || [];
        
        // Add to first AI column
        if (agents[0]) {
            const ai1Messages = document.getElementById('ai-1-messages');
            const messageEl = UIUtils.createMessage(message, 'user');
            ai1Messages.appendChild(messageEl);
            UIUtils.scrollToBottom('ai-1-messages');
        }

        // Add to second AI column
        if (agents[1]) {
            const ai2Messages = document.getElementById('ai-2-messages');
            const messageEl = UIUtils.createMessage(message, 'user');
            ai2Messages.appendChild(messageEl);
            UIUtils.scrollToBottom('ai-2-messages');
        }
    }

    /**
     * Handle AI responses from backend
     * @param {Object} response - Response from chat API
     */
    handleAIResponses(response) {
        const agents = this.sessionData.selectedAgents || [];
        
        if (response.responses && response.metadata) {
            // Handle first AI response
            if (agents[0] && response.responses[agents[0].key]) {
                this.addAIResponse(
                    'ai-1',
                    response.responses[agents[0].key],
                    response.metadata[agents[0].key]
                );
            }

            // Handle second AI response
            if (agents[1] && response.responses[agents[1].key]) {
                this.addAIResponse(
                    'ai-2',
                    response.responses[agents[1].key],
                    response.metadata[agents[1].key]
                );
            }
        }
    }

    /**
     * Add AI response to chat interface
     * @param {string} aiId - AI identifier (ai-1 or ai-2)
     * @param {string} content - Response content
     * @param {Object} metadata - Response metadata
     */
    addAIResponse(aiId, content, metadata) {
        const messagesContainer = document.getElementById(`${aiId}-messages`);
        if (!messagesContainer) return;

        // Create and add message
        const messageEl = UIUtils.createMessage(content, 'assistant', metadata);
        messagesContainer.appendChild(messageEl);
        
        // Update status to ready
        UIUtils.updateAIStatus(aiId, 'ready', 'Ready');
        
        // Scroll to bottom
        UIUtils.scrollToBottom(`${aiId}-messages`);
    }

    /**
     * Update send button state
     */
    updateSendButton() {
        const sendButton = document.getElementById('send-button');
        const messageInput = document.getElementById('message-input');
        
        if (sendButton) {
            sendButton.disabled = this.isProcessing;
            sendButton.textContent = this.isProcessing ? 'Sending...' : 'Send';
        }

        if (messageInput) {
            messageInput.disabled = this.isProcessing;
        }
    }

    /**
     * Clear all messages from chat interface
     */
    clearMessages() {
        const ai1Messages = document.getElementById('ai-1-messages');
        const ai2Messages = document.getElementById('ai-2-messages');
        
        if (ai1Messages) ai1Messages.innerHTML = '';
        if (ai2Messages) ai2Messages.innerHTML = '';
        
        this.messageHistory = [];
    }

    /**
     * Reset the state
     */
    reset() {
        this.sessionData = {};
        this.messageHistory = [];
        this.isProcessing = false;
        
        this.clearMessages();
        this.updateSendButton();
        
        // Reset AI headers
        const ai1Name = document.getElementById('ai-1-name');
        const ai2Name = document.getElementById('ai-2-name');
        
        if (ai1Name) ai1Name.textContent = 'AI Model 1';
        if (ai2Name) ai2Name.textContent = 'AI Model 2';
        
        UIUtils.updateAIStatus('ai-1', 'ready', 'Ready');
        UIUtils.updateAIStatus('ai-2', 'ready', 'Ready');
    }
}

// Make ChatComparisonState globally available
window.ChatComparisonState = ChatComparisonState;