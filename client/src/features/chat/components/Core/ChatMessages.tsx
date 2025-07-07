import React, { useEffect, useRef } from 'react';
import { Loader2, Bot } from 'lucide-react';
import { Skeleton } from '../../../../ui/Feedback/Skeleton';
import { ChatMessageItem } from './ChatMessageItem';
import { ChatSuggestions } from './ChatSuggestions';
import { ChatContext, ChatMessage } from '../../../../types';

interface ChatMessagesProps {
  messages: ChatMessage[];
  isLoading: boolean;
  chatContext?: ChatContext;
  onSuggestionClick: (suggestion: string) => void;
  onClearComparison: () => void;
  isEmbedded?: boolean;
  isMobile?: boolean;
  shouldAutoScroll?: boolean;
}

export const ChatMessages: React.FC<ChatMessagesProps> = ({
  messages,
  isLoading,
  chatContext,
  onSuggestionClick,
  onClearComparison,
  isEmbedded = false,
  isMobile = false,
  shouldAutoScroll = true
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (shouldAutoScroll) {
      const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      };
      // Small delay to ensure DOM is updated
      setTimeout(scrollToBottom, 100);
    }
  }, [messages, shouldAutoScroll]);

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.length === 0 ? (
        <ChatSuggestions onSuggestionClick={onSuggestionClick} />
      ) : (
        messages.map((message) => (
          <ChatMessageItem
            key={message.id}
            message={message}
            onClearComparison={onClearComparison}
            chatContext={chatContext}
            isMobile={isMobile}
          />
        ))
      )}
      
      {/* Loading indicator */}
      {isLoading && (
        <div className="flex items-center space-x-2 text-gray-500">
          <Loader2 className="h-4 w-4 animate-spin" />
          <span className="text-sm">Thinking...</span>
        </div>
      )}
      
      {/* Loading skeleton */}
      {isLoading && (
        <div className="flex items-start space-x-2">
          <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center flex-shrink-0">
            <Bot className="w-4 h-4 text-white" />
          </div>
          <div className="flex-1 space-y-2">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
          </div>
        </div>
      )}
      
      {/* Invisible element to scroll to */}
      <div ref={messagesEndRef} />
    </div>
  );
}; 