import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, Package, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ChatMessage, ChatContext, Product } from '../types';
import { useGlobalChat } from '../contexts/ChatContext';
import { useIsMobile } from '@/hooks/use-mobile';
import { api } from '@/lib/api';
import { useAuth } from '@/lib/auth';

interface ChatWidgetProps {
  initialQuery?: string;
  shouldOpen?: boolean;
  shouldClearChat?: boolean;
  onClearChat?: () => void;
  chatContext?: ChatContext;
}

// Simple markdown to HTML converter for chat messages
const formatMessageContent = (content: string): string => {
  let formattedContent = content;
  
  // Convert **bold** to <strong>
  formattedContent = formattedContent.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  
  // Convert *italic* to <em>
  formattedContent = formattedContent.replace(/\*(.*?)\*/g, '<em>$1</em>');
  
  // Convert numbered lists (1. item) to proper HTML lists
  if (/^\d+\.\s/m.test(formattedContent)) {
    const lines = formattedContent.split('\n');
    let inList = false;
    const processedLines: string[] = [];
    
    lines.forEach(line => {
      const trimmedLine = line.trim();
      const numberListMatch = trimmedLine.match(/^(\d+)\.\s(.+)$/);
      
      if (numberListMatch) {
        if (!inList) {
          processedLines.push('<ol>');
          inList = true;
        }
        processedLines.push(`<li>${numberListMatch[2]}</li>`);
      } else if (trimmedLine.startsWith('- ')) {
        if (!inList) {
          processedLines.push('<ul>');
          inList = true;
        }
        processedLines.push(`<li>${trimmedLine.substring(2)}</li>`);
      } else {
        if (inList) {
          processedLines.push('</ol>');
          inList = false;
        }
        if (trimmedLine) {
          processedLines.push(`<p>${trimmedLine}</p>`);
        }
      }
    });
    
    if (inList) {
      processedLines.push('</ol>');
    }
    
    formattedContent = processedLines.join('');
  } else {
    // Just wrap paragraphs if no lists
    const paragraphs = formattedContent.split('\n\n');
    formattedContent = paragraphs
      .filter(p => p.trim())
      .map(p => `<p>${p.trim()}</p>`)
      .join('');
  }
  
  return formattedContent;
};

// Helper function to get transition message styling based on type
const getTransitionStyling = (message: ChatMessage): string => {
  // Handle new transition messages with explicit types
  if (message.isTransition) {
    switch (message.transitionType) {
      case 'product':
        return 'bg-green-50 border border-green-200 text-green-700';
      case 'comparison':
        return 'bg-purple-50 border border-purple-200 text-purple-700';
      case 'general':
        return 'bg-blue-50 border border-blue-200 text-blue-700';
      default:
        return 'bg-chewy-light-blue border border-chewy-blue text-chewy-blue';
    }
  }
  
  // Handle legacy messages based on content
  if (message.content.includes('Now comparing:')) {
    return 'bg-purple-50 border border-purple-200 text-purple-700';
  }
  if (message.content.includes('Now discussing:')) {
    return 'bg-green-50 border border-green-200 text-green-700';
  }
  if (message.content.includes('Returned to') || message.content.includes('Exited')) {
    return 'bg-blue-50 border border-blue-200 text-blue-700';
  }
  
  return '';
};

// Helper function to check if a message is a transition (new or legacy)
const isTransitionMessage = (message: ChatMessage): boolean => {
  return message.isTransition || 
         message.content.includes('Now comparing:') || 
         message.content.includes('Now discussing:') || 
         message.content.includes('Returned to') || 
         message.content.includes('Exited');
};

