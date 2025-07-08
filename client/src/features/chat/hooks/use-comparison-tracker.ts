import { useRef, useEffect } from 'react';
import { useGlobalChat } from '../context';

export const useComparisonTracker = () => {
  const {
    currentContext,
    isInComparisonMode,
    comparingProducts,
    clearComparison,
    addTransitionMessage,
    setCurrentContext
  } = useGlobalChat();
  
  const comparisonStartIndexRef = useRef<number>(-1);

  // Handle chat context changes from props
  const handleChatContextChange = (chatContext: any) => {
    if (chatContext) {
      setCurrentContext(chatContext);
      
      // Set comparison ref for comparison mode
      if (chatContext.type === 'comparison' && chatContext.products && chatContext.products.length >= 2) {
        comparisonStartIndexRef.current = 1;
      }
    }
  };

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

  const handleExitToGeneralChat = () => {
    const previousContext = currentContext;
    const newContext = { type: 'general' as const, product: undefined, products: undefined };
    
    clearComparison();
    comparisonStartIndexRef.current = -1; // Reset comparison start index
    
    // Add transition message when exiting to general chat
    addTransitionMessage(previousContext, newContext);
    setCurrentContext(newContext);
  };

  const resetComparisonTracker = () => {
    comparisonStartIndexRef.current = -1;
  };

  return {
    comparisonStartIndexRef,
    handleChatContextChange,
    handleExitToGeneralChat,
    resetComparisonTracker
  };
}; 