/**
 * Main application entry point
 * Initializes the chatbot comparison application
 */

class ChatbotApp {
    constructor() {
        this.initialized = false;
        this.init();
    }

    /**
     * Initialize the application
     */
    async init() {
        try {
            console.log('Initializing Chatbot Comparison App...');
            
            // Wait for DOM to be ready
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.start());
            } else {
                this.start();
            }
            
        } catch (error) {
            console.error('Error initializing app:', error);
            this.showInitializationError(error);
        }
    }

    /**
     * Start the application
     */
    async start() {
        try {
            // Wait a bit for all scripts to load
            await this.waitForScripts();
            
            // Check if all required classes are available
            this.checkDependencies();
            
            // Perform health check
            await this.performHealthCheck();
            
            // Initialize state manager (this will initialize the first state)
            if (!window.stateManager) {
                console.log('Initializing State Manager...');
                window.stateManager = new StateManager();
            }
            
            // Set up global error handlers
            this.setupErrorHandlers();
            
            // Set up keyboard shortcuts
            this.setupKeyboardShortcuts();
            
            this.initialized = true;
            console.log('App initialized successfully!');
            
        } catch (error) {
            console.error('Error starting app:', error);
            this.showInitializationError(error);
        }
    }

    /**
     * Wait for all scripts to load
     */
    async waitForScripts() {
        const maxWait = 5000; // 5 seconds max
        const checkInterval = 100; // Check every 100ms
        let waited = 0;

        return new Promise((resolve, reject) => {
            const checkScripts = () => {
                const requiredClasses = [
                    'UIUtils',
                    'UserSelectionState',
                    'AISelectionState', 
                    'ChatComparisonState',
                    'StateManager'
                ];

                const missing = requiredClasses.filter(className => !window[className]);
                
                if (missing.length === 0 && window.apiClient) {
                    console.log('All scripts loaded successfully');
                    resolve();
                    return;
                }

                waited += checkInterval;
                if (waited >= maxWait) {
                    console.warn('Timeout waiting for scripts. Missing:', missing);
                    reject(new Error(`Timeout waiting for scripts. Missing: ${missing.join(', ')}`));
                    return;
                }

                setTimeout(checkScripts, checkInterval);
            };

            checkScripts();
        });
    }

    /**
     * Check if all required dependencies are loaded
     */
    checkDependencies() {
        const requiredClasses = [
            'UIUtils',
            'UserSelectionState',
            'AISelectionState', 
            'ChatComparisonState',
            'StateManager'
        ];

        const missing = requiredClasses.filter(className => {
            const exists = !!window[className];
            if (!exists) {
                console.error(`Missing class: ${className}`);
            }
            return !exists;
        });
        
        if (missing.length > 0) {
            throw new Error(`Missing required classes: ${missing.join(', ')}`);
        }

        if (!window.apiClient) {
            console.error('Missing: apiClient');
            throw new Error('API client not initialized');
        }

        console.log('All dependencies loaded');
    }

    /**
     * Perform API health check
     */
    async performHealthCheck() {
        try {
            console.log('Performing health check...');
            const health = await apiClient.healthCheck();
            
            if (health.status !== 'healthy') {
                throw new Error('Backend service is not healthy');
            }
            
            console.log('Backend health check passed');
        } catch (error) {
            console.warn('Health check failed:', error.message);
            // Don't throw error here, allow app to continue
            // The user will see errors when they try to use features
        }
    }

    /**
     * Set up global error handlers
     */
    setupErrorHandlers() {
        // Handle unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            
            // Show user-friendly error for API-related errors
            if (event.reason && event.reason.message) {
                if (event.reason.message.includes('fetch')) {
                    UIUtils.showError('Connection error with server. Please verify that the backend is running.');
                } else {
                    UIUtils.showError('Unexpected error: ' + event.reason.message);
                }
            }
            
            event.preventDefault();
        });

        // Handle general JavaScript errors
        window.addEventListener('error', (event) => {
            console.error('JavaScript error:', event.error);
            
            // Only show error modal for critical errors
            if (event.error && event.error.message && !event.error.message.includes('Script error')) {
                UIUtils.showError('Application error: ' + event.error.message);
            }
        });
    }

    /**
     * Set up keyboard shortcuts
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (event) => {
            // Escape key to close modals
            if (event.key === 'Escape') {
                UIUtils.hideError();
                UIUtils.hideLoading();
            }

            // Ctrl/Cmd + Enter to send message (when in chat state)
            if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
                if (window.stateManager && window.stateManager.getCurrentState() === 'chat-comparison') {
                    const messageForm = document.getElementById('message-form');
                    if (messageForm) {
                        messageForm.dispatchEvent(new Event('submit'));
                    }
                }
            }

            // Ctrl/Cmd + R to reset (go back to user selection)
            if ((event.ctrlKey || event.metaKey) && event.key === 'r') {
                event.preventDefault();
                if (window.stateManager) {
                    if (confirm('Are you sure you want to reset the application?')) {
                        window.stateManager.resetToUserSelection();
                    }
                }
            }
        });
    }

    /**
     * Show initialization error
     * @param {Error} error - Error that occurred during initialization
     */
    showInitializationError(error) {
        // Create error display if UI utils not available
        const errorHtml = `
            <div style="
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: white;
                padding: 2rem;
                border-radius: 15px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                max-width: 500px;
                text-align: center;
                z-index: 9999;
            ">
                <h2 style="color: #e53e3e; margin-bottom: 1rem;">Initialization Error</h2>
                <p style="color: #4a5568; margin-bottom: 1.5rem;">
                    The application could not be initialized correctly.
                </p>
                <details style="text-align: left; margin-bottom: 1rem;">
                    <summary style="cursor: pointer; color: #667eea;">View technical details</summary>
                    <pre style="
                        background: #f7fafc;
                        padding: 1rem;
                        border-radius: 5px;
                        margin-top: 0.5rem;
                        font-size: 0.875rem;
                        overflow-x: auto;
                    ">${error.message}\n\n${error.stack || ''}</pre>
                </details>
                <button onclick="location.reload()" style="
                    background: #667eea;
                    color: white;
                    border: none;
                    padding: 0.75rem 1.5rem;
                    border-radius: 10px;
                    cursor: pointer;
                    font-size: 1rem;
                ">Reload Page</button>
            </div>
            <div style="
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.7);
                z-index: 9998;
            "></div>
        `;

        document.body.insertAdjacentHTML('beforeend', errorHtml);
    }

    /**
     * Get app status
     * @returns {Object} App status information
     */
    getStatus() {
        return {
            initialized: this.initialized,
            currentState: window.stateManager ? window.stateManager.getCurrentState() : null,
            sessionData: window.stateManager ? window.stateManager.getSessionData() : null
        };
    }
}

// Initialize the application
console.log('Starting Chatbot Comparison Application...');
window.chatbotApp = new ChatbotApp();

// Make app status available globally for debugging
window.getAppStatus = () => window.chatbotApp.getStatus();

// Development helpers
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    console.log('Development mode detected');
    
    // Add development helpers to window
    window.dev = {
        resetApp: () => {
            if (window.stateManager) {
                window.stateManager.resetToUserSelection();
            }
        },
        getSessionData: () => {
            return window.stateManager ? window.stateManager.getSessionData() : null;
        },
        testAPI: async () => {
            try {
                const health = await apiClient.healthCheck();
                console.log('API Health:', health);
                return health;
            } catch (error) {
                console.error('API Test failed:', error);
                return error;
            }
        },
        checkClasses: () => {
            const classes = ['UIUtils', 'UserSelectionState', 'AISelectionState', 'ChatComparisonState', 'StateManager'];
            const status = {};
            classes.forEach(cls => {
                status[cls] = !!window[cls];
            });
            status.apiClient = !!window.apiClient;
            console.table(status);
            return status;
        }
    };
    
    console.log('Development helpers available: window.dev');
    console.log('Use window.dev.checkClasses() to debug loading issues');
}