export default function ChatWidget({ initialQuery, shouldOpen, shouldClearChat, onClearChat, chatContext }: ChatWidgetProps) {
  const { 
    messages, 
    setMessages, 
    addMessage, 
    insertMessageAt,
    clearMessages,
    addTransitionMessage,
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
  
  const { user } = useAuth();
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

  // Handle chat context changes from props
  useEffect(() => {
    if (chatContext) {
      setCurrentContext(chatContext);
      
      // Set comparison ref for comparison mode
      if (chatContext.type === 'comparison' && chatContext.products && chatContext.products.length >= 2) {
        comparisonStartIndexRef.current = 1;
      }
    }
  }, [chatContext?.type, chatContext?.product?.id, setCurrentContext]);

  // Reset comparison start index when switching contexts
  useEffect(() => {
    if (currentContext.type !== 'comparison') {
      comparisonStartIndexRef.current = -1;
    }
  }, [currentContext.type]);

  // Handle comparison mode changes - now handled by page components with proper transitions
  useEffect(() => {
    // Set comparison start index when we're in comparison mode
    if (isInComparisonMode && comparingProducts.length >= 2 && comparisonStartIndexRef.current === -1) {
      comparisonStartIndexRef.current = 1;
    }
    // Reset when exiting comparison mode
    else if (!isInComparisonMode && comparingProducts.length === 0) {
      comparisonStartIndexRef.current = -1;
    }
  }, [isInComparisonMode, comparingProducts.length]);

  // Handle switching between AI and Live Agent modes
  const handleModeSwitch = (liveAgent: boolean) => {
    setIsLiveAgent(liveAgent);
    // Clear input when switching modes
    setInputValue('');
  };

  const handleExitToGeneralChat = () => {
    const previousContext = currentContext;
    const newContext = { type: 'general' as const };
    
    clearComparison();
    comparisonStartIndexRef.current = -1; // Reset comparison start index
    
    // Add transition message when exiting to general chat
    addTransitionMessage(previousContext, newContext);
    setCurrentContext(newContext);
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

          // If in comparison mode and we have products to compare, call the backend
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
          } else {
            // Use backend chatbot endpoint for general chat mode
            const chatHistory = messages.map(msg => ({
              role: msg.sender === 'user' ? 'user' : 'assistant',
              content: msg.content
            }));
            
            // Skip products if this is the initial query from search bar (products already loaded)
            const skipProducts = initialQuery === processedQueryRef.current;
            const response = await api.chatbot(initialQuery, chatHistory, user?.customer_key, skipProducts);
            aiResponse = {
              id: (Date.now() + 1).toString(),
              content: response.message,
              sender: 'ai',
              timestamp: new Date(),
            };
            
            // Update global search state with the products from the response only if we didn't skip them
            if (!skipProducts && response.products && response.products.length > 0) {
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
  }, [initialQuery, shouldClearChat, isLiveAgent, addMessage, clearMessages, currentContext, setSearchResults, setCurrentSearchQuery, setHasSearched, user, messages]);

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
        // Use backend chatbot endpoint for general chat mode
        const chatHistory = messages.map(msg => ({
          role: msg.sender === 'user' ? 'user' : 'assistant',
          content: msg.content
        }));
        
        const response = await api.chatbot(messageToSend, chatHistory, user?.customer_key);
        aiResponse = {
          id: (Date.now() + 1).toString(),
          content: response.message,
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
      <div className="h-full flex flex-col bg-white border border-gray-200">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 p-3 flex-shrink-0">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-6 h-6 bg-chewy-blue flex items-center justify-center">
                <img 
                  src="/chewy-c-white.png" 
                  alt="Chewy C" 
                  className="w-4 h-4"
                />
              </div>
              <div className="text-gray-900 font-work-sans text-sm font-semibold">
                {chatContext?.type === 'product' ? 'AI Beta - Product Questions' : 'AI Beta - Product Comparison'}
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
        <div className="flex-1 p-3 overflow-y-auto bg-gray-50">
          {/* Initial suggestions if no messages */}
          {messages.length === 0 && (
            <div>
              <div className="text-center text-gray-500 mb-4">
                <p className="text-sm">
                  {chatContext?.type === 'product' 
                    ? 'Ask a question about this product to get started'
                    : 'Ask a question about these products to get started'
                  }
                </p>
              </div>
              <div className="space-y-2">
                {chatContext?.type === 'product' ? (
                  // Individual product questions
                  <>
                    <button
                      onClick={() => setInputValue("What are the key ingredients in this product?")}
                      className="block w-full text-left text-sm text-chewy-blue bg-blue-50 border border-chewy-blue p-2 transition-colors hover:bg-blue-100 font-work-sans"
                    >
                      What are the key ingredients in this product?
                    </button>
                    <button
                      onClick={() => setInputValue("Is this suitable for my dog's age and size?")}
                      className="block w-full text-left text-sm text-chewy-blue bg-blue-50 border border-chewy-blue p-2 transition-colors hover:bg-blue-100 font-work-sans"
                    >
                      Is this suitable for my dog's age and size?
                    </button>
                    <button
                      onClick={() => setInputValue("What do customers love about this product?")}
                      className="block w-full text-left text-sm text-chewy-blue bg-blue-50 border border-chewy-blue p-2 transition-colors hover:bg-blue-100 font-work-sans"
                    >
                      What do customers love about this product?
                    </button>
                  </>
                ) : (
                  // Comparison questions
                  <>
                    <button
                      onClick={() => setInputValue("What are the main differences between these products?")}
                      className="block w-full text-left text-sm text-chewy-blue bg-blue-50 border border-chewy-blue p-2 transition-colors hover:bg-blue-100 font-work-sans"
                    >
                      What are the main differences between these products?
                    </button>
                    <button
                      onClick={() => setInputValue("Which product is best for my large breed dog?")}
                      className="block w-full text-left text-sm text-chewy-blue bg-blue-50 border border-chewy-blue p-2 transition-colors hover:bg-blue-100 font-work-sans"
                    >
                      Which product is best for my large breed dog?
                    </button>
                    <button
                      onClick={() => setInputValue("Compare the nutritional value of these products")}
                      className="block w-full text-left text-sm text-chewy-blue bg-blue-50 border border-chewy-blue p-2 transition-colors hover:bg-blue-100 font-work-sans"
                    >
                      Compare the nutritional value of these products
                    </button>
                  </>
                )}
              </div>
            </div>
          )}
          
          {messages
            .map((message) => (
            <div
              key={message.id}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'} mb-4`}
            >
              <div
                className={`max-w-[75%] px-3 py-2 text-sm rounded-lg ${
                  message.sender === 'user'
                    ? 'bg-chewy-blue text-white'
                    : isTransitionMessage(message)
                    ? getTransitionStyling(message)
                    : 'bg-white text-gray-900 border border-gray-200'
                } ${message.sender === 'ai' && !isTransitionMessage(message) ? 'prose prose-sm prose-gray' : ''}`}
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
                  <div 
                    dangerouslySetInnerHTML={{ 
                      __html: message.sender === 'ai' ? formatMessageContent(message.content) : message.content 
                    }} 
                  />
                )}
              </div>
            </div>
          ))}
          
          {/* Loading indicator */}
          {isLoading && (
            <div className="flex justify-start mb-3">
              <div className="bg-white px-3 py-2 border border-gray-200">
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
        <div className="border-t border-gray-200 p-3 bg-white flex-shrink-0">
          <div className="flex space-x-2">
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask your question here"
              className="flex-1 border-gray-200 font-work-sans py-2 px-3 text-sm focus:border-chewy-blue focus:ring-chewy-blue"
            />
            <Button 
              onClick={() => sendMessage()} 
              size="icon" 
              disabled={!inputValue.trim() || isLoading}
              className="bg-chewy-blue hover:bg-blue-700 w-9 h-9 flex items-center justify-center disabled:bg-gray-300"
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
          <div className="fixed left-0 bottom-0 w-full h-1/3 z-50 bg-white shadow-2xl border-t border-gray-200 rounded-t-lg flex flex-col" style={{minHeight: 320, maxHeight: 500}}>
            {/* Chat Content */}
            <div className="flex flex-col h-full">
                              <CardHeader className="bg-white border-b border-gray-100 p-3 rounded-t-lg flex-shrink-0">
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
                        .map((message) => (
                        <div
                          key={message.id}
                          className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                                                  <div
                          className={`max-w-[80%] px-3 py-2 rounded-lg font-work-sans text-sm ${
                            message.sender === 'user'
                              ? 'bg-chewy-blue text-white'
                              : isTransitionMessage(message)
                              ? getTransitionStyling(message)
                              : 'bg-gray-100 text-gray-900'
                          } ${message.sender === 'ai' && !isTransitionMessage(message) ? 'prose prose-sm prose-gray' : ''}`}
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
                              <div 
                                dangerouslySetInnerHTML={{ 
                                  __html: message.sender === 'ai' ? formatMessageContent(message.content) : message.content 
                                }} 
                              />
                            )}
                          </div>
                        </div>
                      ))}
                      
                      {/* Loading indicator */}
                      {isLoading && (
                        <div className="flex justify-start">
                          <div className="bg-gray-100 px-3 py-2 rounded-lg">
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
                    <div className="border-t border-gray-100 p-3 bg-white rounded-b-lg flex-shrink-0">
                      <div className="flex space-x-2">
                                              <Input
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="What do you want to learn?"
                        className="flex-1 rounded-md border-gray-200 font-work-sans py-2 px-3 text-sm focus:border-chewy-blue focus:ring-chewy-blue"
                      />
                                              <Button 
                        onClick={() => sendMessage()} 
                        size="icon" 
                        className="bg-chewy-blue hover:bg-blue-700 rounded-md w-9 h-9 flex items-center justify-center"
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
        <Card className="absolute bottom-16 right-0 w-80 h-[450px] shadow-2xl rounded-lg border-0">
          <CardHeader className="bg-white border-b border-gray-100 p-3 rounded-t-lg">
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
                    .map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                                                  <div
                          className={`max-w-[75%] px-3 py-2 rounded-lg font-work-sans text-sm ${
                            message.sender === 'user'
                              ? 'bg-chewy-blue text-white'
                              : isTransitionMessage(message)
                              ? getTransitionStyling(message)
                              : 'bg-gray-100 text-gray-900'
                          } ${message.sender === 'ai' && !isTransitionMessage(message) ? 'prose prose-sm prose-gray' : ''}`}
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
                              <div 
                                dangerouslySetInnerHTML={{ 
                                  __html: message.sender === 'ai' ? formatMessageContent(message.content) : message.content 
                                }} 
                              />
                            )}
                          </div>
                        </div>
                      ))}
                      
                      {/* Loading indicator */}
                      {isLoading && (
                        <div className="flex justify-start">
                          <div className="bg-gray-100 px-3 py-2 rounded-md">
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
                <div className="border-t border-gray-100 p-3 bg-white rounded-b-lg">
                  <div className="flex space-x-2">
                    <Input
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="What do you want to learn?"
                      className="flex-1 rounded-md border-gray-200 font-work-sans py-2 px-3 text-sm focus:border-chewy-blue focus:ring-chewy-blue"
                    />
                    <Button 
                      onClick={() => sendMessage()} 
                      size="icon" 
                      className="bg-chewy-blue hover:bg-blue-700 rounded-md w-9 h-9 flex items-center justify-center"
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
