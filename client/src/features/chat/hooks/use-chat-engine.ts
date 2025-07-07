import { useState, useRef, useEffect } from 'react';
import { useAuth } from '../../../lib/auth';
import { useGlobalChat } from '../context';
import { api } from '../../../lib/api';
import { ChatMessage } from '../../../types';

interface ChatEngineProps {
  initialQuery?: string;
  shouldClearChat?: boolean;
  preloadedChatResponse?: {message: string, history: any[], products: any[]};
  isLiveAgent: boolean;
  showInitialSearchGreeting: (query: string) => Promise<void>;
  showSearchGreeting: (message: string) => Promise<void>;
}

export const useChatEngine = ({
  initialQuery,
  shouldClearChat,
  preloadedChatResponse,
  isLiveAgent,
  showInitialSearchGreeting,
  showSearchGreeting
}: ChatEngineProps) => {
  const { user } = useAuth();
  const {
    messages,
    addMessage,
    clearMessages,
    currentContext,
    isInComparisonMode,
    comparingProducts,
    setSearchResults,
    setCurrentSearchQuery,
    setHasSearched
  } = useGlobalChat();

  const [isLoading, setIsLoading] = useState(false);
  const processedQueryRef = useRef<string>('');

  // Handle initial query processing
  useEffect(() => {
    if (initialQuery && initialQuery.trim() && initialQuery !== processedQueryRef.current && !isLiveAgent) {
      processedQueryRef.current = initialQuery; // Mark as processed
      
      // Clear chat if this is a new search and there are existing messages
      if (shouldClearChat && messages.length > 0) {
        clearMessages();
      }
      
      // Create and add user message immediately (don't wait for shouldOpen)
      const userMessage: ChatMessage = {
        id: Date.now().toString(),
        content: preloadedChatResponse ? `Searching for: ${initialQuery}` : initialQuery,
        sender: 'user',
        timestamp: new Date(),
      };
      
      addMessage(userMessage);
      
      // If we have a preloaded chat response, use it instead of making an API call
      if (preloadedChatResponse) {
        const aiResponse: ChatMessage = {
          id: (Date.now() + 1).toString(),
          content: preloadedChatResponse.message,
          sender: 'ai',
          timestamp: new Date(),
        };
        
        addMessage(aiResponse);
        
        // Update global search state with the products from the response
        if (preloadedChatResponse.products && preloadedChatResponse.products.length > 0) {
          setSearchResults(preloadedChatResponse.products);
          setCurrentSearchQuery(initialQuery);
          setHasSearched(true);
        }
        return;
      }
      
      setIsLoading(true);
      
      // Generate AI response
      generateInitialResponse(initialQuery);
    }
  }, [initialQuery, shouldClearChat, isLiveAgent, addMessage, clearMessages, preloadedChatResponse]);

  const generateInitialResponse = async (query: string) => {
    await showInitialSearchGreeting(query);

    try {
      let aiResponse: ChatMessage;

      // Prepare chat history for all endpoints
      const chatHistory = messages.map(msg => ({
        role: msg.sender === 'user' ? 'user' : 'assistant',
        content: msg.content
      }));

      // If in comparison mode and we have products to compare, call the backend
      if (isInComparisonMode && comparingProducts.length >= 2) {
        const response = await api.compareProducts(query, comparingProducts, chatHistory);
        aiResponse = {
          id: (Date.now() + 1).toString(),
          content: response,
          sender: 'ai',
          timestamp: new Date(),
          comparisonProducts: comparingProducts,
          comparisonProductCount: comparingProducts.length,
        };
      } else if (currentContext.type === 'product' && currentContext.product) {
        // If in product context, call the backend for product-specific questions
        const response = await api.askAboutProduct(query, currentContext.product, chatHistory);
        aiResponse = {
          id: (Date.now() + 1).toString(),
          content: response,
          sender: 'ai',
          timestamp: new Date(),
          productTitle: `${currentContext.product.brand} ${currentContext.product.title}`,
        };
      } else {
        // Use backend chatbot endpoint for general chat mode
        const chatHistory = messages.map(msg => ({
          role: msg.sender === 'user' ? 'user' : 'assistant',
          content: msg.content
        }));
        
        // NEW LOGIC: Always get products from chat endpoint for search queries
        // The backend will show "Searching for: {query}" and return products + follow-ups
        const response = await api.chatbot(query, chatHistory, user?.customer_key);
        aiResponse = {
          id: (Date.now() + 1).toString(),
          content: response.message,
          sender: 'ai',
          timestamp: new Date(),
        };
        
        // Update global search state with the products from the response
        if (response.products && response.products.length > 0) {
          setSearchResults(response.products);
          setCurrentSearchQuery(query);
          setHasSearched(true);
        }
      }

      addMessage(aiResponse);
    } catch (error) {
      // Handle API errors gracefully
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: "Sorry, I'm having trouble processing your request right now. Please try again in a moment.",
        sender: 'ai',
        timestamp: new Date(),
      };
      addMessage(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async (messageText: string) => {
    // Only allow sending messages in AI mode
    if (isLiveAgent) return;
    
    if (!messageText || !messageText.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: messageText,
      sender: 'user',
      timestamp: new Date(),
    };

    addMessage(userMessage);
    setIsLoading(true);

    // Check if we should show a personalized greeting before the response
    await showSearchGreeting(messageText);

    try {
      let aiResponse: ChatMessage;

      // Prepare chat history for all endpoints
      const chatHistory = messages.map(msg => ({
        role: msg.sender === 'user' ? 'user' : 'assistant',
        content: msg.content
      }));

      // If in comparison mode and we have at least 2 products to compare, call the backend
      if (isInComparisonMode && comparingProducts.length >= 2) {
        const response = await api.compareProducts(messageText, comparingProducts, chatHistory);
        aiResponse = {
          id: (Date.now() + 1).toString(),
          content: response,
          sender: 'ai',
          timestamp: new Date(),
          comparisonProducts: comparingProducts,
          comparisonProductCount: comparingProducts.length,
        };
      } else if (currentContext.type === 'product' && currentContext.product) {
        // If in product context, call the backend for product-specific questions
        const response = await api.askAboutProduct(messageText, currentContext.product, chatHistory);
        aiResponse = {
          id: (Date.now() + 1).toString(),
          content: response,
          sender: 'ai',
          timestamp: new Date(),
          productTitle: `${currentContext.product.brand} ${currentContext.product.title}`,
        };
      } else if (currentContext.type === 'comparison' && currentContext.products) {
        // If in comparison context, call the backend for product comparison
        const response = await api.compareProducts(messageText, currentContext.products, chatHistory);
        aiResponse = {
          id: (Date.now() + 1).toString(),
          content: response,
          sender: 'ai',
          timestamp: new Date(),
          comparisonProducts: currentContext.products,
          comparisonProductCount: currentContext.products.length,
        };
      } else {
        // Use backend chatbot endpoint for general chat mode
        const response = await api.chatbot(messageText, chatHistory, user?.customer_key);
        aiResponse = {
          id: (Date.now() + 1).toString(),
          content: response.message,
          sender: 'ai',
          timestamp: new Date(),
        };
        
        // Update global search state with the products from the response
        if (response.products && response.products.length > 0) {
          setSearchResults(response.products);
          setCurrentSearchQuery(messageText);
          setHasSearched(true);
        }
      }

      addMessage(aiResponse);
    } catch (error) {
      console.error('Error in sendMessage:', error);
      // Handle API errors gracefully
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: "Sorry, I'm having trouble processing your request right now. Please try again in a moment.",
        sender: 'ai',
        timestamp: new Date(),
      };
      addMessage(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const resetProcessedQuery = () => {
    processedQueryRef.current = '';
  };

  return {
    isLoading,
    sendMessage,
    resetProcessedQuery
  };
}; 