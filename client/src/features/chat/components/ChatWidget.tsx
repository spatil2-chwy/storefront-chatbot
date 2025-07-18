import React, { useState, useEffect, useRef } from 'react';
import { useGlobalChat } from '../context';
import { ChatContext, ChatMessage, Product, PetProfileInfo } from '../../../types';
import { useGreeting } from '../hooks/use-greeting';
import { useComparisonTracker } from '../hooks/use-comparison-tracker';
import { SidebarChatLayout } from './Layout/SidebarChatLayout';
import { chatApi, productsApi } from '../../../lib/api';
import { useAuth } from '../../../lib/auth';

interface ChatWidgetProps {
  initialQuery?: string;
  shouldOpen?: boolean;
  shouldClearChat?: boolean;
  onClearChat?: () => void;
  chatContext?: ChatContext;
}

export default function ChatWidget({ 
  initialQuery, 
  shouldOpen, 
  shouldClearChat, 
  onClearChat, 
  chatContext
}: ChatWidgetProps) {
  // Use global state for search results and query
  const { 
    messages,
    addMessage,
    searchResults, 
    setSearchResults, 
    currentSearchQuery, 
    setCurrentSearchQuery, 
    hasSearched, 
    setHasSearched,
    setShouldAutoOpen,
    comparingProducts,
    isInComparisonMode,
    currentContext,
    setCurrentContext,
    addTransitionMessage,
    updateMessage,
    isOpen: isChatSidebarOpen,
    setIsOpen,
    shouldAutoOpen,
    clearMessages,
    clearComparison,
    isMainChatHidden,
    isOpen
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
  const [selectedImage, setSelectedImage] = useState<File | null>(null); // Track selected image for upload
  const [selectedPet, setSelectedPet] = useState<PetProfileInfo | undefined>(undefined); // Track selected pet
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

  // Handle pet selection
  const handlePetSelect = async (petId: string) => {
    if (!user?.customer_key) return;

    try {
      const response = await chatApi.selectPet(user.customer_key, petId);
      
      if (response.type === 'browse') {
        // User chose to browse - show browse message
        const browseMessage: ChatMessage = {
          id: `browse-${Date.now()}`,
          content: response.message || "Sounds good! What are you looking for today?",
          sender: 'ai',
          timestamp: new Date(),
        };
        addMessage(browseMessage);
        setSelectedPet(undefined);
        setCurrentContext({ type: 'general' });
      } else if (response.type === 'pet_profile' && response.pet_info) {
        // User selected a pet - show pet profile
        const petProfileMessage: ChatMessage = {
          id: `pet-profile-${Date.now()}`,
          content: "Here's what I know about your pet:",
          sender: 'ai',
          timestamp: new Date(),
          isPetProfile: true,
          petProfileInfo: response.pet_info,
        };
        addMessage(petProfileMessage);
        setSelectedPet(response.pet_info);
        setCurrentContext({ 
          type: 'general', 
          selectedPet: response.pet_info 
        });
      }
    } catch (error) {
      console.error('Error selecting pet:', error);
      const errorMessage: ChatMessage = {
        id: `pet-error-${Date.now()}`,
        content: "Sorry, I'm having trouble loading the pet information. Let's continue with general browsing.",
        sender: 'ai',
        timestamp: new Date(),
      };
      addMessage(errorMessage);
    }
  };

  // Handle pet profile actions
  const handlePetProfileAction = async (action: 'looks_good' | 'edit_info', petInfo?: PetProfileInfo) => {
    if (action === 'looks_good' && petInfo) {
      // User is happy with pet info - show shopping message
      const shoppingMessage: ChatMessage = {
        id: `shopping-${Date.now()}`,
        content: `Great! What are you looking for today?`,
        sender: 'ai',
        timestamp: new Date(),
      };
      addMessage(shoppingMessage);
      setSelectedPet(petInfo);
      setCurrentContext({ 
        type: 'general', 
        selectedPet: petInfo 
      });
    } else if (action === 'edit_info' && petInfo) {
      // User wants to edit pet info - enable inline editing on the current message
      // Find the pet profile message and update it to editing mode
      const petProfileMessage = messages.find(msg => 
        msg.isPetProfile && msg.petProfileInfo?.id === petInfo.id
      );
      
      if (petProfileMessage) {
        updateMessage(petProfileMessage.id, (msg) => ({
          ...msg,
          isEditing: true
        }));
      } else {
        // Fallback: create a new message if the original wasn't found
        const editMessage: ChatMessage = {
          id: `pet-edit-${Date.now()}`,
          content: "Let's update your pet's information:",
          sender: 'ai',
          timestamp: new Date(),
          isPetProfile: true,
          petProfileInfo: petInfo,
          isEditing: true,
        };
        addMessage(editMessage);
      }
    }
  };

  // Handle pet edit save
  const handlePetEditSave = async (updatedPet: PetProfileInfo) => {
    try {
      const response = await chatApi.updatePetProfile(updatedPet.id, updatedPet);
      
      // Find and update the pet profile message
      const petProfileMessage = messages.find(msg => 
        msg.isPetProfile && msg.petProfileInfo?.id === updatedPet.id
      );
      
      if (petProfileMessage) {
        updateMessage(petProfileMessage.id, (msg) => ({
          ...msg,
          petProfileInfo: response.pet_info,
          isEditing: false
        }));
      } else {
        // Fallback: create a new message with the updated profile
        const updatedProfileMessage: ChatMessage = {
          id: `pet-profile-updated-${Date.now()}`,
          content: `Great! What are you looking for today?`,
          sender: 'ai',
          timestamp: new Date(),
          isPetProfile: true,
          petProfileInfo: response.pet_info,
          isEditing: false,
        };
        addMessage(updatedProfileMessage);
      }
      
      setSelectedPet(response.pet_info);
      setCurrentContext({ 
        type: 'general', 
        selectedPet: response.pet_info 
      });
    } catch (error) {
      console.error('Error updating pet profile:', error);
      const errorMessage: ChatMessage = {
        id: `pet-update-error-${Date.now()}`,
        content: "Sorry, I'm having trouble updating the pet information. Let's continue with what we have.",
        sender: 'ai',
        timestamp: new Date(),
      };
      addMessage(errorMessage);
    }
  };

  // Handle pet edit cancel
  const handlePetEditCancel = () => {
    // Find and update the pet profile message to disable editing
    const petProfileMessage = messages.find(msg => 
      msg.isPetProfile && msg.isEditing
    );
    
    if (petProfileMessage) {
      updateMessage(petProfileMessage.id, (msg) => ({
        ...msg,
        isEditing: false
      }));
    } else {
      // Fallback: add a cancel message
      const cancelMessage: ChatMessage = {
        id: `pet-edit-cancel-${Date.now()}`,
        content: "No problem! Let's continue with the current information.",
        sender: 'ai',
        timestamp: new Date(),
      };
      addMessage(cancelMessage);
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
      
      const generateResponse = async () => {
        // Show greeting first if it hasn't been shown yet
        await showInitialSearchGreeting(initialQuery);
        
        const userMessage: ChatMessage = {
          id: Date.now().toString(),
          content: `Searching for: ${initialQuery}`,
          sender: 'user',
          timestamp: new Date(),
        };
        addMessage(userMessage);
        setIsLoading(true);
        try {
          const chatHistory = messages.map(msg => ({
            role: msg.sender === 'user' ? 'user' : 'assistant',
            content: msg.content
          }));
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
          await chatApi.chatbotStream(
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
            },
            undefined // No image for initial query
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
  }, [initialQuery, shouldClearChat, isLiveAgent, addMessage, clearMessages, messages, user, updateMessage, setSearchResults, setCurrentSearchQuery, setHasSearched, showInitialSearchGreeting]);

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
    if ((!messageToSend.trim() && !selectedImage) || isLiveAgent) return;
    
    setInputValue('');
    
    let imageBase64: string | undefined;
    let imageUrl: string | undefined;
    
    // Handle image conversion if present
    if (selectedImage) {
      try {
        imageBase64 = await convertImageToBase64(selectedImage);
        imageUrl = URL.createObjectURL(selectedImage);
      } catch (error) {
        console.error('Error converting image to base64:', error);
        return;
      }
    }
    
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: messageToSend,
      sender: 'user',
      timestamp: new Date(),
      image: imageBase64,
      imageUrl: imageUrl,
    };
    
    addMessage(userMessage);
    setSelectedImage(null); // Clear selected image after sending
    setIsLoading(true);
    try {
      const chatHistory = messages.map(msg => {
        if (msg.sender === 'user' && msg.image) {
          // Format message with image for LLM
          return {
            role: 'user',
            content: [
              { type: "input_text", text: msg.content },
              {
                type: "input_image",
                image_url: `data:image/jpeg;base64,${msg.image}`,
              },
            ],
          };
        } else {
          return {
            role: msg.sender === 'user' ? 'user' : 'assistant',
            content: msg.content
          };
        }
      });
      
      // Add current message to history if it has an image
      if (imageBase64) {
        chatHistory.push({
          role: 'user',
          content: [
            { type: "input_text", text: messageToSend },
            {
              type: "input_image", 
              image_url: `data:image/jpeg;base64,${imageBase64}`,
            },
          ],
        });
      } else {
        chatHistory.push({
          role: 'user',
          content: messageToSend
        });
      }
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
        const response = await productsApi.compareProducts(messageToSend, comparingProducts, chatHistory, imageBase64);
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
        const response = await productsApi.askAboutProduct(messageToSend, currentContext.product, chatHistory, imageBase64);
        updateMessage(responseId, (msg) => ({ 
          ...msg, 
          content: response,
          productTitle: `${currentContext.product?.brand || ''} ${currentContext.product?.title || ''}`,
        }));
        setIsStreaming(false);
        setStreamingMessageId(null);
      } else if (currentContext.type === 'comparison' && currentContext.products) {
        // Use compare endpoint for comparison context
        const response = await productsApi.compareProducts(messageToSend, currentContext.products, chatHistory, imageBase64);
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
        await chatApi.chatbotStream(
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
          },
          imageBase64, // Pass image if present
          selectedPet // Pass selected pet context
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
    setSelectedImage(null);
    setSelectedPet(undefined);
    resetProcessedQuery();
    resetComparisonTracker();
    resetGreeting();
    onClearChat?.();
  };

  const handleSuggestionClick = (suggestion: string) => {
    sendMessage(suggestion);
  };

  const handleTagClick = (tag: string) => {
    sendMessage(tag);
  };

  const handleClearComparison = () => {
    clearComparison();
    resetComparisonTracker();
  };

  const handleExitProductChat = () => {
    handleExitToGeneralChat();
  };

  // Image handling functions
  const handleImageUpload = (file: File) => {
    setSelectedImage(file);
  };

  const handleImageRemove = () => {
    setSelectedImage(null);
  };

  // Convert image to base64
  const convertImageToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        if (reader.result && typeof reader.result === 'string') {
          // Remove the data:image/jpeg;base64, prefix to get just the base64 string
          const base64 = reader.result.split(',')[1];
          resolve(base64);
        } else {
          reject(new Error('Failed to convert image to base64'));
        }
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
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
      onTagClick={handleTagClick}
      onImageUpload={handleImageUpload}
      selectedImage={selectedImage}
      onImageRemove={handleImageRemove}
      onPetSelect={handlePetSelect}
      onPetProfileAction={handlePetProfileAction}
      onPetEditSave={handlePetEditSave}
      onPetEditCancel={handlePetEditCancel}
    />
  );
}
