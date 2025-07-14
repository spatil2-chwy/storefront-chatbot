import { useState, useRef, useEffect } from 'react';
import { useGlobalChat } from '../context';
import { ChatMessage } from '../../../types';

interface ChatMessagesProps {
  initialQuery?: string;
  shouldClearChat?: boolean;
  isLiveAgent: boolean;
}

export const useChatMessages = ({
  initialQuery,
  shouldClearChat,
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
        content: `Searching for: ${initialQuery}`,
        sender: 'user',
        timestamp: new Date(),
      };
      
      addMessage(userMessage);
      setIsLoading(true);
    }
  }, [initialQuery, shouldClearChat, isLiveAgent, addMessage, clearMessages, messages.length, setSearchResults, setCurrentSearchQuery, setHasSearched]);

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