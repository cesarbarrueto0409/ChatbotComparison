/**
 * AI Selection State Handler
 * Manages AI agent selection for comparison
 */

class AISelectionState {
    constructor() {
        this.availableAgents = [];
        this.selectedAgents = [];
        this.sessionId = null;
        this.init();
    }

    /**
     * Initialize the AI selection state
     */
    init() {
        this.bindEvents();
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        // Event delegation for AI card clicks
        const firstAIContainer = document.getElementById('first-ai-options');
        const secondAIContainer = document.getElementById('second-ai-options');

        if (firstAIContainer) {
            firstAIContainer.addEventListener('click', (e) => {
                const card = e.target.closest('.ai-card');
                if (card && !card.classList.contains('disabled')) {
                    this.selectFirstAgent(card.dataset.agentKey);
                }
            });
        }

        if (secondAIContainer) {
            secondAIContainer.addEventListener('click', (e) => {
                const card = e.target.closest('.ai-card');
                if (card && !card.classList.contains('disabled')) {
                    this.selectSecondAgent(card.dataset.agentKey);
                }
            });
        }
    }

    /**
     * Load available AI agents
     * @param {string} sessionId - Session ID
     */
    async loadAvailableAgents(sessionId) {
        this.sessionId = sessionId;
        
        try {
            UIUtils.showLoading('Loading AI agents...');
            
            const response = await apiClient.getAvailableAgents(sessionId);
            
            if (response.success && response.available_agents) {
                this.availableAgents = response.available_agents;
                this.renderFirstAgentOptions();
            } else {
                UIUtils.showError('Error loading AI agents');
            }
        } catch (error) {
            console.error('Error loading AI agents:', error);
            UIUtils.showError('Error loading AI agents: ' + error.message);
        } finally {
            UIUtils.hideLoading();
        }
    }

    /**
     * Render first agent selection options
     */
    renderFirstAgentOptions() {
        const container = document.getElementById('first-ai-options');
        if (!container) return;

        if (this.availableAgents.length === 0) {
            container.innerHTML = '<div class="loading">No AI agents available.</div>';
            return;
        }

        container.innerHTML = '';
        
        this.availableAgents.forEach(agent => {
            const card = UIUtils.createAICard(agent, false, false);
            container.appendChild(card);
        });
    }

    /**
     * Render second agent selection options
     */
    async renderSecondAgentOptions() {
        try {
            const response = await apiClient.getSecondAgentOptions(this.sessionId);
            
            if (response.success && response.available_agents) {
                const container = document.getElementById('second-ai-options');
                if (!container) return;

                container.innerHTML = '';
                
                response.available_agents.forEach(agent => {
                    const card = UIUtils.createAICard(agent, false, false);
                    container.appendChild(card);
                });

                // Show second selection section
                const secondSection = document.getElementById('second-ai-section');
                if (secondSection) {
                    secondSection.style.display = 'block';
                }
            }
        } catch (error) {
            console.error('Error loading second agent options:', error);
            UIUtils.showError('Error loading second agent options: ' + error.message);
        }
    }

    /**
     * Select first AI agent
     * @param {string} agentKey - Agent key to select
     */
    async selectFirstAgent(agentKey) {
        try {
            UIUtils.showLoading('Selecting first agent...');
            
            const response = await apiClient.selectFirstAgent(this.sessionId, agentKey);
            
            if (response.success) {
                // Update UI to show selection
                this.updateFirstAgentSelection(agentKey);
                
                // Load second agent options
                await this.renderSecondAgentOptions();
            } else {
                UIUtils.showError('Error selecting first agent');
            }
        } catch (error) {
            console.error('Error selecting first agent:', error);
            UIUtils.showError('Error selecting first agent: ' + error.message);
        } finally {
            UIUtils.hideLoading();
        }
    }

    /**
     * Select second AI agent
     * @param {string} agentKey - Agent key to select
     */
    async selectSecondAgent(agentKey) {
        try {
            UIUtils.showLoading('Selecting second agent...');
            
            const response = await apiClient.selectSecondAgent(this.sessionId, agentKey);
            
            if (response.success && response.ready_for_conversation) {
                // Update UI to show selection
                this.updateSecondAgentSelection(agentKey);
                
                // Prepare selected agents data
                const selectedAgents = this.availableAgents.filter(agent => 
                    response.selected_agents.includes(agent.key)
                );
                
                // Notify state manager
                if (window.stateManager) {
                    window.stateManager.onAISelectionComplete(selectedAgents);
                }
            } else {
                UIUtils.showError('Error selecting second agent');
            }
        } catch (error) {
            console.error('Error selecting second agent:', error);
            UIUtils.showError('Error selecting second agent: ' + error.message);
        } finally {
            UIUtils.hideLoading();
        }
    }

    /**
     * Update UI to show first agent selection
     * @param {string} agentKey - Selected agent key
     */
    updateFirstAgentSelection(agentKey) {
        this.updateAgentSelection('first-ai-options', agentKey, false);
    }

    /**
     * Update UI to show second agent selection
     * @param {string} agentKey - Selected agent key
     */
    updateSecondAgentSelection(agentKey) {
        this.updateAgentSelection('second-ai-options', agentKey, true);
    }

    /**
     * Generic method to update agent selection UI
     * @param {string} containerId - Container ID
     * @param {string} agentKey - Selected agent key
     * @param {boolean} disableOthers - Whether to disable other cards
     */
    updateAgentSelection(containerId, agentKey, disableOthers) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const cards = container.querySelectorAll('.ai-card');
        cards.forEach(card => {
            if (card.dataset.agentKey === agentKey) {
                card.classList.add('selected');
                
                // Add selected badge if not present
                if (!card.querySelector('.ai-selected-badge')) {
                    const header = card.querySelector('.ai-card-header');
                    const badge = document.createElement('div');
                    badge.className = 'ai-selected-badge';
                    badge.textContent = 'Selected';
                    header.appendChild(badge);
                }
            } else {
                card.classList.remove('selected');
                
                if (disableOthers) {
                    card.classList.add('disabled');
                } else {
                    // Don't disable other cards - allow re-selection
                    card.classList.remove('disabled');
                }
                
                // Remove selected badge
                const badge = card.querySelector('.ai-selected-badge');
                if (badge) {
                    badge.remove();
                }
            }
        });
    }

    /**
     * Reset the state
     */
    reset() {
        this.availableAgents = [];
        this.selectedAgents = [];
        this.sessionId = null;

        // Clear UI
        const firstContainer = document.getElementById('first-ai-options');
        const secondContainer = document.getElementById('second-ai-options');
        const secondSection = document.getElementById('second-ai-section');

        if (firstContainer) {
            firstContainer.innerHTML = '<div class="loading">Loading AI options...</div>';
        }

        if (secondContainer) {
            secondContainer.innerHTML = '';
        }

        if (secondSection) {
            secondSection.style.display = 'none';
        }
    }
}

// Make AISelectionState globally available
window.AISelectionState = AISelectionState;