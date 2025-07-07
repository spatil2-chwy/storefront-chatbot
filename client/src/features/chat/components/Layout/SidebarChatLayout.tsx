import React, { useEffect } from 'react';
import { MessageCircle, X } from 'lucide-react';
import { Button } from '../../../../ui/Buttons/Button';
import { ChatHeader } from '../Core/ChatHeader';
import { ChatMessages } from '../Core/ChatMessages';
import { ChatInput } from '../Core/ChatInput';
import { LiveAgentFallback } from '../Fallbacks/LiveAgentFallback';
import { ChatMessage, ChatContext } from '../../../../types';

interface SidebarChatLayoutProps {
  isOpen: boolean;
  onToggle: () => void;
  isLiveAgent: boolean;
  onModeSwitch: (liveAgent: boolean) => void;
  onClose: () => void;
  onClearChat: () => void;
  messages: ChatMessage[];
  isLoading: boolean;
  inputValue: string;
  onInputChange: (value: string) => void;
  onSend: () => void;
  onKeyPress: (e: React.KeyboardEvent) => void;
  onSuggestionClick: (suggestion: string) => void;
  onClearComparison: () => void;
  chatContext?: ChatContext;
  isEmbedded?: boolean;
}

export const SidebarChatLayout: React.FC<SidebarChatLayoutProps> = ({
  isOpen,
  onToggle,
  isLiveAgent,
  onModeSwitch,
  onClose,
  onClearChat,
  messages,
  isLoading,
  inputValue,
  onInputChange,
  onSend,
  onKeyPress,
  onSuggestionClick,
  onClearComparison,
  chatContext,
  isEmbedded = false
}) => {
  // Handle body scroll and layout adjustment when sidebar is open
  useEffect(() => {
    if (!isEmbedded) {
      const body = document.body;
      const html = document.documentElement;
      
      if (isOpen) {
        // Add classes to indicate chat is open
        body.classList.add('chat-sidebar-open');
        html.classList.add('chat-sidebar-open');
        
        // Prevent body scroll on mobile only
        if (window.innerWidth < 768) {
          body.style.overflow = 'hidden';
        }
      } else {
        // Remove classes and restore scroll
        body.classList.remove('chat-sidebar-open');
        html.classList.remove('chat-sidebar-open');
        body.style.overflow = '';
      }
      
      // Cleanup function
      return () => {
        body.classList.remove('chat-sidebar-open');
        html.classList.remove('chat-sidebar-open');
        body.style.overflow = '';
      };
    }
  }, [isOpen, isEmbedded]);

  // For embedded mode (like comparison pages), render inline
  if (isEmbedded) {
    return (
      <div className="h-full flex flex-col bg-white border border-gray-200 rounded-lg shadow-sm">
        <ChatHeader
          isLiveAgent={isLiveAgent}
          onModeSwitch={onModeSwitch}
          onClearChat={onClearChat}
          chatContext={chatContext}
          hasMessages={messages.length > 0}
        />

        <div className="flex-1 flex flex-col overflow-hidden">
          {!isLiveAgent ? (
            <>
              <ChatMessages
                messages={messages}
                isLoading={isLoading}
                chatContext={chatContext}
                onSuggestionClick={onSuggestionClick}
                onClearComparison={onClearComparison}
                isEmbedded={true}
                shouldAutoScroll={true}
              />
              <ChatInput
                value={inputValue}
                onChange={onInputChange}
                onSend={onSend}
                onKeyPress={onKeyPress}
                disabled={isLoading}
                placeholder="Ask your question here"
                isEmbedded={true}
              />
            </>
          ) : (
            <div className="flex-1 p-6 bg-white overflow-y-auto">
              <LiveAgentFallback />
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <>
      {/* Chat Toggle Button - Always visible when sidebar is closed */}
      {!isOpen && (
        <Button
          onClick={onToggle}
          className="fixed bottom-6 right-6 w-14 h-14 bg-chewy-blue hover:bg-blue-700 text-white rounded-full shadow-lg flex items-center justify-center z-50 transition-all duration-300 hover:scale-110"
          size="icon"
          aria-label="Open chat"
        >
          <MessageCircle className="w-6 h-6" />
        </Button>
      )}

      {/* Sidebar Chat Panel */}
      <div
        className={`fixed top-0 right-0 h-full bg-white shadow-2xl border-l border-gray-200 z-50 transition-transform duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        } ${
          // Responsive width: full width on mobile, fixed width on desktop
          'w-full md:w-96 lg:w-[400px]'
        }`}
        role="complementary"
        aria-label="Chat sidebar"
      >
        <div className="h-full flex flex-col">
          {/* Header */}
          <ChatHeader
            isLiveAgent={isLiveAgent}
            onModeSwitch={onModeSwitch}
            onClose={onClose}
            onClearChat={onClearChat}
            chatContext={chatContext}
            hasMessages={messages.length > 0}
          />

          {/* Chat Content */}
          <div className="flex-1 flex flex-col overflow-hidden">
            {!isLiveAgent ? (
              <>
                <ChatMessages
                  messages={messages}
                  isLoading={isLoading}
                  chatContext={chatContext}
                  onSuggestionClick={onSuggestionClick}
                  onClearComparison={onClearComparison}
                  shouldAutoScroll={true}
                />
                <ChatInput
                  value={inputValue}
                  onChange={onInputChange}
                  onSend={onSend}
                  onKeyPress={onKeyPress}
                  disabled={isLoading}
                  placeholder="What do you want to learn?"
                />
              </>
            ) : (
              <div className="flex-1 p-6 bg-white overflow-y-auto">
                <LiveAgentFallback />
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Overlay for mobile when sidebar is open */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}
    </>
  );
}; 