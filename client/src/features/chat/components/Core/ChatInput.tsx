import React, { useRef } from 'react';
import { Send, Paperclip, X } from 'lucide-react';
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
  onImageUpload?: (file: File) => void;
  selectedImage?: File | null;
  onImageRemove?: () => void;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  value,
  onChange,
  onSend,
  onKeyPress,
  disabled = false,
  placeholder = "Type your message...",
  isEmbedded = false,
  onImageUpload,
  selectedImage,
  onImageRemove
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const handleImageClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type.startsWith('image/')) {
      onImageUpload?.(file);
    }
    // Reset the input so the same file can be selected again
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const baseClasses = "border-t border-gray-200 p-3 flex-shrink-0 bg-white";
  const embeddedClasses = "border-t border-gray-200 p-3 flex-shrink-0 bg-white";
  const floatingClasses = "border-t border-gray-200 p-3 flex-shrink-0 bg-white rounded-b-lg";

  return (
    <div className={isEmbedded ? embeddedClasses : floatingClasses}>
      {selectedImage && (
        <div className="mb-3 flex items-center space-x-2 p-2 bg-gray-50 rounded-lg">
          <img 
            src={URL.createObjectURL(selectedImage)} 
            alt="Selected" 
            className="w-12 h-12 object-cover rounded-lg"
          />
          <span className="text-sm text-gray-600 flex-1">{selectedImage.name}</span>
          <Button
            onClick={onImageRemove}
            className="p-1 h-6 w-6 bg-gray-400 hover:bg-gray-500 text-white rounded-full flex items-center justify-center"
          >
            <X className="w-3 h-3" />
          </Button>
        </div>
      )}
      
      <div className="flex items-center space-x-2">
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept="image/*"
          className="hidden"
        />
        
        <Button
          onClick={handleImageClick}
          disabled={disabled}
          className="bg-gray-100 hover:bg-gray-200 text-gray-600 px-3 py-2 rounded-md flex items-center"
        >
          <Paperclip className="w-4 h-4" />
        </Button>
        
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
          disabled={disabled || (!value.trim() && !selectedImage)}
          className="bg-chewy-blue hover:bg-blue-700 text-white px-4 py-2 rounded-md flex items-center space-x-2"
        >
          <Send className="w-4 h-4" />
          <span>Send</span>
        </Button>
      </div>
    </div>
  );
}; 