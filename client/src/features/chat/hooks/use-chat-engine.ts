import { useAuth } from '../../../lib/auth';
import { useGlobalChat } from '../context';
import { ChatMessage } from '../../../types';
import { useChatApi } from './use-chat-api';
import { useChatMessages } from './use-chat-messages';

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
    currentContext,
    isInComparisonMode,
    comparingProducts,
    setSearchResults,
    setCurrentSearchQuery,
    setHasSearched
  } = useGlobalChat();

  const {
    isLoading,
    setIsLoading,
    createUserMessage,
    resetProcessedQuery,
    processedQueryRef,
  } = useChatMessages({
    initialQuery,
    shouldClearChat,
    preloadedChatResponse,
    isLiveAgent
  });

  const {
    generateComparisonResponse,
    generateProductResponse,
    generateGeneralResponse,
    generateErrorResponse,
  } = useChatApi({
    setSearchResults,
    setCurrentSearchQuery,
    setHasSearched
  });

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
        aiResponse = await generateComparisonResponse(query, comparingProducts, chatHistory);
      } else if (currentContext.type === 'product' && currentContext.product) {
        // If in product context, call the backend for product-specific questions
        aiResponse = await generateProductResponse(query, currentContext.product, chatHistory);
      } else {
        // Use backend chatbot endpoint for general chat mode
        aiResponse = await generateGeneralResponse(query, chatHistory, user?.customer_key);
      }

      addMessage(aiResponse);
    } catch (error) {
      // Handle API errors gracefully
      const errorMessage = generateErrorResponse();
      addMessage(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async (messageText: string) => {
    // Only allow sending messages in AI mode
    if (isLiveAgent) return;
    
    if (!messageText || !messageText.trim()) return;

    const userMessage = createUserMessage(messageText);
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
        aiResponse = await generateComparisonResponse(messageText, comparingProducts, chatHistory);
      } else if (currentContext.type === 'product' && currentContext.product) {
        // If in product context, call the backend for product-specific questions
        aiResponse = await generateProductResponse(messageText, currentContext.product, chatHistory);
      } else if (currentContext.type === 'comparison' && currentContext.products) {
        // If in comparison context, call the backend for product comparison
        aiResponse = await generateComparisonResponse(messageText, currentContext.products, chatHistory);
      } else {
        // Use backend chatbot endpoint for general chat mode
        aiResponse = await generateGeneralResponse(messageText, chatHistory, user?.customer_key);
      }

      addMessage(aiResponse);
    } catch (error) {
      console.error('Error in sendMessage:', error);
      // Handle API errors gracefully
      const errorMessage = generateErrorResponse();
      addMessage(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return {
    isLoading,
    sendMessage,
    resetProcessedQuery,
  };
}; 