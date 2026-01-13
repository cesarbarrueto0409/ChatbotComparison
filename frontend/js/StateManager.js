/**
 * Frontend State Manager
 * Coordinates transitions between different UI states
 */

class StateManager {
    constructor() {
        this.currentState = 'user-selection';
        this.sessionData = {};
        this.states = {
            'user-selection': null,
            'ai-selection': null,
            'chat-comparison': null
        };
        
        this.init();
    }

    /**
     * Initialize state manager
     */
    init() {
        // Check if required classes are available
        if (!window.UserSelectionState) {
            console.error('UserSelectionState not available');
            return;
        }
        
        if (!window.UIUtils) {
            console.error('UIUtils not available');
            return;
        }
        
        try {
            // Initialize state handlers
            this.states['user-selection'] = new UserSelectionState();
            // AI selection and chat states will be initialized when needed
            
            // Show initial state
            this.showState('user-selection');
            UIUtils.updateProgress(1);
            
            // Bind navigation events
            this.bindNavigationEvents();
            
            console.log('StateManager initialized successfully');
        } catch (error) {
            console.error('Error initializing StateManager:', error);
            throw error;
        }
    }

    /**
     * Bind navigation event listeners
     */
    bindNavigationEvents() {
        // Back to user selection
        const backToUserBtn = document.getElementById('back-to-user');
        if (backToUserBtn) {
            backToUserBtn.addEventListener('click', () => {
                this.transitionToUserSelection();
            });
        }

        // Back to AI selection
        const backToAIBtn = document.getElementById('back-to-ai');
        if (backToAIBtn) {
            backToAIBtn.addEventListener('click', () => {
                this.transitionToAISelection();
            });
        }

        // New session
        const newSessionBtn = document.getElementById('new-session');
        if (newSessionBtn) {
            newSessionBtn.addEventListener('click', () => {
                this.resetToUserSelection();
            });
        }

        // Close error modal
        const closeErrorBtn = document.getElementById('close-error');
        if (closeErrorBtn) {
            closeErrorBtn.addEventListener('click', () => {
                UIUtils.hideError();
            });
        }
    }

    /**
     * Show specific state
     * @param {string} stateName - State name to show
     */
    showState(stateName) {
        this.currentState = stateName;
        UIUtils.showState(`${stateName}-state`);
    }

    /**
     * Set session data
     * @param {Object} data - Session data
     */
    setSessionData(data) {
        this.sessionData = { ...this.sessionData, ...data };
        console.log('Session data updated:', this.sessionData);
    }

    /**
     * Get session data
     * @returns {Object} Current session data
     */
    getSessionData() {
        return this.sessionData;
    }

    /**
     * Transition to AI selection state
     */
    transitionToAISelection() {
        if (!this.sessionData.session_id) {
            UIUtils.showError('No session selected');
            return;
        }

        // Initialize AI selection state if not already done
        if (!this.states['ai-selection']) {
            if (!window.AISelectionState) {
                UIUtils.showError('AISelectionState is not available');
                return;
            }
            this.states['ai-selection'] = new AISelectionState();
        }

        // Update user info display
        this.updateUserInfoDisplay();

        // Load available agents
        this.states['ai-selection'].loadAvailableAgents(this.sessionData.session_id);

        this.showState('ai-selection');
        UIUtils.updateProgress(2);
    }

    /**
     * Transition to chat comparison state
     */
    transitionToChatComparison() {
        if (!this.sessionData.session_id || !this.sessionData.selectedAgents) {
            UIUtils.showError('Missing session data or selected agents');
            return;
        }

        // Initialize chat comparison state if not already done
        if (!this.states['chat-comparison']) {
            if (!window.ChatComparisonState) {
                UIUtils.showError('ChatComparisonState is not available');
                return;
            }
            this.states['chat-comparison'] = new ChatComparisonState();
        }

        // Update session info display
        this.updateChatSessionInfo();

        // Initialize chat interface
        this.states['chat-comparison'].initializeChat(this.sessionData);

        this.showState('chat-comparison');
        UIUtils.updateProgress(3);
    }

    /**
     * Transition back to user selection
     */
    transitionToUserSelection() {
        this.showState('user-selection');
        UIUtils.updateProgress(1);
        
        // Reset user selection state
        if (this.states['user-selection']) {
            this.states['user-selection'].reset();
        }
    }

    /**
     * Reset to user selection and clear all data
     */
    resetToUserSelection() {
        this.sessionData = {};
        
        // Reset all states
        Object.keys(this.states).forEach(stateName => {
            if (this.states[stateName] && typeof this.states[stateName].reset === 'function') {
                this.states[stateName].reset();
            }
        });

        this.transitionToUserSelection();
    }

    /**
     * Update user info display in AI selection state
     */
    updateUserInfoDisplay() {
        const userInfoEl = document.getElementById('current-user-info');
        if (userInfoEl && this.sessionData.name && this.sessionData.project_title) {
            userInfoEl.textContent = `${this.sessionData.name} - ${this.sessionData.project_title}`;
        }
    }

    /**
     * Update session info in chat comparison state
     */
    updateChatSessionInfo() {
        const userNameEl = document.getElementById('chat-user-name');
        const projectTitleEl = document.getElementById('chat-project-title');
        const aiNamesEl = document.getElementById('chat-ai-names');

        if (userNameEl && this.sessionData.name) {
            userNameEl.textContent = this.sessionData.name;
        }

        if (projectTitleEl && this.sessionData.project_title) {
            projectTitleEl.textContent = this.sessionData.project_title;
        }

        if (aiNamesEl && this.sessionData.selectedAgents) {
            const agentNames = this.sessionData.selectedAgents.map(agent => agent.display_name);
            aiNamesEl.textContent = agentNames.join(' vs ');
        }
    }

    /**
     * Handle AI selection completion
     * @param {Array} selectedAgents - Selected AI agents
     */
    onAISelectionComplete(selectedAgents) {
        this.setSessionData({ selectedAgents });
        this.transitionToChatComparison();
    }

    /**
     * Get current state name
     * @returns {string} Current state name
     */
    getCurrentState() {
        return this.currentState;
    }
}

// Make StateManager class available globally, but don't create instance yet
window.StateManager = StateManager;