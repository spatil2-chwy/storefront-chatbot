import { ChatMessage } from '../../../types';

// Chat utility functions for styling and message type detection

// Helper function to get transition message styling based on type
export const getTransitionStyling = (message: ChatMessage): string => {
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
export const isTransitionMessage = (message: ChatMessage): boolean => {
  return message.isTransition || 
         message.content.includes('Now comparing:') || 
         message.content.includes('Now discussing:') || 
         message.content.includes('Returned to') || 
         message.content.includes('Exited');
}; 