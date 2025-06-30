import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, Package, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ChatMessage, ChatContext, Product } from '../types';
import { useGlobalChat } from '../contexts/ChatContext';
import { useIsMobile } from '@/hooks/use-mobile';
import { api } from '@/lib/api';

interface ChatWidgetProps {
  initialQuery?: string;
  shouldOpen?: boolean;
  shouldClearChat?: boolean;
  onClearChat?: () => void;
  chatContext?: ChatContext;
}

export default function ChatWidget({ initialQuery, shouldOpen, shouldClearChat, onClearChat, chatContext }: ChatWidgetProps) {
  const { 
    messages, 
    setMessages, 
    addMessage, 
    insertMessageAt,
    clearMessages, 
    currentContext, 
    setCurrentContext, 
    isOpen, 
    setIsOpen,
    comparingProducts,
    isInComparisonMode,
    clearComparison,
    shouldAutoOpen,
    setShouldAutoOpen,
    searchResults,
    setSearchResults,
    setCurrentSearchQuery,
    setHasSearched,
    isMainChatHidden
  } = useGlobalChat();
  
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLiveAgent, setIsLiveAgent] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const processedQueryRef = useRef<string>(''); // Track processed queries to avoid duplicates
  const comparisonStartIndexRef = useRef<number>(-1); // Track where comparison started
  const isMobile = useIsMobile();

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  };

  useEffect(() => {
    // Only scroll when messages change and we're not in comparison mode to prevent glitching
    if (!isInComparisonMode) {
      scrollToBottom();
    }
  }, [messages, isInComparisonMode]);

  useEffect(() => {
    if (shouldOpen || shouldAutoOpen) {
      setIsOpen(true);
      setShouldAutoOpen(false); // Reset auto-open trigger
    }
  }, [shouldOpen, shouldAutoOpen, setIsOpen, setShouldAutoOpen]);

    // Product chat is now handled by the ProductChatModal component

  // Handle chat context changes
  useEffect(() => {
    if (chatContext) {
      const previousContext = currentContext;
      setCurrentContext(chatContext);
      
      // Only auto-open chatbot if there's an explicit shouldOpen trigger
      // Don't auto-open on context changes alone
      
      // Product context set - no message needed, will be handled by modal
      
      // If switching to comparison context, add a comparison message (don't duplicate what useEffect handles)
      if (chatContext.type === 'comparison' && chatContext.products && chatContext.products.length >= 2) {
        // Set the ref to indicate we're in comparison mode, but let the useEffect handle the message
        comparisonStartIndexRef.current = 1;
      }
      
      // Removed transition message - no longer showing "Transitioned to general chat"
    }
  }, [chatContext?.type, chatContext?.product?.id, currentContext.type]);

  // Handle global context changes (for when context is set from ProductCard)
  useEffect(() => {
    // Only handle context changes if we're not already processing a chatContext prop change
    if (!chatContext && currentContext.type === 'product' && currentContext.product) {
      // Reset comparison start index when transitioning to product mode
      // This prevents the "Transitioned to general chat" message from appearing
      comparisonStartIndexRef.current = -1;
      
      // Product context handled by modal - no automatic message needed
    }
  }, [currentContext.type, currentContext.product?.id, chatContext, messages, addMessage]);

  // Handle comparison mode changes - simplified to avoid infinite loops
  useEffect(() => {
    // Only add comparison message when first entering comparison mode (2+ products)
    if (isInComparisonMode && comparingProducts.length >= 2 && comparisonStartIndexRef.current === -1) {
      // Check if we already have a comparison message to avoid duplicates
      const hasComparisonMessage = messages.some(msg => msg.content.includes('Now comparing:'));
      if (!hasComparisonMessage && comparingProducts.length >= 2) { // Double-check we have 2+ products
        comparisonStartIndexRef.current = 1; // Mark that we've added the comparison message
        
        const comparisonMessage: ChatMessage = {
          id: Date.now().toString(),
          content: `Now comparing: ${comparingProducts.length} products`,
          sender: 'ai',
          timestamp: new Date(),
          comparisonProductIds: comparingProducts.map(p => p.id).filter((id): id is number => id !== undefined),
          comparisonProductCount: comparingProducts.length,
          comparisonProducts: [...comparingProducts],
        };
        addMessage(comparisonMessage);
      } else {
        comparisonStartIndexRef.current = 1; // Mark as handled even if message exists
      }
    }
    // When exiting comparison mode (no products left) - only if we were actually in comparison mode
    else if (!isInComparisonMode && comparingProducts.length === 0 && comparisonStartIndexRef.current !== -1) {
      // Reset the comparison start index
      comparisonStartIndexRef.current = -1;
      
      // Removed transition message - no longer showing "Transitioned to general chat"
    }
  }, [isInComparisonMode, comparingProducts.length, messages, currentContext.type]);

  // Handle switching between AI and Live Agent modes
  const handleModeSwitch = (liveAgent: boolean) => {
    setIsLiveAgent(liveAgent);
    // Clear input when switching modes
    setInputValue('');
  };

  const handleExitToGeneralChat = () => {
    clearComparison();
    comparisonStartIndexRef.current = -1; // Reset comparison start index
    setCurrentContext({ type: 'general' });
    // Removed transition message - no longer showing "Transitioned to general chat"
  };

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
        content: initialQuery,
        sender: 'user',
        timestamp: new Date(),
      };
      
      addMessage(userMessage);
      
      setIsLoading(true);
      
      // Generate AI response
      const generateResponse = async () => {
        try {
          let aiResponse: ChatMessage;

                // If in comparison mode and we have at least 2 products to compare, call the backend
      if (isInComparisonMode && comparingProducts.length >= 2) {
        const response = await api.compareProducts(initialQuery, comparingProducts);
        aiResponse = {
          id: (Date.now() + 1).toString(),
          content: response,
          sender: 'ai',
          timestamp: new Date(),
        };
                } else if (currentContext.type === 'product' && currentContext.product) {
        // If in product context, call the backend for product-specific questions
        const response = await api.askAboutProduct(initialQuery, currentContext.product);
        aiResponse = {
          id: (Date.now() + 1).toString(),
          content: response,
          sender: 'ai',
          timestamp: new Date(),
        };
      } else if (currentContext.type === 'comparison' && currentContext.products) {
        // If in comparison context, call the backend for product comparison
        const response = await api.compareProducts(initialQuery, currentContext.products);
        aiResponse = {
          id: (Date.now() + 1).toString(),
          content: response,
          sender: 'ai',
          timestamp: new Date(),
        };
      } else {
            // Use backend SearchProducts for general chat mode to update products and display
            const response = await api.searchProducts(initialQuery);
            aiResponse = {
              id: (Date.now() + 1).toString(),
              content: response.reply,
              sender: 'ai',
              timestamp: new Date(),
            };
            
            // Update global search state with the products from the response
            if (response.products && response.products.length > 0) {
              setSearchResults(response.products);
              setCurrentSearchQuery(initialQuery);
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

      generateResponse();
    }
  }, [initialQuery, shouldClearChat, isLiveAgent, addMessage, clearMessages, currentContext, setSearchResults, setCurrentSearchQuery, setHasSearched]);

  const sendMessage = async (messageText?: string) => {
    // Only allow sending messages in AI mode
    if (isLiveAgent) return;
    
    const messageToSend = messageText || inputValue;
    if (!messageToSend || !messageToSend.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: messageToSend,
      sender: 'user',
      timestamp: new Date(),
    };

    addMessage(userMessage);
    setInputValue(''); // Always clear input after sending
    setIsLoading(true);

    try {
      let aiResponse: ChatMessage;

      // If in comparison mode and we have at least 2 products to compare, call the backend
      if (isInComparisonMode && comparingProducts.length >= 2) {
        const response = await api.compareProducts(messageToSend, comparingProducts);
        aiResponse = {
          id: (Date.now() + 1).toString(),
          content: response,
          sender: 'ai',
          timestamp: new Date(),
        };
      } else if (currentContext.type === 'product' && currentContext.product) {
        // If in product context, call the backend for product-specific questions
        const response = await api.askAboutProduct(messageToSend, currentContext.product);
        aiResponse = {
          id: (Date.now() + 1).toString(),
          content: response,
          sender: 'ai',
          timestamp: new Date(),
        };
      } else if (currentContext.type === 'comparison' && currentContext.products) {
        // If in comparison context, call the backend for product comparison
        const response = await api.compareProducts(messageToSend, currentContext.products);
        aiResponse = {
          id: (Date.now() + 1).toString(),
          content: response,
          sender: 'ai',
          timestamp: new Date(),
        };
      } else {
        // Use backend SearchProducts for general chat mode to update products and display
        const response = await api.searchProducts(messageToSend);
        aiResponse = {
          id: (Date.now() + 1).toString(),
          content: response.reply,
          sender: 'ai',
          timestamp: new Date(),
        };
        
        // Update global search state with the products from the response
        if (response.products && response.products.length > 0) {
          setSearchResults(response.products);
          setCurrentSearchQuery(messageToSend);
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

  // Hide chat when product modal is active
  if (isMainChatHidden) {
    return null;
  }

  // If chatContext is provided (for embedded chat like comparison page), render inline
  if (chatContext) {
    return (
      <div className="h-full flex flex-col bg-white">
        {/* Header */}
        <div className="bg-white border-b border-gray-100 p-4 flex-shrink-0">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-chewy-blue rounded-full flex items-center justify-center">
                <img 
                  src="/chewy-c-white.png" 
                  alt="Chewy C" 
                  className="w-5 h-5"
                />
              </div>
              <div className="text-gray-900 font-work-sans text-base font-semibold">
                AI Beta - Product Comparison
              </div>
            </div>
            
            {/* Clear Chat Button */}
            {messages.length > 0 && (
              <button
                onClick={() => {
                  clearMessages();
                  setInputValue('');
                  processedQueryRef.current = '';
                  comparisonStartIndexRef.current = -1;
                  onClearChat?.();
                }}
                className="text-xs text-gray-500 hover:text-gray-700 font-work-sans underline"
              >
                Clear chat
              </button>
            )}
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 p-4 overflow-y-auto bg-gray-50">
          {/* Initial suggestions if no messages */}
          {messages.length === 0 && (
            <div className="space-y-2">
              <p className="text-sm text-gray-600 font-work-sans mb-4">Compare these products or ask questions:</p>
              <div className="space-y-2">
                <button
                  onClick={() => setInputValue("What are the main differences between these products?")}
                  className="block w-full text-left text-sm text-gray-700 hover:text-chewy-blue hover:bg-blue-50 p-3 rounded-lg border border-gray-200 font-work-sans"
                >
                  "What are the main differences between these products?"
                </button>
                <button
                  onClick={() => setInputValue("Which product is best for my large breed dog?")}
                  className="block w-full text-left text-sm text-gray-700 hover:text-chewy-blue hover:bg-blue-50 p-3 rounded-lg border border-gray-200 font-work-sans"
                >
                  "Which product is best for my large breed dog?"
                </button>
                <button
                  onClick={() => setInputValue("Compare the nutritional value of these products")}
                  className="block w-full text-left text-sm text-gray-700 hover:text-chewy-blue hover:bg-blue-50 p-3 rounded-lg border border-gray-200 font-work-sans"
                >
                  "Compare the nutritional value of these products"
                </button>
              </div>
            </div>
          )}
          
          {messages
            .filter(message => {
              // Filter out comparison messages when there are 0 products
              if (message.content.includes('Now comparing:') && comparingProducts.length === 0) {
                return false;
              }
              return true;
            })
            .map((message) => (
            <div
              key={message.id}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'} mb-4`}
            >
              <div
                className={`max-w-lg px-4 py-3 text-sm ${
                  message.sender === 'user'
                    ? 'bg-chewy-blue text-white rounded-2xl'
                    : message.content.includes('Now comparing:')
                    ? 'bg-chewy-light-blue border border-chewy-blue text-chewy-blue rounded-2xl'
                    : 'bg-white text-gray-900 border border-gray-200 rounded-2xl'
                }`}
              >
                {message.content.includes('Now comparing:') ? (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="font-semibold">Now comparing: {comparingProducts.length} product{comparingProducts.length !== 1 ? 's' : ''}</div>
                      <button
                        onClick={() => {
                          clearComparison();
                          comparisonStartIndexRef.current = -1;
                        }}
                        className="text-chewy-blue hover:text-blue-700 text-sm ml-2"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </div>
                    {comparingProducts.length > 0 && (
                      <div className="mt-3 space-y-2">
                        {comparingProducts.map((product) => (
                          <div key={product.id} className="flex items-center space-x-2">
                            <div className="w-8 h-8 bg-white rounded border border-gray-200 flex items-center justify-center flex-shrink-0">
                              {product.image ? (
                                <img 
                                  src={product.image} 
                                  alt={product.title}
                                  className="w-6 h-6 object-cover rounded"
                                />
                              ) : (
                                <Package className="w-4 h-4 text-gray-400" />
                              )}
                            </div>
                            <div className="text-sm font-semibold text-chewy-blue">
                              {product.title}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ) : (
                  message.content
                )}
              </div>
            </div>
          ))}
          
          {/* Loading indicator */}
          {isLoading && (
            <div className="flex justify-start mb-4">
              <div className="bg-white px-4 py-3 rounded-2xl border border-gray-200">
                <div className="flex items-center space-x-2">
                  <div className="flex space-x-1">
                    <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-pulse"></div>
                    <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-pulse delay-150"></div>
                    <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-pulse delay-300"></div>
                  </div>
                  <span className="text-xs text-gray-500 font-work-sans">LOADING...</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input */}
        <div className="border-t border-gray-100 p-4 bg-white flex-shrink-0">
          <div className="flex space-x-2">
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about these products..."
              className="flex-1 rounded-full border-gray-200 font-work-sans py-2 px-4 text-sm focus:border-chewy-blue focus:ring-chewy-blue"
            />
            <Button 
              onClick={() => sendMessage()} 
              size="icon" 
              disabled={!inputValue.trim() || isLoading}
              className="bg-chewy-blue hover:bg-blue-700 rounded-full w-10 h-10 flex items-center justify-center disabled:bg-gray-300"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // Desktop: floating window, Mobile: bottom drawer/modal
  if (isMobile) {
    return (
      <>
        {/* Chat Button (always visible, floating, bottom right) */}
        <Button
          onClick={() => setIsOpen(!isOpen)}
          className="fixed bottom-6 right-6 w-14 h-14 bg-chewy-blue hover:bg-blue-700 text-white rounded-full shadow-lg flex items-center justify-center z-50"
          size="icon"
        >
          <MessageCircle className="w-6 h-6" />
        </Button>
        
        {/* Chat Modal - 1/3 screen overlay */}
        {isOpen && (
          <div className="fixed left-0 bottom-0 w-full h-1/3 z-50 bg-white shadow-2xl border-t border-gray-200 rounded-t-3xl flex flex-col" style={{minHeight: 320, maxHeight: 500}}>
            {/* Chat Content */}
            <div className="flex flex-col h-full">
              <CardHeader className="bg-white border-b border-gray-100 p-3 rounded-t-3xl flex-shrink-0">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 bg-chewy-blue rounded-full flex items-center justify-center">
                      <img 
                        src="/chewy-c-white.png" 
                        alt="Chewy C" 
                        className="w-5 h-5"
                      />
                    </div>
                    <CardTitle className="text-gray-900 font-work-sans text-base">
                      {isLiveAgent ? 'Live Agent' : 'AI Beta'}
                    </CardTitle>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={handleCloseChat}
                    className="text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-full w-7 h-7"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
                {/* Toggle between AI and Live Agent */}
                <div className="flex items-center justify-between mt-2">
                  <div className="flex bg-gray-100 rounded-full p-0.5">
                    <button
                      onClick={() => handleModeSwitch(false)}
                      className={`px-3 py-1.5 rounded-full text-xs font-work-sans transition-colors ${
                        !isLiveAgent 
                          ? 'bg-chewy-blue text-white' 
                          : 'text-gray-600 hover:text-gray-800'
                      }`}
                    >
                      AI Chat
                    </button>
                    <button
                      onClick={() => handleModeSwitch(true)}
                      className={`px-3 py-1.5 rounded-full text-xs font-work-sans transition-colors ${
                        isLiveAgent 
                          ? 'bg-chewy-blue text-white' 
                          : 'text-gray-600 hover:text-gray-800'
                      }`}
                    >
                      Live Agent
                    </button>
                  </div>
                  {/* Clear Chat Button - Only show in AI mode */}
                  {!isLiveAgent && messages.length > 0 && (
                    <div className="flex flex-col items-end space-y-1">
                      <button
                        onClick={() => {
                          clearMessages();
                          setInputValue('');
                          processedQueryRef.current = '';
                          comparisonStartIndexRef.current = -1; // Reset comparison start index
                          onClearChat?.();
                        }}
                        className="text-xs text-gray-500 hover:text-gray-700 font-work-sans underline"
                      >
                        Clear chat
                      </button>
                      {/* Show exit button for product discussion mode when not on product detail page */}
                      {currentContext.type === 'product' && !chatContext && (
                        <button
                          onClick={handleExitToGeneralChat}
                          className="text-xs text-chewy-blue hover:text-blue-700 font-work-sans underline flex items-center space-x-1"
                        >
                          <ArrowLeft className="w-3 h-3" />
                          Exit to general chat
                        </button>
                      )}
                      {/* Show exit button for comparison mode */}
                      {currentContext.type === 'comparison' && (
                        <button
                          onClick={handleExitToGeneralChat}
                          className="text-xs text-chewy-blue hover:text-blue-700 font-work-sans underline flex items-center space-x-1"
                        >
                          <ArrowLeft className="w-3 h-3" />
                          Exit to general chat
                        </button>
                      )}
                    </div>
                  )}
                </div>
              </CardHeader>
              <div className="flex-1 flex flex-col overflow-hidden">
                {/* AI Chat Mode */}
                {!isLiveAgent && (
                  <>
                    {/* Messages - Scrollable area */}
                    <div className="flex-1 p-4 overflow-y-auto space-y-3 bg-white">
                      {/* Initial suggestions if no messages */}
                      {messages.length === 0 && (
                        <div className="space-y-2">
                          <p className="text-xs text-gray-600 font-work-sans">Try asking:</p>
                          <div className="space-y-1.5">
                            <button
                              onClick={() => setInputValue("Easiest way to deal with backyard dog poop?")}
                              className="block w-full text-left text-xs text-gray-700 hover:text-chewy-blue hover:bg-gray-50 p-2 rounded-lg border border-gray-200 font-work-sans"
                            >
                              "Easiest way to deal with backyard dog poop?"
                            </button>
                            <button
                              onClick={() => setInputValue("Dog developed chicken allergy. Need protein though.")}
                              className="block w-full text-left text-xs text-gray-700 hover:text-chewy-blue hover:bg-gray-50 p-2 rounded-lg border border-gray-200 font-work-sans"
                            >
                              "Dog developed chicken allergy. Need protein though."
                            </button>
                          </div>
                        </div>
                      )}
                      
                      {messages
                        .filter(message => {
                          // Filter out comparison messages when there are 0 products
                          if (message.content.includes('Now comparing:') && comparingProducts.length === 0) {
                            return false;
                          }
                          return true;
                        })
                        .map((message) => (
                        <div
                          key={message.id}
                          className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                          <div
                            className={`max-w-xs px-3 py-2 rounded-2xl font-work-sans text-sm ${
                              message.sender === 'user'
                                ? 'bg-chewy-blue text-white'
                                : message.content.includes('Now comparing:')
                                ? 'bg-chewy-light-blue border border-chewy-blue text-chewy-blue'
                                : 'bg-gray-100 text-gray-900'
                            }`}
                          >
                            {message.content.includes('Now comparing:') ? (
                              <div className="space-y-2">
                                <div className="flex items-center justify-between">
                                  <div className="font-semibold">Now comparing: {comparingProducts.length} product{comparingProducts.length !== 1 ? 's' : ''}</div>
                                  <button
                                    onClick={() => {
                                      clearComparison();
                                      comparisonStartIndexRef.current = -1;
                                      // Exit comparison without transition message
                                    }}
                                    className="text-chewy-blue hover:text-blue-700 text-sm ml-2"
                                  >
                                    <X className="w-3 h-3" />
                                  </button>
                                </div>
                                {comparingProducts.length > 0 && (
                                  <div className="mt-3 space-y-2">
                                    {comparingProducts.map((product) => (
                                      <div key={product.id} className="flex items-center space-x-2">
                                        <div className="w-8 h-8 bg-white rounded border border-gray-200 flex items-center justify-center flex-shrink-0">
                                          {product.image ? (
                                            <img 
                                              src={product.image} 
                                              alt={product.title}
                                              className="w-6 h-6 object-cover rounded"
                                            />
                                          ) : (
                                            <Package className="w-4 h-4 text-gray-400" />
                                          )}
                                        </div>
                                        <div className="text-sm font-semibold text-chewy-blue">
                                          {product.title}
                                        </div>
                                      </div>
                                    ))}
                                  </div>
                                )}
                              </div>
                            ) : (
                              message.content
                            )}
                          </div>
                        </div>
                      ))}
                      
                      {/* Loading indicator */}
                      {isLoading && (
                        <div className="flex justify-start">
                          <div className="bg-gray-100 px-3 py-2 rounded-2xl">
                            <div className="flex items-center space-x-2">
                              <div className="flex space-x-1">
                                <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-pulse"></div>
                                <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-pulse delay-150"></div>
                                <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-pulse delay-300"></div>
                              </div>
                              <span className="text-xs text-gray-500 font-work-sans">LOADING...</span>
                            </div>
                          </div>
                        </div>
                      )}
                      <div ref={messagesEndRef} />
                    </div>
                    {/* Input - Fixed at bottom */}
                    <div className="border-t border-gray-100 p-3 bg-white rounded-b-3xl flex-shrink-0">
                      <div className="flex space-x-2">
                        <Input
                          value={inputValue}
                          onChange={(e) => setInputValue(e.target.value)}
                          onKeyPress={handleKeyPress}
                          placeholder="What do you want to learn?"
                          className="flex-1 rounded-full border-gray-200 font-work-sans py-2 px-3 text-sm focus:border-chewy-blue focus:ring-chewy-blue"
                        />
                        <Button 
                          onClick={() => sendMessage()} 
                          size="icon" 
                          className="bg-chewy-blue hover:bg-blue-700 rounded-full w-9 h-9 flex items-center justify-center"
                        >
                          <Send className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </>
                )}
                {/* Live Agent Mode */}
                {isLiveAgent && (
                  <div className="flex-1 p-6 bg-white overflow-y-auto">
                    <div className="text-center space-y-6">
                      {/* Header */}
                      <div className="space-y-2">
                        <h3 className="text-lg font-semibold text-gray-900 font-work-sans">
                          Connect with a Human Agent
                        </h3>
                      </div>
                      {/* Contact Options */}
                      <div className="space-y-4">
                        <div className="bg-gray-50 p-4 rounded-xl">
                          <div className="flex items-center space-x-3">
                            <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
                              <span className="text-white text-lg">📞</span>
                            </div>
                            <div className="flex-1 text-left">
                              <h4 className="font-semibold text-gray-900 text-sm">Call Us</h4>
                              <p className="text-gray-600 text-sm">Speak with an agent</p>
                              <p className="text-chewy-blue font-semibold text-sm">1-800-672-4399</p>
                            </div>
                          </div>
                        </div>
                        <div className="bg-gray-50 p-4 rounded-xl">
                          <div className="flex items-center space-x-3">
                            <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
                              <span className="text-white text-lg">💬</span>
                            </div>
                            <div className="flex-1 text-left">
                              <h4 className="font-semibold text-gray-900 text-sm">Live Chat</h4>
                              <p className="text-gray-600 text-sm">Chat with an agent</p>
                            </div>
                          </div>
                        </div>
                        <div className="bg-gray-50 p-4 rounded-xl">
                          <div className="flex items-center space-x-3">
                            <div className="w-10 h-10 bg-purple-500 rounded-full flex items-center justify-center">
                              <span className="text-white text-lg">📧</span>
                            </div>
                            <div className="flex-1 text-left">
                              <h4 className="font-semibold text-gray-900 text-sm">Email Us</h4>
                              <p className="text-gray-600 text-sm">Send us a message</p>
                              <p className="text-chewy-blue font-semibold text-sm">help@chewy.com</p>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </>
    );
  }
  // Desktop version (unchanged)
  return (
    <div className="fixed bottom-6 right-6 z-50">
      {/* Chat Button */}
      <Button
        onClick={() => setIsOpen(!isOpen)}
        className="w-14 h-14 bg-chewy-blue hover:bg-blue-700 text-white rounded-full shadow-lg flex items-center justify-center"
        size="icon"
      >
        <MessageCircle className="w-6 h-6" />
      </Button>

      {/* Chat Modal */}
      {isOpen && (
        <Card className="absolute bottom-16 right-0 w-80 h-[450px] shadow-2xl rounded-3xl border-0">
          <CardHeader className="bg-white border-b border-gray-100 p-3 rounded-t-3xl">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-chewy-blue rounded-full flex items-center justify-center">
                  <img 
                    src="/chewy-c-white.png" 
                    alt="Chewy C" 
                    className="w-5 h-5"
                  />
                </div>
                <CardTitle className="text-gray-900 font-work-sans text-base">
                  {isLiveAgent ? 'Live Agent' : 'AI Beta'}
                </CardTitle>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={handleCloseChat}
                className="text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-full w-7 h-7"
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
            
            {/* Toggle between AI and Live Agent */}
            <div className="flex items-center justify-between mt-2">
              <div className="flex bg-gray-100 rounded-full p-0.5">
                <button
                  onClick={() => handleModeSwitch(false)}
                  className={`px-3 py-1.5 rounded-full text-xs font-work-sans transition-colors ${
                    !isLiveAgent 
                      ? 'bg-chewy-blue text-white' 
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                >
                  AI Chat
                </button>
                <button
                  onClick={() => handleModeSwitch(true)}
                  className={`px-3 py-1.5 rounded-full text-xs font-work-sans transition-colors ${
                    isLiveAgent 
                      ? 'bg-chewy-blue text-white' 
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                >
                  Live Agent
                </button>
              </div>
              
              {/* Clear Chat Button - Only show in AI mode */}
              {!isLiveAgent && messages.length > 0 && (
                <div className="flex flex-col items-end space-y-1">
                  <button
                    onClick={() => {
                      clearMessages();
                      setInputValue('');
                      processedQueryRef.current = '';
                      comparisonStartIndexRef.current = -1; // Reset comparison start index
                      onClearChat?.();
                    }}
                    className="text-xs text-gray-500 hover:text-gray-700 font-work-sans underline"
                  >
                    Clear chat
                  </button>
                  {/* Show exit button for product discussion mode when not on product detail page */}
                  {currentContext.type === 'product' && !chatContext && (
                    <button
                      onClick={handleExitToGeneralChat}
                      className="text-xs text-chewy-blue hover:text-blue-700 font-work-sans underline flex items-center space-x-1"
                    >
                      <ArrowLeft className="w-3 h-3" />
                      Exit to general chat
                    </button>
                  )}
                  {/* Show exit button for comparison mode */}
                  {currentContext.type === 'comparison' && (
                    <button
                      onClick={handleExitToGeneralChat}
                      className="text-xs text-chewy-blue hover:text-blue-700 font-work-sans underline flex items-center space-x-1"
                    >
                      <ArrowLeft className="w-3 h-3" />
                      Exit to general chat
                    </button>
                  )}
                </div>
              )}
            </div>
          </CardHeader>

          <CardContent className="flex flex-col h-80 p-0 bg-gray-50">
            {/* AI Chat Mode */}
            {!isLiveAgent && (
              <>
                {/* Messages */}
                <div className="flex-1 p-4 overflow-y-auto space-y-3 bg-white">
                  {/* Initial suggestions if no messages */}
                  {messages.length === 0 && (
                    <div className="space-y-2">
                      <p className="text-xs text-gray-600 font-work-sans">Try asking:</p>
                      <div className="space-y-1.5">
                        <button
                          onClick={() => setInputValue("Easiest way to deal with backyard dog poop?")}
                          className="block w-full text-left text-xs text-gray-700 hover:text-chewy-blue hover:bg-gray-50 p-2 rounded-lg border border-gray-200 font-work-sans"
                        >
                          "Easiest way to deal with backyard dog poop?"
                        </button>
                        <button
                          onClick={() => setInputValue("Dog developed chicken allergy. Need protein though.")}
                          className="block w-full text-left text-xs text-gray-700 hover:text-chewy-blue hover:bg-gray-50 p-2 rounded-lg border border-gray-200 font-work-sans"
                        >
                          "Dog developed chicken allergy. Need protein though."
                        </button>
                      </div>
                    </div>
                  )}
                  
                  {messages
                    .filter(message => {
                      // Filter out comparison messages when there are 0 products
                      if (message.content.includes('Now comparing:') && comparingProducts.length === 0) {
                        return false;
                      }
                      return true;
                    })
                    .map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-xs px-6 py-2 rounded-2xl font-work-sans text-sm ${
                          message.sender === 'user'
                            ? 'bg-chewy-blue text-white'
                            : message.content.includes('Now comparing:')
                            ? 'bg-chewy-light-blue border border-chewy-blue text-chewy-blue'
                            : 'bg-gray-100 text-gray-900'
                        }`}
                      >
                        {message.content.includes('Now comparing:') ? (
                          <div className="space-y-2">
                            <div className="flex items-center justify-between">
                              <div className="font-semibold">Now comparing: {comparingProducts.length} product{comparingProducts.length !== 1 ? 's' : ''}</div>
                              <button
                                onClick={() => {
                                  clearComparison();
                                  comparisonStartIndexRef.current = -1;
                                  // Exit comparison without transition message
                                }}
                                className="text-chewy-blue hover:text-blue-700 text-sm ml-2"
                              >
                                <X className="w-3 h-3" />
                              </button>
                            </div>
                            {comparingProducts.length > 0 && (
                              <div className="mt-3 space-y-2">
                                {comparingProducts.map((product) => (
                                  <div key={product.id} className="flex items-center space-x-2">
                                    <div className="w-8 h-8 bg-white rounded border border-gray-200 flex items-center justify-center flex-shrink-0">
                                      {product.image ? (
                                        <img 
                                          src={product.image} 
                                          alt={product.title}
                                          className="w-6 h-6 object-cover rounded"
                                        />
                                      ) : (
                                        <Package className="w-4 h-4 text-gray-400" />
                                      )}
                                    </div>
                                    <div className="text-sm font-semibold text-chewy-blue">
                                      {product.title}
                                    </div>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        ) : (
                          message.content
                        )}
                      </div>
                    </div>
                  ))}
                  
                  {/* Loading indicator */}
                  {isLoading && (
                    <div className="flex justify-start">
                      <div className="bg-gray-100 px-3 py-2 rounded-2xl">
                        <div className="flex items-center space-x-2">
                          <div className="flex space-x-1">
                            <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-pulse"></div>
                            <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-pulse delay-150"></div>
                            <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-pulse delay-300"></div>
                          </div>
                          <span className="text-xs text-gray-500 font-work-sans">LOADING...</span>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  <div ref={messagesEndRef} />
                </div>

                {/* Input */}
                <div className="border-t border-gray-100 p-3 bg-white rounded-b-3xl">
                  <div className="flex space-x-2">
                    <Input
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="What do you want to learn?"
                      className="flex-1 rounded-full border-gray-200 font-work-sans py-2 px-3 text-sm focus:border-chewy-blue focus:ring-chewy-blue"
                    />
                    <Button 
                      onClick={() => sendMessage()} 
                      size="icon" 
                      className="bg-chewy-blue hover:bg-blue-700 rounded-full w-9 h-9 flex items-center justify-center"
                    >
                      <Send className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </>
            )}

            {/* Live Agent Mode */}
            {isLiveAgent && (
              <div className="flex-1 p-6 bg-white">
                <div className="text-center space-y-6">
                  {/* Header */}
                  <div className="space-y-2">
                    <h3 className="text-lg font-semibold text-gray-900 font-work-sans">
                      Connect with a Human Agent
                    </h3>
                  </div>

                  {/* Contact Options */}
                  <div className="space-y-4">
                    <div className="bg-gray-50 p-4 rounded-xl">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
                          <span className="text-white text-lg">📞</span>
                        </div>
                        <div className="flex-1 text-left">
                          <h4 className="font-semibold text-gray-900 text-sm">Call Us</h4>
                          <p className="text-gray-600 text-sm">Speak with an agent</p>
                          <p className="text-chewy-blue font-semibold text-sm">1-800-672-4399</p>
                        </div>
                      </div>
                    </div>

                    <div className="bg-gray-50 p-4 rounded-xl">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
                          <span className="text-white text-lg">💬</span>
                        </div>
                        <div className="flex-1 text-left">
                          <h4 className="font-semibold text-gray-900 text-sm">Live Chat</h4>
                          <p className="text-gray-600 text-sm">Chat with an agent</p>
                        </div>
                      </div>
                    </div>

                    <div className="bg-gray-50 p-4 rounded-xl">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-purple-500 rounded-full flex items-center justify-center">
                          <span className="text-white text-lg">📧</span>
                        </div>
                        <div className="flex-1 text-left">
                          <h4 className="font-semibold text-gray-900 text-sm">Email Us</h4>
                          <p className="text-gray-600 text-sm">Send us a message</p>
                          <p className="text-chewy-blue font-semibold text-sm">help@chewy.com</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
