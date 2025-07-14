import { useState, useRef, useEffect } from 'react';
import { useGlobalChat } from '../context';
import { ChatMessage } from '../../../types';

interface ChatMessagesProps {
  initialQuery?: string;
  shouldClearChat?: boolean;
  preloadedChatResponse?: {message: string, history: any[], products: any[]};
  isLiveAgent: boolean;
}

export const useChatMessages = ({
  initialQuery,
  shouldClearChat,
  preloadedChatResponse,
  isLiveAgent
}: ChatMessagesProps) => {
  const {
    messages,
    addMessage,
    clearMessages,
    setSearchResults,
    setCurrentSearchQuery,
    setHasSearched
  } = useGlobalChat();

  const [isLoading, setIsLoading] = useState(false);
  const processedQueryRef = useRef<string>('');

  // Handle initial query processing
  useEffect(() => {
    if (initialQuery && initialQuery.trim() && initialQuery !== processedQueryRef.current && !isLiveAgent) {
      processedQueryRef.current = initialQuery;
      
      // Clear chat if this is a new search and there are existing messages
      if (shouldClearChat && messages.length > 0) {
        clearMessages();
      }
      
      // Create and add user message
      const userMessage: ChatMessage = {
        id: Date.now().toString(),
        content: preloadedChatResponse ? `Searching for: ${initialQuery}` : initialQuery,
        sender: 'user',
        timestamp: new Date(),
      };
      
      addMessage(userMessage);
      
      // Use preloaded response if available
      if (preloadedChatResponse) {
        const aiResponse: ChatMessage = {
          id: (Date.now() + 1).toString(),
          content: preloadedChatResponse.message,
          sender: 'ai',
          timestamp: new Date(),
        };
        
        addMessage(aiResponse);
        
        // Update search state with products from response
        if (preloadedChatResponse.products && preloadedChatResponse.products.length > 0) {
          setSearchResults(preloadedChatResponse.products);
          setCurrentSearchQuery(initialQuery);
          setHasSearched(true);
        }
        return;
      }
      
      setIsLoading(true);
    }
  }, [initialQuery, shouldClearChat, isLiveAgent, addMessage, clearMessages, preloadedChatResponse, messages.length, setSearchResults, setCurrentSearchQuery, setHasSearched]);

  const createUserMessage = (messageText: string): ChatMessage => {
    return {
      id: Date.now().toString(),
      content: messageText,
      sender: 'user',
      timestamp: new Date(),
    };
  };

  const resetProcessedQuery = () => {
    processedQueryRef.current = '';
  };

  return {
    isLoading,
    setIsLoading,
    createUserMessage,
    resetProcessedQuery,
    processedQueryRef,
  };
}; 