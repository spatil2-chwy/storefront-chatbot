import { chatApi, productsApi } from '../../../lib/api';
import { ChatMessage } from '../../../types';
import { Product } from '../../../types';

interface ChatApiCallbacks {
  setSearchResults: (products: Product[]) => void;
  setCurrentSearchQuery: (query: string) => void;
  setHasSearched: (searched: boolean) => void;
}

export const useChatApi = (callbacks: ChatApiCallbacks) => {
  const { setSearchResults, setCurrentSearchQuery, setHasSearched } = callbacks;

  const generateComparisonResponse = async (
    query: string,
    comparingProducts: Product[],
    chatHistory: any[]
  ): Promise<ChatMessage> => {
    const response = await productsApi.compareProducts(query, comparingProducts, chatHistory);
    return {
      id: (Date.now() + 1).toString(),
      content: response,
      sender: 'ai',
      timestamp: new Date(),
      comparisonProducts: comparingProducts,
      comparisonProductCount: comparingProducts.length,
    };
  };

  const generateProductResponse = async (
    query: string,
    product: Product,
    chatHistory: any[]
  ): Promise<ChatMessage> => {
    const response = await productsApi.askAboutProduct(query, product, chatHistory);
    return {
      id: (Date.now() + 1).toString(),
      content: response,
      sender: 'ai',
      timestamp: new Date(),
      productTitle: `${product.brand} ${product.title}`,
    };
  };

  const generateGeneralResponse = async (
    query: string,
    chatHistory: any[],
    customerKey?: number
  ): Promise<ChatMessage> => {
    const response = await chatApi.chatbot(query, chatHistory, customerKey);
    
    // Update global search state with the products from the response
    if (response.products && response.products.length > 0) {
      setSearchResults(response.products);
      setCurrentSearchQuery(query);
      setHasSearched(true);
    }

    return {
      id: (Date.now() + 1).toString(),
      content: response.message,
      sender: 'ai',
      timestamp: new Date(),
    };
  };

  const generateErrorResponse = (): ChatMessage => {
    return {
      id: (Date.now() + 1).toString(),
      content: "Sorry, I'm having trouble processing your request right now. Please try again in a moment.",
      sender: 'ai',
      timestamp: new Date(),
    };
  };

  return {
    generateComparisonResponse,
    generateProductResponse,
    generateGeneralResponse,
    generateErrorResponse,
  };
}; 