/**
 * UI utility functions
 */

class UIUtils {
    /**
     * Show loading overlay
     * @param {string} message - Loading message
     */
    static showLoading(message = 'Processing...') {
        const overlay = document.getElementById('loading-overlay');
        const messageEl = overlay.querySelector('p');
        messageEl.textContent = message;
        overlay.style.display = 'flex';
    }

    /**
     * Hide loading overlay
     */
    static hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        overlay.style.display = 'none';
    }

    /**
     * Show error modal
     * @param {string} message - Error message
     */
    static showError(message) {
        const modal = document.getElementById('error-modal');
        const messageEl = document.getElementById('error-message');
        messageEl.textContent = message;
        modal.style.display = 'flex';
    }

    /**
     * Hide error modal
     */
    static hideError() {
        const modal = document.getElementById('error-modal');
        modal.style.display = 'none';
    }

    /**
     * Update progress indicator
     * @param {number} step - Current step (1, 2, or 3)
     */
    static updateProgress(step) {
        const steps = document.querySelectorAll('.step');
        steps.forEach((stepEl, index) => {
            if (index + 1 <= step) {
                stepEl.classList.add('active');
            } else {
                stepEl.classList.remove('active');
            }
        });
    }

    /**
     * Show state container
     * @param {string} stateId - State container ID
     */
    static showState(stateId) {
        // Hide all states
        const states = document.querySelectorAll('.state-container');
        states.forEach(state => state.classList.remove('active'));

        // Show target state
        const targetState = document.getElementById(stateId);
        if (targetState) {
            targetState.classList.add('active');
        }
    }

    /**
     * Format date for display
     * @param {string|Date} date - Date to format
     * @returns {string} Formatted date
     */
    static formatDate(date) {
        const d = new Date(date);
        return d.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    /**
     * Format currency
     * @param {number} amount - Amount in USD
     * @returns {string} Formatted currency
     */
    static formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 6
        }).format(amount);
    }

    /**
     * Format processing time
     * @param {number} seconds - Time in seconds
     * @returns {string} Formatted time
     */
    static formatTime(seconds) {
        if (seconds < 1) {
            return `${Math.round(seconds * 1000)}ms`;
        }
        return `${seconds.toFixed(2)}s`;
    }

    /**
     * Create session card element
     * @param {Object} session - Session data
     * @returns {HTMLElement} Session card element
     */
    static createSessionCard(session) {
        const card = document.createElement('div');
        card.className = 'session-card';
        card.dataset.sessionId = session.session_id;

        card.innerHTML = `
            <div class="session-card-header">
                <div class="session-name">${this.escapeHtml(session.name)}</div>
                <div class="session-date">${this.formatDate(session.created_at)}</div>
            </div>
            <div class="session-project">${this.escapeHtml(session.project_title)}</div>
            <div class="session-id">ID: ${session.session_id}</div>
        `;

        return card;
    }

    /**
     * Create AI agent card element
     * @param {Object} agent - Agent data
     * @param {boolean} selected - Whether agent is selected
     * @param {boolean} disabled - Whether agent is disabled
     * @returns {HTMLElement} AI card element
     */
    static createAICard(agent, selected = false, disabled = false) {
        const card = document.createElement('div');
        card.className = `ai-card ${selected ? 'selected' : ''} ${disabled ? 'disabled' : ''}`;
        card.dataset.agentKey = agent.key;

        card.innerHTML = `
            <div class="ai-card-header">
                <div class="ai-name">${this.escapeHtml(agent.display_name)}</div>
                ${selected ? '<div class="ai-selected-badge">Selected</div>' : ''}
            </div>
            <div class="ai-description">${this.escapeHtml(agent.description)}</div>
            <div class="ai-pricing">
                <div class="price-item">
                    <div class="price-label">Input</div>
                    <div class="price-value">${this.formatCurrency(agent.input_price)}/1K</div>
                </div>
                <div class="price-item">
                    <div class="price-label">Output</div>
                    <div class="price-value">${this.formatCurrency(agent.output_price)}/1K</div>
                </div>
            </div>
        `;

        return card;
    }

    /**
     * Convert markdown-like text to HTML
     * @param {string} text - Text with markdown formatting
     * @returns {string} HTML formatted text
     */
    static markdownToHtml(text) {
        if (!text) return '';
        
        let html = text;
        
        // Convert headers (### Title -> <h3>Title</h3>)
        html = html.replace(/^### (.*$)/gm, '<h3>$1</h3>');
        html = html.replace(/^## (.*$)/gm, '<h2>$1</h2>');
        html = html.replace(/^# (.*$)/gm, '<h1>$1</h1>');
        
        // Convert bold (**text** -> <strong>text</strong>)
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Convert italic (*text* -> <em>text</em>)
        html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Convert inline code (`code` -> <code>code</code>)
        html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        // Convert code blocks (```code``` -> <pre><code>code</code></pre>)
        html = html.replace(/```(\w+)?\n?([\s\S]*?)```/g, (match, lang, code) => {
            const language = lang ? ` class="language-${lang}"` : '';
            return `<pre><code${language}>${code.trim()}</code></pre>`;
        });
        
        // Convert horizontal rules (--- -> <hr>)
        html = html.replace(/^---$/gm, '<hr>');
        
        // Convert line breaks to <br> but preserve paragraph structure
        html = html.replace(/\n\n/g, '</p><p>');
        html = html.replace(/\n/g, '<br>');
        
        // Wrap in paragraph tags if not already wrapped
        if (!html.startsWith('<')) {
            html = '<p>' + html + '</p>';
        }
        
        // Clean up empty paragraphs
        html = html.replace(/<p><\/p>/g, '');
        html = html.replace(/<p><br><\/p>/g, '');
        
        return html;
    }

    /**
     * Create message element
     * @param {string} content - Message content
     * @param {string} role - Message role (user/assistant)
     * @param {Object} metadata - Message metadata
     * @returns {HTMLElement} Message element
     */
    static createMessage(content, role, metadata = {}) {
        const message = document.createElement('div');
        message.className = `message ${role}`;

        let metadataHtml = '';
        if (role === 'assistant' && metadata) {
            const modelName = metadata.display_name || metadata.model || 'AI';
            metadataHtml = `
                <div class="message-metadata">
                    <span class="message-model">${this.escapeHtml(modelName)}</span>
                    <span class="message-time">${this.formatTime(metadata.processing_time_seconds || 0)}</span>
                    <span class="message-cost">${this.formatCurrency(metadata.cost_usd || 0)}</span>
                </div>
            `;
        }

        // For assistant messages, convert markdown to HTML
        // For user messages, keep as plain text
        const messageContent = role === 'assistant' 
            ? this.markdownToHtml(content)
            : this.escapeHtml(content);

        message.innerHTML = `
            <div class="message-content">${messageContent}</div>
            ${metadataHtml}
        `;

        return message;
    }

    /**
     * Update AI status
     * @param {string} aiId - AI identifier (ai-1 or ai-2)
     * @param {string} status - Status (ready, processing, error)
     * @param {string} text - Status text
     */
    static updateAIStatus(aiId, status, text) {
        const statusEl = document.getElementById(`${aiId}-status`);
        if (statusEl) {
            statusEl.className = `ai-status ${status}`;
            statusEl.textContent = text;
        }
    }

    /**
     * Scroll to bottom of messages container
     * @param {string} containerId - Container ID
     */
    static scrollToBottom(containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            container.scrollTop = container.scrollHeight;
        }
    }

    /**
     * Escape HTML to prevent XSS
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    static escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Debounce function calls
     * @param {Function} func - Function to debounce
     * @param {number} wait - Wait time in milliseconds
     * @returns {Function} Debounced function
     */
    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Make UIUtils globally available
window.UIUtils = UIUtils;