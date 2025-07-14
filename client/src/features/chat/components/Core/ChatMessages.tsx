import React, { useEffect, useRef } from 'react';
import { Loader2, Bot } from 'lucide-react';
import { Skeleton } from '../../../../ui/Feedback/Skeleton';
import { ChatMessageItem } from './ChatMessageItem';
import { ChatSuggestions } from './ChatSuggestions';
import { ChatContext, ChatMessage } from '../../../../types';
import { isTransitionMessage } from "../../../../lib/utils";

interface ChatMessagesProps {
  messages: ChatMessage[];
  isLoading: boolean;
  chatContext?: ChatContext;
  activeChatContext?: ChatContext;
  onSuggestionClick: (suggestion: string) => void;
  onClearComparison: () => void;
  onExitProductChat: () => void;
  isEmbedded?: boolean;
  isMobile?: boolean;
  isStreaming: boolean;
  streamingMessageId?: string | null;
  userHasScrolled: boolean;
  onScroll: (event: React.UIEvent<HTMLDivElement>) => void;
  scrollContainerRef: React.RefObject<HTMLDivElement>;
  onTagClick?: (tag: string) => void;
}

export const ChatMessages: React.FC<ChatMessagesProps> = ({
  messages,
  isLoading,
  chatContext,
  activeChatContext,
  onSuggestionClick,
  onClearComparison,
  onExitProductChat,
  isEmbedded = false,
  isMobile = false,
  isStreaming,
  streamingMessageId,
  userHasScrolled,
  onScroll,
  scrollContainerRef,
  onTagClick,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const lastProductMessageIndex = messages.map(m => isTransitionMessage(m) && m.content.includes('Now discussing:')).lastIndexOf(true);

  return (
    <div 
      className="flex-1 overflow-y-auto p-4 space-y-4" 
      ref={scrollContainerRef} 
      onScroll={onScroll}
    >
      {messages.length === 0 ? (
        <ChatSuggestions onSuggestionClick={onSuggestionClick} />
      ) : (
        messages.map((message, index) => (
          <ChatMessageItem
            key={message.id}
            message={message}
            onClearComparison={onClearComparison}
            onExitProductChat={onExitProductChat}
            chatContext={chatContext}
            isMobile={isMobile}
            isStreaming={streamingMessageId === message.id}
            showExitButton={index === lastProductMessageIndex && activeChatContext?.type === 'product'}
            onTagClick={onTagClick}
          />
        ))
      )}
      
      {/* Loading indicator - only show when loading and not streaming */}
      {isLoading && !isStreaming && (
        <div className="flex items-center space-x-2 text-gray-500">
          <Loader2 className="h-4 w-4 animate-spin" />
          <span className="text-sm">Thinking...</span>
        </div>
      )}
      
      {/* Loading skeleton - only show when loading and not streaming */}
      {isLoading && !isStreaming && (
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
      
      {/* New message indicator when streaming and user has scrolled up */}
      {isStreaming && userHasScrolled && (
        <div className="flex justify-center sticky bottom-2">
          <div className="bg-chewy-blue text-white px-3 py-1 rounded-full text-xs font-work-sans animate-pulse">
            New message incoming...
          </div>
        </div>
      )}

      {/* Invisible element to scroll to */}
      <div ref={messagesEndRef} />
    </div>
  );
}; 