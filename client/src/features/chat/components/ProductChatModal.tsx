import React, { useState, useRef, useEffect } from 'react';
import { X, Send, Package } from 'lucide-react';
import { Button } from '@/ui/Buttons/Button';
import { Input } from '@/ui/Input/Input';
import { Product, ChatMessage } from '../../../types';
import { api } from '@/lib/api';
import { useAuth } from '@/lib/auth';
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
} from '@/ui/Overlay/AlertDialog';

// Simple markdown to HTML converter for chat messages
const formatMessageContent = (content: string): string => {
  let formattedContent = content;
  
  // Convert **bold** to <strong>
  formattedContent = formattedContent.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  
  // Convert *italic* to <em>
  formattedContent = formattedContent.replace(/\*(.*?)\*/g, '<em>$1</em>');
  
  // Convert numbered lists (1. item) to proper HTML lists
  if (/^\d+\.\s/m.test(formattedContent)) {
    const lines = formattedContent.split('\n');
    let inList = false;
    const processedLines: string[] = [];
    
    lines.forEach(line => {
      const trimmedLine = line.trim();
      const numberListMatch = trimmedLine.match(/^(\d+)\.\s(.+)$/);
      
      if (numberListMatch) {
        if (!inList) {
          processedLines.push('<ol>');
          inList = true;
        }
        processedLines.push(`<li>${numberListMatch[2]}</li>`);
      } else if (trimmedLine.startsWith('- ')) {
        if (!inList) {
          processedLines.push('<ul>');
          inList = true;
        }
        processedLines.push(`<li>${trimmedLine.substring(2)}</li>`);
      } else {
        if (inList) {
          processedLines.push('</ol>');
          inList = false;
        }
        if (trimmedLine) {
          processedLines.push(`<p>${trimmedLine}</p>`);
        }
      }
    });
    
    if (inList) {
      processedLines.push('</ol>');
    }
    
    formattedContent = processedLines.join('');
  } else {
    // Just wrap paragraphs if no lists
    const paragraphs = formattedContent.split('\n\n');
    formattedContent = paragraphs
      .filter(p => p.trim())
      .map(p => `<p>${p.trim()}</p>`)
      .join('');
  }
  
  return formattedContent;
};

interface ProductChatModalProps {
  product: Product;
  isOpen: boolean;
  onClose: () => void;
  onHideMainChat: (hide: boolean) => void;
}

export default function ProductChatModal({ product, isOpen, onClose, onHideMainChat }: ProductChatModalProps) {
  const { user } = useAuth();
  const [inputValue, setInputValue] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showClearDialog, setShowClearDialog] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen) {
      onHideMainChat(true);
    } else {
      onHideMainChat(false);
    }
  }, [isOpen, onHideMainChat]);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  if (!isOpen) return null;

  const sendMessage = async (messageToSend: string) => {
    if (!messageToSend.trim()) return;

    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: messageToSend,
      sender: 'user',
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Get AI response for product-specific question
      const response = await api.askAboutProduct(messageToSend, product);
      const aiResponse: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: response,
        sender: 'ai',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, aiResponse]);
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: "Sorry, I'm having trouble processing your request right now. Please try again in a moment.",
        sender: 'ai',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = () => {
    if (inputValue.trim()) {
      sendMessage(inputValue.trim());
    }
  };

  const handleSampleQuestionClick = (question: string) => {
    sendMessage(question);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  const handleClose = () => {
    setMessages([]);
    setInputValue('');
    onClose();
  };

  const handleClearChat = () => {
    setMessages([]);
    setInputValue('');
    setShowClearDialog(false);
  };

  const sampleQuestions = [
    "What are the key ingredients in this product?",
    "Is this suitable for my dog's age and size?",
    "How does this compare to similar products?"
  ];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white shadow-2xl max-w-2xl w-full h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 flex-shrink-0">
          <div className="flex items-center space-x-3">
            {/* Product Image */}
            <div className="w-12 h-12 bg-gray-100 flex items-center justify-center flex-shrink-0">
              {product.image ? (
                <img 
                  src={product.image} 
                  alt={product.title}
                  className="w-10 h-10 object-cover"
                />
              ) : (
                <Package className="w-6 h-6 text-gray-400" />
              )}
            </div>
            {/* Product Details */}
            <div className="flex-1">
              <div className="text-xs text-gray-500 font-medium">{product.brand}</div>
              <h3 className="text-sm font-medium text-gray-900 line-clamp-1">
                {product.title}
              </h3>
              <div className="text-sm font-semibold text-gray-900">
                ${product.price?.toFixed(2)}
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            {/* Clear Chat Button */}
            {messages.length > 0 && (
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
            
            {/* Close Button */}
            <Button
              variant="ghost"
              size="icon"
              onClick={handleClose}
              className="text-gray-500 hover:text-gray-700"
            >
              <X className="w-5 h-5" />
            </Button>
          </div>
        </div>

        {/* Sample Questions */}
        {messages.length === 0 && (
          <div className="p-4 border-b border-gray-100 flex-shrink-0">
            <div className="space-y-2">
              {sampleQuestions.map((question, index) => (
                <button
                  key={index}
                  onClick={() => handleSampleQuestionClick(question)}
                  className="block w-full text-left text-sm text-chewy-blue bg-blue-50 border border-chewy-blue p-3 transition-colors hover:bg-blue-100"
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Messages Area */}
        <div className="flex-1 p-4 overflow-y-auto bg-gray-50">
          {messages.length === 0 ? (
            <div className="text-center text-gray-500 mt-8">
              <p>Ask a question about this product to get started</p>
            </div>
          ) : (
            <div className="space-y-3">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs px-4 py-2 text-sm ${
                      message.sender === 'user'
                        ? 'bg-chewy-blue text-white'
                        : 'bg-white text-gray-900 border border-gray-200'
                    } ${message.sender === 'ai' ? 'prose prose-sm prose-gray' : ''}`}
                                      >
                      <div 
                        dangerouslySetInnerHTML={{ 
                          __html: message.sender === 'ai' ? formatMessageContent(message.content) : message.content 
                        }} 
                      />
                    </div>
                </div>
              ))}
              
              {/* Loading indicator */}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-white px-4 py-2 border border-gray-200">
                    <div className="flex items-center space-x-2">
                      <div className="flex space-x-1">
                        <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-pulse"></div>
                        <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-pulse delay-150"></div>
                        <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-pulse delay-300"></div>
                      </div>
                      <span className="text-xs text-gray-500">LOADING...</span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Section */}
        <div className="p-4 border-t border-gray-200 bg-white flex-shrink-0">
          <div className="flex space-x-2">
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask your question here"
              className="flex-1 border-gray-200 text-sm focus:border-chewy-blue focus:ring-chewy-blue"
            />
            <Button 
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isLoading}
              size="icon" 
              className="bg-chewy-blue hover:bg-blue-700 w-10 h-10 flex items-center justify-center disabled:bg-gray-300"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
} 