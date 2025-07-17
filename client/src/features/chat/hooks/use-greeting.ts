import { useState, useEffect } from 'react';
import { chatApi } from '../../../lib/api';
import { useAuth } from '../../../lib/auth';
import { useGlobalChat } from '../context';
import { ChatMessage, PetOption, PetProfileInfo } from '../../../types';

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
  const [preloadedGreeting, setPreloadedGreeting] = useState<{
    greeting: string;
    has_pets: boolean;
    pet_options: PetOption[];
  } | null>(null);

  // Fetch personalized greeting when component mounts
  useEffect(() => {
    const fetchGreetingOnLoad = async () => {
      if (user && !preloadedGreeting) {
        try {
          const response = await chatApi.getPersonalizedGreeting(user.customer_key);
          setPreloadedGreeting(response);
        } catch (error) {
          console.error('Failed to preload personalized greeting:', error);
          setPreloadedGreeting({
            greeting: "Hey there! What can I help you find for your furry friends today?",
            has_pets: false,
            pet_options: []
          });
        }
      }
    };

    fetchGreetingOnLoad();
  }, [user, preloadedGreeting]);

  // Display preloaded greeting when chat opens for the first time
  useEffect(() => {
    const displayGreeting = () => {
      if (isOpen && user && !greetingShown && messages.length === 0 && (!currentContext.type || currentContext.type === 'general') && preloadedGreeting) {
        // Create greeting message with pet selection if user has pets
        const greetingMessage: ChatMessage = {
          id: `greeting-${Date.now()}`,
          content: preloadedGreeting.greeting,
          sender: 'ai',
          timestamp: new Date(),
        };

        // If user has pets, include pet selection in the same message
        if (preloadedGreeting.has_pets && preloadedGreeting.pet_options.length > 0) {
          greetingMessage.isPetSelection = true;
          greetingMessage.petOptions = preloadedGreeting.pet_options;
        }

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
          content: preloadedGreeting.greeting,
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