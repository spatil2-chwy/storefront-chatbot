// Base HTTP client for all API calls
// Handles common stuff like base URL, error handling, and request/response processing

const API_BASE_URL = 'http://localhost:8000';

// Custom error class for API errors
export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

// Main request function - handles all HTTP operations
export async function apiRequest(
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  // Set default options with auth and content type
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    credentials: 'include', // Include cookies for auth
    ...options,
  };

  const response = await fetch(url, defaultOptions);
  
  // Throw error for non-2xx responses
  if (!response.ok) {
    throw new ApiError(response.status, `API request failed: ${response.statusText}`);
  }
  
  return response;
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