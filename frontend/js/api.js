// API Configuration and Service
const API_CONFIG = {
    BASE_URL: 'http://localhost:5000/api',
    TIMEOUT: 30000,
    HEADERS: {
        'Content-Type': 'application/json'
    }
};

class APIService {
    constructor() {
        this.baseURL = API_CONFIG.BASE_URL;
    }

    async fetchWithTimeout(url, options = {}, timeout = API_CONFIG.TIMEOUT) {
        const controller = new AbortController();
        const id = setTimeout(() => controller.abort(), timeout);

        try {
            const response = await fetch(url, {
                ...options,
                signal: controller.signal,
                headers: {
                    ...API_CONFIG.HEADERS,
                    ...options.headers
                }
            });

            clearTimeout(id);

            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                throw new Error(error.error || `HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            clearTimeout(id);
            if (error.name === 'AbortError') {
                throw new Error('Request timeout - please try again');
            }
            throw error;
        }
    }

    async healthCheck() {
        try {
            const data = await this.fetchWithTimeout(`${this.baseURL}/health`);
            return data;
        } catch (error) {
            console.error('Health check failed:', error);
            return { status: 'error', message: error.message };
        }
    }

    async getAnswer(question) {
        try {
            const data = await this.fetchWithTimeout(
                `${this.baseURL}/answer`,
                {
                    method: 'POST',
                    body: JSON.stringify({ question })
                }
            );

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw new Error(`Failed to get answer: ${error.message}`);
        }
    }
}

// Export API service instance
const apiService = new APIService();