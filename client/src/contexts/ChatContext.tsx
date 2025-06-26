import React, { createContext, useContext, useState, ReactNode } from 'react';
import { ChatMessage, ChatContext as ChatContextType, Product } from '../types';

interface GlobalChatContextType {
  messages: ChatMessage[];
  setMessages: (messages: ChatMessage[]) => void;
  addMessage: (message: ChatMessage) => void;
  clearMessages: () => void;
  currentContext: ChatContextType;
  setCurrentContext: (context: ChatContextType) => void;
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
  // Product state management
  searchResults: Product[];
  setSearchResults: (products: Product[]) => void;
  currentSearchQuery: string;
  setCurrentSearchQuery: (query: string) => void;
  hasSearched: boolean;
  setHasSearched: (searched: boolean) => void;
}

const GlobalChatContext = createContext<GlobalChatContextType | undefined>(undefined);

export const useGlobalChat = () => {
  const context = useContext(GlobalChatContext);
  if (!context) {
    throw new Error('useGlobalChat must be used within a GlobalChatProvider');
  }
  return context;
};

interface GlobalChatProviderProps {
  children: ReactNode;
}

export const GlobalChatProvider: React.FC<GlobalChatProviderProps> = ({ children }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentContext, setCurrentContext] = useState<ChatContextType>({ type: 'general' });
  const [isOpen, setIsOpen] = useState(false); // Start with chatbot collapsed
  
  // Product state management
  const [searchResults, setSearchResults] = useState<Product[]>([]);
  const [currentSearchQuery, setCurrentSearchQuery] = useState<string>('');
  const [hasSearched, setHasSearched] = useState<boolean>(false);

  const addMessage = (message: ChatMessage) => {
    setMessages(prev => [...prev, message]);
  };

  const clearMessages = () => {
    setMessages([]);
  };

  return (
    <GlobalChatContext.Provider
      value={{
        messages,
        setMessages,
        addMessage,
        clearMessages,
        currentContext,
        setCurrentContext,
        isOpen,
        setIsOpen,
        searchResults,
        setSearchResults,
        currentSearchQuery,
        setCurrentSearchQuery,
        hasSearched,
        setHasSearched,
      }}
    >
      {children}
    </GlobalChatContext.Provider>
  );
}; 