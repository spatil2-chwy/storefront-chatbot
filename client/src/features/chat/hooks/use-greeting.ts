import { useState, useEffect } from 'react';
import { chatApi } from '../../../lib/api';
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

  // Fetch personalized greeting when component mounts
  useEffect(() => {
    const fetchGreetingOnLoad = async () => {
      if (user && !preloadedGreeting) {
        console.log('Fetching personalized greeting for user:', user.customer_key);
        try {
          const response = await chatApi.getPersonalizedGreeting(user.customer_key);
          console.log('Received greeting response:', response);
          setPreloadedGreeting(response.greeting);
        } catch (error) {
          console.error('Failed to preload personalized greeting:', error);
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
    // Disabled to prevent confusion - initial greeting is sufficient
    return;
  };

  const showInitialSearchGreeting = async (initialQuery: string) => {
    // Show personalized greeting for search queries if user is logged in and in general chat mode
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
        
        // Add delay so greeting appears before main response
        await new Promise(resolve => setTimeout(resolve, 300));
      } else {
        // Fallback if greeting not preloaded
        try {
          const response = await chatApi.getPersonalizedGreeting(user.customer_key);
          const greetingMessage: ChatMessage = {
            id: `search-greeting-${Date.now()}`,
            content: response.greeting,
            sender: 'ai',
            timestamp: new Date(),
          };
          addMessage(greetingMessage);
          setSearchGreetingShown(true);
          
          // Add delay so greeting appears before main response
          await new Promise(resolve => setTimeout(resolve, 300));
        } catch (error) {
          console.error('Failed to fetch personalized search greeting:', error);
        }
      }
    }
  };

  const resetGreeting = () => {
    setGreetingShown(false);
    setSearchGreetingShown(false);
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