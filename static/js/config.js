// Configuration for AI Cash-Revolution Frontend
const CONFIG = {
    // Railway Backend URL - Using direct Railway URL
    API_BASE_URL: 'https://web-production-51f67.up.railway.app', // ✅ Connected to Railway backend
    
    // API Endpoints
    ENDPOINTS: {
        // Authentication
        register: '/register',
        login: '/token',
        me: '/me',
        
        // Signals
        topSignals: '/signals/top',
        userSignals: '/signals',
        
        // Trial signup
        trialSignup: '/api/trial-signup',
        
        // MT5 Integration
        mt5Connect: '/mt5/connect',
        mt5Status: '/mt5/status'
    },
    
    // Request configuration
    REQUEST_CONFIG: {
        timeout: 10000, // 10 seconds
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    }
};

// Helper function to get full API URL
function getApiUrl(endpoint) {
    return CONFIG.API_BASE_URL + CONFIG.ENDPOINTS[endpoint];
}

// Helper function to make authenticated requests
async function makeApiRequest(endpoint, options = {}) {
    const url = getApiUrl(endpoint);
    const token = localStorage.getItem('access_token');
    
    const config = {
        ...CONFIG.REQUEST_CONFIG,
        ...options,
        headers: {
            ...CONFIG.REQUEST_CONFIG.headers,
            ...(token && { 'Authorization': `Bearer ${token}` }),
            ...(options.headers || {})
        }
    };
    
    try {
        const response = await fetch(url, config);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        }
        
        return await response.text();
    } catch (error) {
        console.error(`API Request failed for ${endpoint}:`, error);
        throw error;
    }
}

// Export for use in other scripts
window.CONFIG = CONFIG;
window.getApiUrl = getApiUrl;
window.makeApiRequest = makeApiRequest;