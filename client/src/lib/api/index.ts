// Main API exports - central point for all API functionality
// Provides organized structure for all API modules

// Export all API modules for direct importing
export { authApi } from './auth';
export { cartApi } from './cart';
export { chatApi } from './chat';
export { productsApi } from './products';
export { usersApi } from './users';
export { ordersApi } from './orders';
export { ApiError, apiRequest, apiGet, apiPost, apiPut, apiDelete } from './client';
