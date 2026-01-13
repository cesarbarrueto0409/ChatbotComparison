/**
 * API utility functions for chatbot backend communication
 */

class APIClient {
    constructor() {
        // Use environment-based URL configuration
        // In development: localhost:3000, in production: actual domain
        this.baseURL = this.getBaseURL();
        this.defaultHeaders = {
            'Content-Type': 'application/json'
        };
    }

    /**
     * Get base URL based on environment
     * @returns {string} Base URL for API calls
     */
    getBaseURL() {
        // Check if we're in development (localhost)
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return 'http://localhost:3000/chatbot';
        }
        
        // In production, use relative path or environment variable
        // This assumes the API is served from the same domain with /api prefix
        const protocol = window.location.protocol;
        const host = window.location.host;
        
        // Option 1: Same domain with /api prefix
        return `${protocol}//${host}/api/chatbot`;
        
        // Option 2: Environment variable (if using build tools like Vite/Webpack)
        // return process.env.REACT_APP_API_URL || `${protocol}//${host}/api/chatbot`;
    }

    /**
     * Make HTTP request to API
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Request options
     * @returns {Promise<Object>} Response data
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: { ...this.defaultHeaders, ...options.headers },
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API Request failed: ${endpoint}`, error);
            throw error;
        }
    }

    /**
     * Get all available sessions
     * @returns {Promise<Object>} Sessions data
     */
    async getSessions() {
        return this.request('/sessions');
    }

    /**
     * Create new user session
     * @param {string} name - User name
     * @param {string} projectTitle - Project title
     * @returns {Promise<Object>} Session creation response
     */
    async createSession(name, projectTitle) {
        return this.request('/sessions', {
            method: 'POST',
            body: JSON.stringify({
                action: 'create',
                name: name,
                project_title: projectTitle
            })
        });
    }

    /**
     * Select existing session
     * @param {string} sessionId - Session ID to select
     * @returns {Promise<Object>} Session selection response
     */
    async selectSession(sessionId) {
        return this.request('/sessions', {
            method: 'POST',
            body: JSON.stringify({
                action: 'select',
                session_id: sessionId
            })
        });
    }

    /**
     * Get available AI agents
     * @param {string} sessionId - Session ID
     * @returns {Promise<Object>} Available agents
     */
    async getAvailableAgents(sessionId) {
        return this.request('/ai-selection', {
            method: 'POST',
            body: JSON.stringify({
                session_id: sessionId,
                action: 'get_available'
            })
        });
    }

    /**
     * Select first AI agent
     * @param {string} sessionId - Session ID
     * @param {string} agentKey - Agent key to select
     * @returns {Promise<Object>} Selection response
     */
    async selectFirstAgent(sessionId, agentKey) {
        return this.request('/ai-selection', {
            method: 'POST',
            body: JSON.stringify({
                session_id: sessionId,
                action: 'select_first',
                agent_key: agentKey
            })
        });
    }

    /**
     * Get available options for second agent
     * @param {string} sessionId - Session ID
     * @returns {Promise<Object>} Available second agents
     */
    async getSecondAgentOptions(sessionId) {
        return this.request('/ai-selection', {
            method: 'POST',
            body: JSON.stringify({
                session_id: sessionId,
                action: 'get_second_options'
            })
        });
    }

    /**
     * Select second AI agent
     * @param {string} sessionId - Session ID
     * @param {string} agentKey - Agent key to select
     * @returns {Promise<Object>} Selection response
     */
    async selectSecondAgent(sessionId, agentKey) {
        return this.request('/ai-selection', {
            method: 'POST',
            body: JSON.stringify({
                session_id: sessionId,
                action: 'select_second',
                agent_key: agentKey
            })
        });
    }

    /**
     * Send chat message
     * @param {string} sessionId - Session ID
     * @param {string} message - Message to send
     * @returns {Promise<Object>} Chat response
     */
    async sendMessage(sessionId, message) {
        return this.request('/chat', {
            method: 'POST',
            body: JSON.stringify({
                session_id: sessionId,
                message: message
            })
        });
    }

    /**
     * Start chat message processing
     * @param {string} sessionId - Session ID
     * @param {string} message - Message to send
     * @returns {Promise<Object>} Request tracking info
     */
    async startChatMessage(sessionId, message) {
        return this.request('/chat/start', {
            method: 'POST',
            body: JSON.stringify({
                session_id: sessionId,
                message: message
            })
        });
    }

    /**
     * Get chat processing status
     * @param {string} requestId - Request ID
     * @returns {Promise<Object>} Status information
     */
    async getChatStatus(requestId) {
        return this.request(`/chat/status/${requestId}`);
    }

    /**
     * Health check
     * @returns {Promise<Object>} Health status
     */
    async healthCheck() {
        return this.request('/health');
    }
}

// Create global API client instance
window.apiClient = new APIClient();