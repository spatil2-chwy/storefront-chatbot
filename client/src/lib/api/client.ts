// Base HTTP client for all API calls
// Handles common stuff like base URL, error handling, and request/response processing

const API_BASE_URL = 'http://localhost:8000';

// Request deduplication cache
const pendingRequests = new Map<string, Promise<Response>>();

// Custom error class for API errors
export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

// Generate cache key for request deduplication
function getRequestKey(endpoint: string, options: RequestInit = {}): string {
  const method = options.method || 'GET';
  const body = options.body ? JSON.stringify(options.body) : '';
  return `${method}:${endpoint}:${body}`;
}

// Main request function - handles all HTTP operations with deduplication
export async function apiRequest(
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> {
  const url = `${API_BASE_URL}${endpoint}`;
  const requestKey = getRequestKey(endpoint, options);
  
  // Check if there's already a pending request with the same key
  if (pendingRequests.has(requestKey)) {
    return pendingRequests.get(requestKey)!;
  }
  
  // Set default options with auth and content type
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    credentials: 'include', // Include cookies for auth
    ...options,
  };

  // Create the request promise
  const requestPromise = fetch(url, defaultOptions).then(response => {
    // Remove from pending requests when completed
    pendingRequests.delete(requestKey);
    
    // Throw error for non-2xx responses
    if (!response.ok) {
      throw new ApiError(response.status, `API request failed: ${response.statusText}`);
    }
    
    return response;
  }).catch(error => {
    // Remove from pending requests on error
    pendingRequests.delete(requestKey);
    throw error;
  });

  // Store the pending request
  pendingRequests.set(requestKey, requestPromise);
  
  return requestPromise;
}

// Helper for GET requests
export async function apiGet<T>(endpoint: string): Promise<T> {
  const response = await apiRequest(endpoint);
  return response.json();
}

// Helper for POST requests
export async function apiPost<T>(endpoint: string, data?: unknown): Promise<T> {
  const response = await apiRequest(endpoint, {
    method: 'POST',
    body: data ? JSON.stringify(data) : undefined,
  });
  return response.json();
} 