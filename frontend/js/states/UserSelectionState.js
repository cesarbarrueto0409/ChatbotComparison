/**
 * User Selection State Handler
 * Manages user session creation and selection
 */

class UserSelectionState {
    constructor() {
        this.sessions = [];
        this.selectedSession = null;
        this.init();
    }

    /**
     * Initialize the user selection state
     */
    init() {
        this.bindEvents();
        this.loadSessions();
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        // New session form submission
        const newSessionForm = document.getElementById('new-session-form');
        if (newSessionForm) {
            newSessionForm.addEventListener('submit', (e) => this.handleNewSession(e));
        }

        // Project title validation
        const projectTitleInput = document.getElementById('project-title');
        if (projectTitleInput) {
            projectTitleInput.addEventListener('input', 
                UIUtils.debounce((e) => this.validateProjectTitle(e.target.value), 500)
            );
        }
    }

    /**
     * Load existing sessions from API
     */
    async loadSessions() {
        try {
            UIUtils.showLoading('Loading sessions...');
            
            const response = await apiClient.getSessions();
            this.sessions = response.sessions || [];
            
            this.renderSessions();
        } catch (error) {
            console.error('Error loading sessions:', error);
            UIUtils.showError('Error loading sessions: ' + error.message);
        } finally {
            UIUtils.hideLoading();
        }
    }

    /**
     * Render sessions in the UI
     */
    renderSessions() {
        const container = document.getElementById('existing-sessions');
        if (!container) return;

        if (this.sessions.length === 0) {
            container.innerHTML = `
                <div class="loading">
                    No existing sessions found. Create a new session to get started.
                </div>
            `;
            return;
        }

        container.innerHTML = '';
        
        this.sessions.forEach(session => {
            const card = UIUtils.createSessionCard(session);
            card.addEventListener('click', () => this.selectSession(session.session_id));
            container.appendChild(card);
        });
    }

    /**
     * Handle new session form submission
     * @param {Event} event - Form submission event
     */
    async handleNewSession(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const name = formData.get('name').trim();
        const projectTitle = formData.get('project_title').trim();

        if (!name || !projectTitle) {
            UIUtils.showError('Please fill in all fields.');
            return;
        }

        try {
            UIUtils.showLoading('Creating new session...');
            
            const response = await apiClient.createSession(name, projectTitle);
            
            if (response.success) {
                this.selectedSession = {
                    session_id: response.session_id,
                    name: name,
                    project_title: projectTitle
                };
                
                // Notify state manager
                if (window.stateManager) {
                    window.stateManager.setSessionData(this.selectedSession);
                    window.stateManager.transitionToAISelection();
                }
            } else {
                UIUtils.showError('Error creating session.');
            }
        } catch (error) {
            console.error('Error creating session:', error);
            UIUtils.showError('Error creating session: ' + error.message);
        } finally {
            UIUtils.hideLoading();
        }
    }

    /**
     * Select an existing session
     * @param {string} sessionId - Session ID to select
     */
    async selectSession(sessionId) {
        try {
            UIUtils.showLoading('Selecting session...');
            
            const response = await apiClient.selectSession(sessionId);
            
            if (response.success) {
                const session = this.sessions.find(s => s.session_id === sessionId);
                this.selectedSession = session;
                
                // Notify state manager
                if (window.stateManager) {
                    window.stateManager.setSessionData(session);
                    window.stateManager.transitionToAISelection();
                }
            } else {
                UIUtils.showError('Error selecting session.');
            }
        } catch (error) {
            console.error('Error selecting session:', error);
            UIUtils.showError('Error selecting session: ' + error.message);
        } finally {
            UIUtils.hideLoading();
        }
    }

    /**
     * Validate project title uniqueness
     * @param {string} projectTitle - Project title to validate
     */
    async validateProjectTitle(projectTitle) {
        if (!projectTitle.trim()) return;

        const exists = this.sessions.some(session => 
            session.project_title.toLowerCase() === projectTitle.toLowerCase()
        );

        const input = document.getElementById('project-title');
        const submitButton = document.querySelector('#new-session-form button[type="submit"]');

        if (exists) {
            input.style.borderColor = '#f56565';
            input.style.boxShadow = '0 0 0 3px rgba(245, 101, 101, 0.1)';
            submitButton.disabled = true;
            
            // Show error message
            let errorMsg = input.parentNode.querySelector('.error-message');
            if (!errorMsg) {
                errorMsg = document.createElement('div');
                errorMsg.className = 'error-message';
                errorMsg.style.color = '#f56565';
                errorMsg.style.fontSize = '0.875rem';
                errorMsg.style.marginTop = '0.25rem';
                input.parentNode.appendChild(errorMsg);
            }
            errorMsg.textContent = 'This project title already exists. Please choose a different name.';
        } else {
            input.style.borderColor = '#48bb78';
            input.style.boxShadow = '0 0 0 3px rgba(72, 187, 120, 0.1)';
            submitButton.disabled = false;
            
            // Remove error message
            const errorMsg = input.parentNode.querySelector('.error-message');
            if (errorMsg) {
                errorMsg.remove();
            }
        }
    }

    /**
     * Reset the state
     */
    reset() {
        this.selectedSession = null;
        
        // Clear form
        const form = document.getElementById('new-session-form');
        if (form) {
            form.reset();
        }
        
        // Remove validation styles
        const projectInput = document.getElementById('project-title');
        if (projectInput) {
            projectInput.style.borderColor = '';
            projectInput.style.boxShadow = '';
            
            const errorMsg = projectInput.parentNode.querySelector('.error-message');
            if (errorMsg) {
                errorMsg.remove();
            }
        }
        
        // Reload sessions
        this.loadSessions();
    }
}

// Make UserSelectionState globally available
window.UserSelectionState = UserSelectionState;