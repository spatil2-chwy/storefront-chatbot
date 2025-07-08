import React, { createContext, useContext, useState, ReactNode, useCallback, useMemo } from 'react';
import { ChatMessage, ChatContext as ChatContextType, Product } from '../../types';

interface GlobalChatContextType {
  messages: ChatMessage[];
  setMessages: (messages: ChatMessage[]) => void;
  addMessage: (message: ChatMessage) => void;
  insertMessageAt: (message: ChatMessage, index: number) => void;
  updateMessage: (messageId: string, updater: (message: ChatMessage) => ChatMessage) => void;
  clearMessages: () => void;
  // New method for context transitions
  addTransitionMessage: (fromContext: ChatContextType, toContext: ChatContextType) => void;
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
  // Comparison state management
  comparingProducts: Product[];
  addToComparison: (product: Product) => void;
  removeFromComparison: (productId: number) => void;
  clearComparison: () => void;
  isInComparisonMode: boolean;
  // Auto-open management
  shouldAutoOpen: boolean;
  setShouldAutoOpen: (should: boolean) => void;
  // Hide main chat when product modal is active
  isMainChatHidden: boolean;
  setIsMainChatHidden: (hidden: boolean) => void;
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

  // Comparison state management
  const [comparingProducts, setComparingProducts] = useState<Product[]>([]);
  
  // Auto-open management
  const [shouldAutoOpen, setShouldAutoOpen] = useState<boolean>(false);
  
  // Hide main chat when product modal is active
  const [isMainChatHidden, setIsMainChatHidden] = useState<boolean>(false);
  
  // Track if a transition message was recently added to prevent duplicates
  const [lastTransitionTime, setLastTransitionTime] = useState<number>(0);

  // Compute comparison mode based on number of products (need 2+ to compare)
  const isInComparisonMode = useMemo(() => {
    return comparingProducts.length >= 2;
  }, [comparingProducts.length]);

  const addMessage = useCallback((message: ChatMessage) => {
    setMessages(prev => [...prev, message]);
  }, []);

  const insertMessageAt = useCallback((message: ChatMessage, index: number) => {
    setMessages(prev => {
      const newMessages = [...prev];
      newMessages.splice(index, 0, message);
      return newMessages;
    });
  }, []);

  const updateMessage = useCallback((messageId: string, updater: (message: ChatMessage) => ChatMessage) => {
    setMessages(prev => 
      prev.map(msg => msg.id === messageId ? updater(msg) : msg)
    );
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  // New method to handle context transitions with appropriate messages
  const addTransitionMessage = useCallback((fromContext: ChatContextType, toContext: ChatContextType) => {
    // Prevent duplicate transitions within 1 second
    const now = Date.now();
    if (now - lastTransitionTime < 1000) {
      return;
    }
    
    let transitionContent = '';
    let transitionType: 'general' | 'product' | 'comparison' | undefined = undefined;
    
    if (toContext.type === 'product' && toContext.product) {
      transitionContent = `Now discussing: ${toContext.product.brand} ${toContext.product.title}`;
      transitionType = 'product';
    } else if (toContext.type === 'comparison' && toContext.products && toContext.products.length > 0) {
      transitionContent = `Now comparing: ${toContext.products.length} products`;
      transitionType = 'comparison';
    } else if (toContext.type === 'general') {
      if (fromContext.type === 'product') {
        transitionContent = 'Returned to general chat';
        transitionType = 'general';
      } else if (fromContext.type === 'comparison') {
        transitionContent = 'Returned to general chat';
        transitionType = 'general';
      }
    }

    if (transitionContent && transitionType) {
      setLastTransitionTime(now);
      const transitionMessage: ChatMessage = {
        id: Date.now().toString(),
        content: transitionContent,
        sender: 'ai',
        timestamp: new Date(),
        isTransition: true,
        transitionType: transitionType,
        // Store product data for individual product transitions
        productData: transitionType === 'product' && toContext.product ? toContext.product : undefined,
        // Store comparison data for historical preservation
        comparisonProductCount: transitionType === 'comparison' && toContext.products ? toContext.products.length : undefined,
        comparisonProducts: transitionType === 'comparison' && toContext.products ? toContext.products : undefined,
      };
      addMessage(transitionMessage);
    }
  }, [addMessage, lastTransitionTime]);

  const addToComparison = useCallback((product: Product) => {
    setComparingProducts(prev => {
      const exists = prev.find(p => p.id === product.id);
      if (exists) return prev; // Already in comparison
      
      // Limit to 4 products maximum
      if (prev.length >= 4) return prev;
      
      return [...prev, product];
    });
  }, []);

  const removeFromComparison = useCallback((productId: number) => {
    setComparingProducts(prev => {
      return prev.filter(p => p.id !== productId);
    });
  }, []);

  const clearComparison = useCallback(() => {
    setComparingProducts([]);
  }, []);

  return (
    <GlobalChatContext.Provider
      value={{
        messages,
        setMessages,
        addMessage,
        insertMessageAt,
        updateMessage,
        clearMessages,
        addTransitionMessage,
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
        comparingProducts,
        addToComparison,
        removeFromComparison,
        clearComparison,
        isInComparisonMode,
        shouldAutoOpen,
        setShouldAutoOpen,
        isMainChatHidden,
        setIsMainChatHidden,
      }}
    >
      {children}
    </GlobalChatContext.Provider>
  );
}; 