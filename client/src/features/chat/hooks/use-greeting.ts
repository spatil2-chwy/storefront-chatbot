import { useState, useEffect } from 'react';
import { api } from '../../../lib/api';
import { useAuth } from '../../../lib/auth';
import { useGlobalChat } from '../context';
import { ChatMessage } from '../../../types';

export const useGreeting = () => {
  const { user } = useAuth();
  const { 
    messages, 
    addMessage, 
    currentContext, 
    isOpen 
  } = useGlobalChat();
  
  const [greetingShown, setGreetingShown] = useState(false);
  const [searchGreetingShown, setSearchGreetingShown] = useState(false);
  const [preloadedGreeting, setPreloadedGreeting] = useState<string | null>(null);

  // Fetch personalized greeting when component mounts (page loads)
  useEffect(() => {
    const fetchGreetingOnLoad = async () => {
      if (user && !preloadedGreeting) {
        console.log('Fetching personalized greeting for user:', user.customer_key);
        try {
          const response = await api.getPersonalizedGreeting(user.customer_key);
          console.log('Received greeting response:', response);
          setPreloadedGreeting(response.greeting);
        } catch (error) {
          console.error('Failed to preload personalized greeting:', error);
          // Set fallback greeting
          setPreloadedGreeting("Hey there! What can I help you find for your furry friends today?");
        }
      }
    };

    fetchGreetingOnLoad();
  }, [user, preloadedGreeting]);

  // Display preloaded greeting when chat opens for the first time
  useEffect(() => {
    const displayGreeting = () => {
      console.log('Display greeting check:', {
        isOpen,
        hasUser: !!user,
        greetingShown,
        messagesLength: messages.length,
        currentContextType: currentContext.type,
        hasPreloadedGreeting: !!preloadedGreeting,
        preloadedGreeting
      });
      
      if (isOpen && user && !greetingShown && messages.length === 0 && (!currentContext.type || currentContext.type === 'general') && preloadedGreeting) {
        console.log('Adding greeting message to chat:', preloadedGreeting);
        const greetingMessage: ChatMessage = {
          id: `greeting-${Date.now()}`,
          content: preloadedGreeting,
          sender: 'ai',
          timestamp: new Date(),
        };
        addMessage(greetingMessage);
        setGreetingShown(true);
      }
    };

    displayGreeting();
  }, [isOpen, user, greetingShown, messages.length, currentContext.type, preloadedGreeting, addMessage]);

  const showSearchGreeting = async (messageToSend: string) => {
    // Disable follow-up greetings to prevent confusion
    // The initial greeting when opening chat should be sufficient
    return;
  };

  const showInitialSearchGreeting = async (initialQuery: string) => {
    // Show personalized greeting for search queries if user is logged in and it's general chat mode
    const shouldShowSearchGreeting = (
      user && 
      !searchGreetingShown && 
      (!currentContext.type || currentContext.type === 'general')
    );

    if (shouldShowSearchGreeting) {
      if (preloadedGreeting) {
        const greetingMessage: ChatMessage = {
          id: `search-greeting-${Date.now()}`,
          content: preloadedGreeting,
          sender: 'ai',
          timestamp: new Date(),
        };
        addMessage(greetingMessage);
        setSearchGreetingShown(true);
        
        // Add a small delay so the greeting appears before the main response
        await new Promise(resolve => setTimeout(resolve, 500));
      } else {
        // Fallback if greeting not preloaded
        try {
          const response = await api.getPersonalizedGreeting(user.customer_key);
          const greetingMessage: ChatMessage = {
            id: `search-greeting-${Date.now()}`,
            content: response.greeting,
            sender: 'ai',
            timestamp: new Date(),
          };
          addMessage(greetingMessage);
          setSearchGreetingShown(true);
          
          // Add a small delay so the greeting appears before the main response
          await new Promise(resolve => setTimeout(resolve, 500));
        } catch (error) {
          console.error('Failed to fetch personalized search greeting:', error);
          // Continue without greeting if it fails
        }
      }
    }
  };

  const resetGreeting = () => {
    setGreetingShown(false);
    setSearchGreetingShown(false); // Keep for compatibility but not used for follow-ups
    setPreloadedGreeting(null);
  };

  return {
    greetingShown,
    searchGreetingShown,
    preloadedGreeting,
    showSearchGreeting,
    showInitialSearchGreeting,
    resetGreeting
  };
}; 