import React from 'react';
import { Send } from 'lucide-react';
import { Button } from '../../../../ui/Buttons/Button';
import { Input } from '../../../../ui/Input/Input';

interface ChatInputProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  onKeyPress: (e: React.KeyboardEvent) => void;
  disabled?: boolean;
  placeholder?: string;
  isEmbedded?: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  value,
  onChange,
  onSend,
  onKeyPress,
  disabled = false,
  placeholder = "Type your message...",
  isEmbedded = false
}) => {
  const baseClasses = "border-t border-gray-200 p-3 flex-shrink-0 bg-white";
  const embeddedClasses = "border-t border-gray-200 p-3 flex-shrink-0 bg-white";
  const floatingClasses = "border-t border-gray-200 p-3 flex-shrink-0 bg-white rounded-b-lg";

  return (
    <div className={isEmbedded ? embeddedClasses : floatingClasses}>
      <div className="flex items-center space-x-2">
        <Input
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyPress={onKeyPress}
          placeholder={placeholder}
          disabled={disabled}
          className="flex-1 border-gray-300 focus:border-chewy-blue focus:ring-chewy-blue"
        />
        <Button
          onClick={onSend}
          disabled={disabled}
          className="bg-chewy-blue hover:bg-blue-700 text-white px-4 py-2 rounded-md flex items-center space-x-2"
        >
          <Send className="w-4 h-4" />
          <span>Send</span>
        </Button>
      </div>
    </div>
  );
}; 