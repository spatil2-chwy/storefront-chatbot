import React from 'react';
import { Button } from '../../../../ui/Buttons/Button';
import { Bot } from 'lucide-react';

interface ChatSuggestionsProps {
  onSuggestionClick: (suggestion: string) => void;
}

export const ChatSuggestions: React.FC<ChatSuggestionsProps> = ({ onSuggestionClick }) => {
  const suggestions = [
    "What's the best food for puppies?",
    "I need help choosing a cat toy",
    "Compare dry vs wet dog food",
    "What supplies do I need for a new kitten?",
    "Show me dog beds for large breeds"
  ];

  return (
    <div className="text-center space-y-4">
      <div className="flex flex-col items-center space-y-2">
        <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
          <Bot className="w-6 h-6 text-white" />
        </div>
        <div>
          <h3 className="font-semibold text-gray-900">How can I help you today?</h3>
          <p className="text-sm text-gray-600">Try one of these suggestions or ask your own question</p>
        </div>
      </div>
      
      <div className="flex flex-wrap gap-2 justify-center">
        {suggestions.map((suggestion, index) => (
          <Button
            key={index}
            variant="outline"
            size="sm"
            onClick={() => onSuggestionClick(suggestion)}
            className="bg-gradient-to-r from-gray-50 to-blue-50 hover:from-gray-100 hover:to-blue-100 border-gray-200 hover:border-blue-300 text-gray-700 hover:text-blue-700 px-4 py-2 text-sm font-medium rounded-full transition-all duration-200 shadow-sm hover:shadow-md transform hover:scale-105"
          >
            {suggestion}
          </Button>
        ))}
      </div>
    </div>
  );
}; 