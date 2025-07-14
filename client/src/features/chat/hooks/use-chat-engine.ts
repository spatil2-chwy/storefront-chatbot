import { useAuth } from '../../../lib/auth';
import { useGlobalChat } from '../context';
import { ChatMessage } from '../../../types';
import { useChatApi } from './use-chat-api';
import { useChatMessages } from './use-chat-messages';

interface ChatEngineProps {
  initialQuery?: string;
  shouldClearChat?: boolean;
  isLiveAgent: boolean;
  showInitialSearchGreeting: (query: string) => Promise<void>;
  showSearchGreeting: (message: string) => Promise<void>;
}

export const useChatEngine = ({
  initialQuery,
  shouldClearChat,
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

      // Prepare chat history for API calls
      const chatHistory = messages.map(msg => ({
        role: msg.sender === 'user' ? 'user' : 'assistant',
        content: msg.content
      }));

      // Route to appropriate API based on context
      if (isInComparisonMode && comparingProducts.length >= 2) {
        aiResponse = await generateComparisonResponse(query, comparingProducts, chatHistory);
      } else if (currentContext.type === 'product' && currentContext.product) {
        aiResponse = await generateProductResponse(query, currentContext.product, chatHistory);
      } else {
        aiResponse = await generateGeneralResponse(query, chatHistory, user?.customer_key);
      }

      addMessage(aiResponse);
    } catch (error) {
      const errorMessage = generateErrorResponse();
      addMessage(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async (messageText: string) => {
    if (isLiveAgent) return;
    if (!messageText || !messageText.trim()) return;

    const userMessage = createUserMessage(messageText);
    addMessage(userMessage);
    setIsLoading(true);

    await showSearchGreeting(messageText);

    try {
      let aiResponse: ChatMessage;

      // Prepare chat history for API calls
      const chatHistory = messages.map(msg => ({
        role: msg.sender === 'user' ? 'user' : 'assistant',
        content: msg.content
      }));

      // Route to appropriate API based on context
      if (isInComparisonMode && comparingProducts.length >= 2) {
        aiResponse = await generateComparisonResponse(messageText, comparingProducts, chatHistory);
      } else if (currentContext.type === 'product' && currentContext.product) {
        aiResponse = await generateProductResponse(messageText, currentContext.product, chatHistory);
      } else if (currentContext.type === 'comparison' && currentContext.products) {
        aiResponse = await generateComparisonResponse(messageText, currentContext.products, chatHistory);
      } else {
        aiResponse = await generateGeneralResponse(messageText, chatHistory, user?.customer_key);
      }

      addMessage(aiResponse);
    } catch (error) {
      console.error('Error in sendMessage:', error);
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