import React, { useState, useEffect, useRef } from 'react';
import { useGlobalChat } from '../context';
import { ChatContext, ChatMessage, Product } from '../../../types';
import { useGreeting } from '../hooks/use-greeting';
import { useComparisonTracker } from '../hooks/use-comparison-tracker';
import { SidebarChatLayout } from './Layout/SidebarChatLayout';
import { api } from '../../../lib/api';
import { useAuth } from '../../../lib/auth/auth';
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
    addMessage,
    updateMessage,
    clearMessages,
    isOpen, 
    setIsOpen,
    comparingProducts,
    isInComparisonMode,
    clearComparison,
    shouldAutoOpen,
    hasSearched,
    setHasSearched,
    setShouldAutoOpen,
    isMainChatHidden,
    setSearchResults,
    setCurrentSearchQuery,
    currentContext
  } = useGlobalChat();
  
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [isLiveAgent, setIsLiveAgent] = useState(false);
  const [greetingShown, setGreetingShown] = useState(false);
  const [searchGreetingShown, setSearchGreetingShown] = useState(false); // Track if greeting shown for search context
  const [preloadedGreeting, setPreloadedGreeting] = useState<string | null>(null); // Store greeting fetched on page load
  const [isStreaming, setIsStreaming] = useState(false); // Track if currently streaming
  const [streamingMessageId, setStreamingMessageId] = useState<string | null>(null); // Track which message is streaming
  const [userHasScrolled, setUserHasScrolled] = useState(false); // Track if user has manually scrolled
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null); // Ref for the messages container
  const processedQueryRef = useRef<string>(''); // Track processed queries to avoid duplicates
  const comparisonStartIndexRef = useRef<number>(-1); // Track where comparison started
  // Initialize hooks
  const { 
    showSearchGreeting, 
    showInitialSearchGreeting, 
    resetGreeting 
  } = useGreeting();
  const { 
    handleChatContextChange,
    handleExitToGeneralChat,
    resetComparisonTracker
  } = useComparisonTracker();
  const scrollToBottom = () => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
    }
  };
  useEffect(() => {
    if (shouldOpen || shouldAutoOpen) {
      setIsOpen(true);
      setShouldAutoOpen(false); // Reset auto-open trigger
    }
  }, [shouldOpen, shouldAutoOpen, setIsOpen, setShouldAutoOpen]);
  useEffect(() => {
    if (initialQuery && processedQueryRef.current !== initialQuery) {
      processedQueryRef.current = initialQuery;
      if (shouldClearChat) {
        clearMessages();
      }
      if (isLiveAgent) return;
      const userMessage: ChatMessage = {
        id: Date.now().toString(),
        content: initialQuery,
        sender: 'user',
        timestamp: new Date(),
      };
      addMessage(userMessage);
      setIsLoading(true);
      const generateResponse = async () => {
        try {
          const chatHistory = messages.map(msg => ({
            role: msg.sender === 'user' ? 'user' : 'assistant',
            content: msg.content
          })).concat({ role: 'user', content: initialQuery });
          const responseId = (Date.now() + 1).toString();
          const streamingMessage: ChatMessage = {
            id: responseId,
            content: "",
            sender: 'ai',
            timestamp: new Date(),
          };
          addMessage(streamingMessage);
          setIsStreaming(true);
          setStreamingMessageId(responseId);
          setIsLoading(false); // Clear loading state since we're now streaming
          await api.chatbotStream(
            initialQuery,
            chatHistory,
            user?.customer_key,
            (chunk: string) => {
              updateMessage(responseId, (msg) => ({ ...msg, content: msg.content + chunk }));
            },
            (products: any[]) => {
              if (products && products.length > 0) {
                setSearchResults(products);
                setCurrentSearchQuery(initialQuery);
                setHasSearched(true);
              }
            },
            (fullMessage: string) => {
              updateMessage(responseId, (msg) => ({ ...msg, content: fullMessage }));
              setIsStreaming(false);
              setStreamingMessageId(null);
            },
            (error: string) => {
              console.error('Streaming error:', error);
              updateMessage(responseId, (msg) => ({ ...msg, content: "Sorry, I'm having trouble processing your request right now." }));
              setIsStreaming(false);
              setStreamingMessageId(null);
            }
          );
        } catch (error) {
          const errorMessage: ChatMessage = {
            id: (Date.now() + 1).toString(),
            content: 'An error occurred. Please try again.',
            sender: 'ai',
            timestamp: new Date(),
          };
          addMessage(errorMessage);
        } finally {
          setIsLoading(false);
          setIsStreaming(false);
          setStreamingMessageId(null);
        }
      };
      generateResponse();
    }
  }, [initialQuery, shouldClearChat, isLiveAgent, addMessage, clearMessages, messages, user, preloadedChatResponse, updateMessage, setSearchResults, setCurrentSearchQuery, setHasSearched]);
  // Check if user is near the bottom of the messages container
  const isNearBottom = () => {
    if (!messagesContainerRef.current) return true;
    const container = messagesContainerRef.current;
    const threshold = 100; // pixels from bottom
    return container.scrollHeight - container.scrollTop - container.clientHeight < threshold;
  };
  // Handle scroll events to detect user scrolling
  const handleScroll = () => {
    if (isStreaming) {
      setUserHasScrolled(!isNearBottom());
    }
  };
  // Only auto-scroll on new messages (not streaming chunk updates)
  const prevMessagesLength = useRef(messages.length);
  useEffect(() => {
    // Only scroll when messages change and we're not in comparison mode to prevent glitching
    // Only scroll if:
    // - Not streaming, or
    // - Streaming just started (new message), or
    // - Streaming just ended
    // - User is at the bottom
    if (!isInComparisonMode) {
      const isNewMessage = messages.length > prevMessagesLength.current;
      prevMessagesLength.current = messages.length;
      if (!isStreaming) {
        // If not streaming, always scroll to bottom on new message
        scrollToBottom();
      } else if (isNewMessage && !userHasScrolled) {
        // If streaming just started (new message), scroll to bottom
        scrollToBottom();
      }
      // Otherwise, do not auto-scroll during streaming chunk updates
    }
  }, [messages, isInComparisonMode, isStreaming, userHasScrolled]);
  // Reset user scroll state when streaming starts or ends
  useEffect(() => {
    if (isStreaming) {
      setUserHasScrolled(false);
    }
  }, [isStreaming]);
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
    if (!messageToSend.trim() || isLiveAgent) return;
    setInputValue('');
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: messageToSend,
      sender: 'user',
      timestamp: new Date(),
    };
    addMessage(userMessage);
    setIsLoading(true);
    try {
      const chatHistory = messages.map(msg => ({
        role: msg.sender === 'user' ? 'user' : 'assistant',
        content: msg.content
      })).concat({ role: 'user', content: messageToSend });
      const responseId = (Date.now() + 1).toString();
      const streamingMessage: ChatMessage = {
        id: responseId,
        content: "",
        sender: 'ai',
        timestamp: new Date(),
      };
      addMessage(streamingMessage);
      setIsStreaming(true);
      setStreamingMessageId(responseId);
      setIsLoading(false); // Clear loading state since we're now streaming
      // Route to the correct endpoint based on context
      if (isInComparisonMode && comparingProducts.length >= 2) {
        // Use compare endpoint for comparison mode
        const response = await api.compareProducts(messageToSend, comparingProducts, chatHistory);
        updateMessage(responseId, (msg) => ({ 
          ...msg, 
          content: response,
          comparisonProducts: comparingProducts,
          comparisonProductCount: comparingProducts.length,
        }));
        setIsStreaming(false);
        setStreamingMessageId(null);
      } else if (currentContext.type === 'product' && currentContext.product) {
        // Use ask about product endpoint for product context
        const response = await api.askAboutProduct(messageToSend, currentContext.product, chatHistory);
        updateMessage(responseId, (msg) => ({ 
          ...msg, 
          content: response,
          productTitle: `${currentContext.product?.brand || ''} ${currentContext.product?.title || ''}`,
        }));
        setIsStreaming(false);
        setStreamingMessageId(null);
      } else if (currentContext.type === 'comparison' && currentContext.products) {
        // Use compare endpoint for comparison context
        const response = await api.compareProducts(messageToSend, currentContext.products, chatHistory);
        updateMessage(responseId, (msg) => ({ 
          ...msg, 
          content: response,
          comparisonProducts: currentContext.products || [],
          comparisonProductCount: currentContext.products?.length || 0,
        }));
        setIsStreaming(false);
        setStreamingMessageId(null);
      } else {
        // Use streaming chatbot endpoint for general chat mode
        await api.chatbotStream(
          messageToSend,
          chatHistory,
          user?.customer_key,
          (chunk: string) => {
            updateMessage(responseId, (msg) => ({ ...msg, content: msg.content + chunk }));
          },
          (products: any[]) => {
            if (products && products.length > 0) {
              setSearchResults(products);
              setCurrentSearchQuery(messageToSend);
              setHasSearched(true);
            }
          },
          (fullMessage: string) => {
            updateMessage(responseId, (msg) => ({ ...msg, content: fullMessage }));
            setIsStreaming(false);
            setStreamingMessageId(null);
          },
          (error: string) => {
            console.error('Streaming error:', error);
            updateMessage(responseId, (msg) => ({ ...msg, content: "Sorry, I'm having trouble processing your request right now." }));
            setIsStreaming(false);
            setStreamingMessageId(null);
          }
        );
      }
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: 'An error occurred. Please try again.',
        sender: 'ai',
        timestamp: new Date(),
      };
      addMessage(errorMessage);
    } finally {
      setIsLoading(false);
      setIsStreaming(false);
      setStreamingMessageId(null);
    }
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
  const resetProcessedQuery = () => {
    processedQueryRef.current = '';
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
    sendMessage(suggestion);
  };
  const handleClearComparison = () => {
    clearComparison();
    resetComparisonTracker();
  };

  const handleExitProductChat = () => {
    handleExitToGeneralChat();
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
      onExitProductChat={handleExitProductChat}
      chatContext={chatContext}
      activeChatContext={currentContext}
      isEmbedded={false}
      isStreaming={isStreaming}
      streamingMessageId={streamingMessageId}
      userHasScrolled={userHasScrolled}
      onScroll={handleScroll}
      scrollContainerRef={messagesContainerRef}
    />
  );
}
