import React from 'react';
import { User, Bot, ShoppingCart, X } from 'lucide-react';
import { Button } from '../../../../ui/Buttons/Button';
import { ChatContext, ChatMessage } from '../../../../types';
import { getTransitionStyling, isTransitionMessage } from '../../utils/chat-utilities';
import { formatMessageContent } from '../../utils/message-formatting';

interface ChatMessageItemProps {
  message: ChatMessage;
  onClearComparison: () => void;
  chatContext?: ChatContext;
  isMobile?: boolean;
}

export const ChatMessageItem: React.FC<ChatMessageItemProps> = ({
  message,
  onClearComparison,
  chatContext,
  isMobile = false
}) => {
  const isTransition = isTransitionMessage(message);
  const isUser = message.sender === 'user';
  
  // Handle transition messages
  if (isTransition) {
    return (
      <div className={`px-4 py-2 rounded-lg text-sm text-center ${getTransitionStyling(message)}`}>
        {message.content}
      </div>
    );
  }

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} items-start space-x-2`}>
      {/* Avatar - only for AI messages */}
      {!isUser && (
        <div className="w-8 h-8 bg-chewy-blue rounded-full flex items-center justify-center flex-shrink-0">
          <img 
            src="/chewy-c-white.png" 
            alt="Chewy C" 
            className="w-5 h-5"
          />
        </div>
      )}
      
      {/* Message Content */}
      <div className={`max-w-xs lg:max-w-md px-3 py-2 rounded-lg ${
        isUser 
          ? 'bg-chewy-blue text-white' 
          : 'bg-gray-100 text-gray-900'
      }`}>
        {/* Show comparison mode indicator */}
        {!isUser && message.content.includes('Now comparing:') && (
          <div className="flex items-center justify-between mb-2 p-2 bg-purple-50 rounded border border-purple-200">
            <div className="flex items-center space-x-2">
              <ShoppingCart className="w-4 h-4 text-purple-600" />
              <span className="text-sm font-medium text-purple-700">Comparison Mode</span>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClearComparison}
              className="text-purple-600 hover:text-purple-700 hover:bg-purple-100 p-1"
            >
              <X className="w-3 h-3" />
            </Button>
          </div>
        )}
        
        {/* Message text */}
        <div 
          className={`text-sm ${isUser ? 'text-white' : 'text-gray-900'}`}
          dangerouslySetInnerHTML={{ __html: formatMessageContent(message.content) }}
        />
      </div>
      
      {/* User avatar */}
      {isUser && (
        <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center flex-shrink-0">
          <User className="w-4 h-4 text-gray-600" />
        </div>
      )}
    </div>
  );
}; 