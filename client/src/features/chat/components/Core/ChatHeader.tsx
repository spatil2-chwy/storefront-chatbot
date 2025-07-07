import React from 'react';
import { X } from 'lucide-react';
import { Button } from '../../../../ui/Buttons/Button';
import { CardTitle } from '../../../../ui/Cards/Card';
import { ChatContext } from '../../../../types';

interface ChatHeaderProps {
  isLiveAgent: boolean;
  onModeSwitch: (liveAgent: boolean) => void;
  onClose?: () => void;
  onClearChat?: () => void;
  chatContext?: ChatContext;
  hasMessages: boolean;
  isDraggable?: boolean;
}

export const ChatHeader: React.FC<ChatHeaderProps> = ({
  isLiveAgent,
  onModeSwitch,
  onClose,
  onClearChat,
  chatContext,
  hasMessages,
  isDraggable = false
}) => {
  const getTitle = () => {
    if (chatContext?.type === 'product') {
      return 'AI Beta - Product Questions';
    }
    if (chatContext?.type === 'comparison') {
      return 'AI Beta - Product Comparison';
    }
    return isLiveAgent ? 'Live Agent' : 'AI Beta';
  };

  const headerClasses = isDraggable
    ? "bg-white border-b border-gray-100 p-3 rounded-t-lg drag-handle cursor-move"
    : "bg-white border-b border-gray-200 p-3 flex-shrink-0";

  return (
    <div className={headerClasses}>
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-chewy-blue rounded-full flex items-center justify-center">
            <img 
              src="/chewy-c-white.png" 
              alt="Chewy C" 
              className="w-5 h-5"
            />
          </div>
          <CardTitle className="text-gray-900 font-work-sans text-base">
            {getTitle()}
          </CardTitle>
        </div>
        
        {onClose && (
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-full w-7 h-7"
          >
            <X className="w-4 h-4" />
          </Button>
        )}

        {/* Clear Chat Button for embedded chats */}
        {chatContext && hasMessages && onClearChat && (
          <button
            onClick={onClearChat}
            className="text-xs text-gray-500 hover:text-gray-700 font-work-sans underline"
          >
            Clear chat
          </button>
        )}
      </div>
      
      {/* Toggle between AI and Live Agent - only for main chat, not embedded */}
      {!chatContext && (
        <div className="flex items-center justify-between mt-2">
          <div className="flex bg-gray-100 rounded-full p-0.5">
            <button
              onClick={() => onModeSwitch(false)}
              className={`px-3 py-1.5 rounded-full text-xs font-work-sans transition-colors ${
                !isLiveAgent 
                  ? 'bg-chewy-blue text-white' 
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              AI Chat
            </button>
            <button
              onClick={() => onModeSwitch(true)}
              className={`px-3 py-1.5 rounded-full text-xs font-work-sans transition-colors ${
                isLiveAgent 
                  ? 'bg-chewy-blue text-white' 
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              Live Agent
            </button>
          </div>
          
          {/* Clear Chat Button - Only show in AI mode */}
          {!isLiveAgent && hasMessages && onClearChat && (
            <div className="flex flex-col items-end space-y-1">
              <button
                onClick={onClearChat}
                className="text-xs text-gray-500 hover:text-gray-700 font-work-sans underline"
              >
                Clear chat
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}; 