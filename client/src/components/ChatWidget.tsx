import { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { chatResponses } from '@/lib/mockData';
import { ChatMessage } from '@shared/schema';

interface ChatWidgetProps {
  onProductFilter?: (keywords: string[]) => void;
}

export default function ChatWidget({ onProductFilter }: ChatWidgetProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const generateAIResponse = (userMessage: string): string => {
    const lowerMessage = userMessage.toLowerCase();
    
    if (lowerMessage.includes('train') || lowerMessage.includes('puppy') || lowerMessage.includes('biting')) {
      return "For training puppies, I recommend starting with positive reinforcement and high-value treats. Redirect biting to appropriate chew toys and be consistent with commands. Would you like me to show you some training treat options?";
    }
    
    if (lowerMessage.includes('grain-free') || lowerMessage.includes('grain free')) {
      return "Grain-free diets can be beneficial for dogs with sensitivities. Let me filter the products to show you our best grain-free options.";
    }
    
    if (lowerMessage.includes('dental') || lowerMessage.includes('teeth') || lowerMessage.includes('chew')) {
      return "Dental health is so important! I can show you some great dental chews and toys that help maintain oral hygiene.";
    }
    
    if (lowerMessage.includes('senior') || lowerMessage.includes('old') || lowerMessage.includes('elderly')) {
      return "Senior dogs have special nutritional needs. Would you like me to show you some senior-specific formulas?";
    }
    
    return chatResponses[Math.floor(Math.random() * chatResponses.length)];
  };

  const extractKeywords = (message: string): string[] => {
    const keywords: string[] = [];
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('grain-free') || lowerMessage.includes('grain free')) {
      keywords.push('grain-free');
    }
    if (lowerMessage.includes('treats') || lowerMessage.includes('training')) {
      keywords.push('treats');
    }
    if (lowerMessage.includes('dental') || lowerMessage.includes('chew')) {
      keywords.push('dental');
    }
    if (lowerMessage.includes('salmon')) {
      keywords.push('salmon');
    }
    if (lowerMessage.includes('chicken')) {
      keywords.push('chicken');
    }
    if (lowerMessage.includes('beef')) {
      keywords.push('beef');
    }
    
    return keywords;
  };

  const sendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: inputValue,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    // Extract keywords for product filtering
    const keywords = extractKeywords(inputValue);
    if (keywords.length > 0) {
      onProductFilter?.(keywords);
    }

    // Simulate AI response delay
    setTimeout(() => {
      const aiResponse: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: generateAIResponse(inputValue),
        sender: 'ai',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, aiResponse]);
      setIsLoading(false);
    }, 1500);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {/* Chat Button */}
      <Button
        onClick={() => setIsOpen(!isOpen)}
        className="w-14 h-14 bg-chewy-blue hover:bg-blue-700 text-white rounded-full shadow-lg"
        size="icon"
      >
        <MessageCircle className="w-6 h-6" />
      </Button>

      {/* Chat Modal */}
      {isOpen && (
        <Card className="absolute bottom-16 right-0 w-96 h-96 shadow-2xl">
          <CardHeader className="bg-chewy-blue text-white p-4 flex flex-row items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center">
                <div className="w-4 h-4 bg-chewy-blue rounded-full"></div>
              </div>
              <CardTitle className="text-white">AI Beta</CardTitle>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsOpen(false)}
              className="text-white hover:text-gray-200 hover:bg-blue-600"
            >
              <X className="w-4 h-4" />
            </Button>
          </CardHeader>

          <CardContent className="flex flex-col h-80 p-0">
            {/* Messages */}
            <div className="flex-1 p-4 overflow-y-auto space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs px-4 py-2 rounded-lg ${
                      message.sender === 'user'
                        ? 'bg-chewy-blue text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    {message.content}
                  </div>
                </div>
              ))}

              {/* Loading indicator */}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 px-4 py-2 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse delay-150"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse delay-300"></div>
                      </div>
                      <span className="text-sm text-gray-500">LOADING...</span>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="border-t p-4">
              <div className="flex space-x-2">
                <Input
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="What do you want to learn?"
                  className="flex-1"
                />
                <Button onClick={sendMessage} size="icon" className="bg-chewy-blue hover:bg-blue-700">
                  <Send className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
