import React, { useState, useEffect } from 'react';
import { useGlobalChat } from '../context';
import { ChatContext, Product } from '../../../types';
import { useChatEngine } from '../hooks/use-chat-engine';
import { useGreeting } from '../hooks/use-greeting';
import { useComparisonTracker } from '../hooks/use-comparison-tracker';
import { isTransitionMessage } from '../utils/chat-utilities';
import { SidebarChatLayout } from './Layout/SidebarChatLayout';

interface ChatWidgetProps {
  initialQuery?: string;
  shouldOpen?: boolean;
  shouldClearChat?: boolean;
  onClearChat?: () => void;
  chatContext?: ChatContext;
  preloadedChatResponse?: {message: string, history: any[], products: any[]};
}

export default function ChatWidget({ 
  initialQuery, 
  shouldOpen, 
  shouldClearChat, 
  onClearChat, 
  chatContext, 
  preloadedChatResponse 
}: ChatWidgetProps) {
  const { 
    messages, 
    clearMessages,
    isOpen, 
    setIsOpen,
    comparingProducts,
    isInComparisonMode,
    clearComparison,
    shouldAutoOpen,
    setShouldAutoOpen,
    isMainChatHidden
  } = useGlobalChat();
  
  const [inputValue, setInputValue] = useState('');
  const [isLiveAgent, setIsLiveAgent] = useState(false);

  // Initialize hooks
  const { 
    showSearchGreeting, 
    showInitialSearchGreeting, 
    resetGreeting 
  } = useGreeting();

  const { 
    comparisonStartIndexRef,
    handleChatContextChange,
    handleExitToGeneralChat,
    resetComparisonTracker
  } = useComparisonTracker();

  const { 
    isLoading, 
    sendMessage: engineSendMessage, 
    resetProcessedQuery 
  } = useChatEngine({
    initialQuery,
    shouldClearChat,
    preloadedChatResponse,
    isLiveAgent,
    showInitialSearchGreeting,
    showSearchGreeting
  });

  useEffect(() => {
    // Only scroll when messages change and we're not in comparison mode to prevent glitching
    if (!isInComparisonMode) {
      // Auto-scroll is now handled within ChatMessages component
    }
  }, [messages, isInComparisonMode]);

  useEffect(() => {
    if (shouldOpen || shouldAutoOpen) {
      setIsOpen(true);
      setShouldAutoOpen(false); // Reset auto-open trigger
    }
  }, [shouldOpen, shouldAutoOpen, setIsOpen, setShouldAutoOpen]);

  // Handle chat context changes from props
  useEffect(() => {
    handleChatContextChange(chatContext);
  }, [chatContext?.type, chatContext?.product?.id, handleChatContextChange]);

  // Handle switching between AI and Live Agent modes
  const handleModeSwitch = (liveAgent: boolean) => {
    setIsLiveAgent(liveAgent);
    // Clear input when switching modes
    setInputValue('');
  };

  const sendMessage = async (messageText?: string) => {
    const messageToSend = messageText || inputValue;
    if (!messageToSend || !messageToSend.trim()) return;

    await engineSendMessage(messageToSend);
    setInputValue(''); // Always clear input after sending
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  };

  const handleCloseChat = () => {
    setIsOpen(false);
    // Store that user closed the chat so we can auto-open on page transitions
    localStorage.setItem('chatClosed', 'true');
  };

  const handleClearChat = () => {
    clearMessages();
    setInputValue('');
    resetProcessedQuery();
    resetComparisonTracker();
    resetGreeting();
    onClearChat?.();
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInputValue(suggestion);
  };

  const handleClearComparison = () => {
    clearComparison();
    resetComparisonTracker();
  };

  // Hide chat when product modal is active
  if (isMainChatHidden) {
    return null;
  }

  // Use the unified sidebar layout for all chat scenarios - always sidebar, never embedded
  return (
    <SidebarChatLayout
      isOpen={isOpen}
      onToggle={() => setIsOpen(!isOpen)}
      isLiveAgent={isLiveAgent}
      onModeSwitch={handleModeSwitch}
      onClose={handleCloseChat}
      onClearChat={handleClearChat}
      messages={messages}
      isLoading={isLoading}
      inputValue={inputValue}
      onInputChange={setInputValue}
      onSend={() => sendMessage()}
      onKeyPress={handleKeyPress}
      onSuggestionClick={handleSuggestionClick}
      onClearComparison={handleClearComparison}
      chatContext={chatContext}
      isEmbedded={false}
    />
  );
}
