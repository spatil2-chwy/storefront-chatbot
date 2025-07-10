// Main API exports - central point for all API functionality
// Provides both new organized structure and backward compatibility

// Export all API modules for direct importing
export { authApi } from './auth';
export { chatApi } from './chat';
export { productsApi } from './products';
export { usersApi } from './users';
export { ApiError, apiRequest, apiGet, apiPost } from './client';

// Legacy compatibility - old api object for backward compatibility
// Can be removed once all components are migrated
import { productsApi } from './products';
import { chatApi } from './chat';
import { usersApi } from './users';

// Legacy API object (deprecated - use specific modules instead)
export const api = {
  // Product methods
  searchProducts: productsApi.searchProducts,
  getSearchStats: productsApi.getSearchStats,
  getProduct: productsApi.getProduct,
  compareProducts: productsApi.compareProducts,
  askAboutProduct: productsApi.askAboutProduct,
  
  // Chat methods
  chatbot: chatApi.chatbot,
  chatbotStream: chatApi.chatbotStream,
  getPersonalizedGreeting: chatApi.getPersonalizedGreeting,
  searchAndChat: chatApi.searchAndChat,
  
  // User methods
  getUserPets: usersApi.getUserPets,
};
