import React, { useState } from 'react';
import { X, Bot } from 'lucide-react';
import { Button } from '../../../../ui/Buttons/Button';
import { CardTitle } from '../../../../ui/Cards/Card';
import { ChatContext } from '../../../../types';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '../../../../ui/Overlay/AlertDialog';

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
  const [showClearDialog, setShowClearDialog] = useState(false);

  const getTitle = () => {
    if (chatContext?.type === 'product') {
      return 'Tylee - Product Questions';
    }
    if (chatContext?.type === 'comparison') {
      return 'Tylee - Product Comparison';
    }
    return isLiveAgent ? 'Live Agent' : 'Tylee';
  };

  const handleClearChat = () => {
    setShowClearDialog(false);
    onClearChat?.();
  };

  const headerClasses = isDraggable
    ? "bg-white border-b border-gray-100 p-3 rounded-t-lg drag-handle cursor-move"
    : "bg-white border-b border-gray-200 p-3 flex-shrink-0";

  return (
    <div className={headerClasses}>
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-chewy-blue rounded-full flex items-center justify-center">
            <Bot className="w-4 h-4 text-white" />
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
          <AlertDialog open={showClearDialog} onOpenChange={setShowClearDialog}>
            <AlertDialogTrigger asChild>
              <button className="text-xs text-gray-500 hover:text-gray-700 font-work-sans underline">
                Clear chat
              </button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Clear Chat History</AlertDialogTitle>
                <AlertDialogDescription>
                  Are you sure you want to clear the chat history? This action cannot be undone.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction onClick={handleClearChat}>Clear Chat</AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
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
              <AlertDialog open={showClearDialog} onOpenChange={setShowClearDialog}>
                <AlertDialogTrigger asChild>
                  <button className="text-xs text-gray-500 hover:text-gray-700 font-work-sans underline">
                    Clear chat
                  </button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>Clear Chat History</AlertDialogTitle>
                    <AlertDialogDescription>
                      Are you sure you want to clear the chat history? This action cannot be undone.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction onClick={handleClearChat}>Clear Chat</AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            </div>
          )}
        </div>
      )}
    </div>
  );
}; 