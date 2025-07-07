import React from 'react';
import { MessageCircle } from 'lucide-react';
import { Button } from '../../../../ui/Buttons/Button';
import { ChatHeader } from '../Core/ChatHeader';
import { ChatMessages } from '../Core/ChatMessages';
import { ChatInput } from '../Core/ChatInput';
import { LiveAgentFallback } from '../Fallbacks/LiveAgentFallback';
import { ChatMessage } from '../../../../types';

interface DesktopChatWindowProps {
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
}

export const DesktopChatWindow: React.FC<DesktopChatWindowProps> = ({
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
  onClearComparison
}) => {
  return (
    <>
      {/* Chat Button (always visible, floating, bottom right) */}
      <Button
        onClick={onToggle}
        className="fixed bottom-6 right-6 w-14 h-14 bg-chewy-blue hover:bg-blue-700 text-white rounded-full shadow-lg flex items-center justify-center z-40"
        size="icon"
      >
        <MessageCircle className="w-6 h-6" />
      </Button>
      
      {/* Desktop Chat Window */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 w-96 h-[500px] bg-white border border-gray-200 rounded-lg shadow-xl flex flex-col z-50">
          <ChatHeader
            isLiveAgent={isLiveAgent}
            onModeSwitch={onModeSwitch}
            onClose={onClose}
            onClearChat={onClearChat}
            hasMessages={messages.length > 0}
            isDraggable={true}
          />

          <div className="flex-1 flex flex-col overflow-hidden">
            {/* AI Chat Mode */}
            {!isLiveAgent && (
              <>
                {/* Messages - Scrollable area */}
                <ChatMessages
                  messages={messages}
                  isLoading={isLoading}
                  onSuggestionClick={onSuggestionClick}
                  onClearComparison={onClearComparison}
                  shouldAutoScroll={true}
                />

                {/* Input - Fixed at bottom */}
                <ChatInput
                  value={inputValue}
                  onChange={onInputChange}
                  onSend={onSend}
                  onKeyPress={onKeyPress}
                  disabled={isLoading}
                  placeholder="What do you want to learn?"
                />
              </>
            )}

            {/* Live Agent Mode */}
            {isLiveAgent && (
              <div className="flex-1 p-6 bg-white rounded-b-lg overflow-y-auto">
                <LiveAgentFallback />
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}; 