import React, { createContext, useContext, useState, ReactNode } from 'react';
import { ChatMessage, ChatContext as ChatContextType } from '../types';

interface GlobalChatContextType {
  messages: ChatMessage[];
  setMessages: (messages: ChatMessage[]) => void;
  addMessage: (message: ChatMessage) => void;
  clearMessages: () => void;
  currentContext: ChatContextType;
  setCurrentContext: (context: ChatContextType) => void;
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
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
  const [isOpen, setIsOpen] = useState(false);

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
      }}
    >
      {children}
    </GlobalChatContext.Provider>
  );
}; 