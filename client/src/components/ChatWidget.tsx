import { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { chatResponses } from '@/lib/mockData';
import { ChatMessage } from '@shared/schema';

interface ChatWidgetProps {
  onProductFilter?: (keywords: string[]) => void;
  initialQuery?: string;
  shouldOpen?: boolean;
}

export default function ChatWidget({ onProductFilter, initialQuery, shouldOpen }: ChatWidgetProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLiveAgent, setIsLiveAgent] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (shouldOpen) {
      setIsOpen(true);
    }
  }, [shouldOpen]);

  useEffect(() => {
    if (initialQuery && initialQuery.trim()) {
      setInputValue(initialQuery);
      if (shouldOpen) {
        // Auto-send the query when opened from search
        setTimeout(() => {
          sendMessage(initialQuery);
        }, 500);
      }
    }
  }, [initialQuery, shouldOpen]);

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

  const sendMessage = async (messageText?: string) => {
    const messageToSend = messageText || inputValue;
    if (!messageToSend.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: messageToSend,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue(''); // Always clear input after sending
    setIsLoading(true);

    // Extract keywords for product filtering
    const keywords = extractKeywords(messageToSend);
    if (keywords.length > 0) {
      onProductFilter?.(keywords);
    }

    // Simulate AI or Live Agent response delay
    setTimeout(() => {
      const aiResponse: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: isLiveAgent 
          ? "Thanks for reaching out! A live agent will be with you shortly. In the meantime, I can help you find relevant products based on your question."
          : generateAIResponse(messageToSend),
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
        className="w-14 h-14 bg-chewy-blue hover:bg-blue-700 text-white rounded-full shadow-lg flex items-center justify-center"
        size="icon"
      >
        <MessageCircle className="w-6 h-6" />
      </Button>

      {/* Chat Modal */}
      {isOpen && (
        <Card className="absolute bottom-16 right-0 w-80 h-[450px] shadow-2xl rounded-3xl border-0">
          <CardHeader className="bg-white border-b border-gray-100 p-3 rounded-t-3xl">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-chewy-blue rounded-full flex items-center justify-center">
                  <div className="text-sm font-bold text-white">C</div>
                </div>
                <CardTitle className="text-gray-900 font-work-sans text-base">
                  {isLiveAgent ? 'Live Agent' : 'AI Beta'}
                </CardTitle>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsOpen(false)}
                className="text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-full w-7 h-7"
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
            
            {/* Toggle between AI and Live Agent */}
            <div className="flex items-center justify-center mt-2">
              <div className="flex bg-gray-100 rounded-full p-0.5">
                <button
                  onClick={() => setIsLiveAgent(false)}
                  className={`px-3 py-1.5 rounded-full text-xs font-work-sans transition-colors ${
                    !isLiveAgent 
                      ? 'bg-chewy-blue text-white' 
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                >
                  AI Chat
                </button>
                <button
                  onClick={() => setIsLiveAgent(true)}
                  className={`px-3 py-1.5 rounded-full text-xs font-work-sans transition-colors ${
                    isLiveAgent 
                      ? 'bg-chewy-blue text-white' 
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                >
                  Live Agent
                </button>
              </div>
            </div>
          </CardHeader>

          <CardContent className="flex flex-col h-80 p-0 bg-gray-50">
            {/* Messages */}
            <div className="flex-1 p-4 overflow-y-auto space-y-3 bg-white">
              {/* Initial suggestions if no messages */}
              {messages.length === 0 && (
                <div className="space-y-2">
                  <p className="text-xs text-gray-600 font-work-sans">Try asking:</p>
                  <div className="space-y-1.5">
                    <button
                      onClick={() => setInputValue("Easiest way to deal with backyard dog poop?")}
                      className="block w-full text-left text-xs text-gray-700 hover:text-chewy-blue hover:bg-gray-50 p-2 rounded-lg border border-gray-200 font-work-sans"
                    >
                      "Easiest way to deal with backyard dog poop?"
                    </button>
                    <button
                      onClick={() => setInputValue("Dog developed chicken allergy. Need protein though.")}
                      className="block w-full text-left text-xs text-gray-700 hover:text-chewy-blue hover:bg-gray-50 p-2 rounded-lg border border-gray-200 font-work-sans"
                    >
                      "Dog developed chicken allergy. Need protein though."
                    </button>
                  </div>
                </div>
              )}
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs px-3 py-2 rounded-2xl font-work-sans text-sm ${
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
                  <div className="bg-gray-100 px-3 py-2 rounded-2xl">
                    <div className="flex items-center space-x-2">
                      <div className="flex space-x-1">
                        <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-pulse"></div>
                        <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-pulse delay-150"></div>
                        <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-pulse delay-300"></div>
                      </div>
                      <span className="text-xs text-gray-500 font-work-sans">LOADING...</span>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="border-t border-gray-100 p-3 bg-white rounded-b-3xl">
              <div className="flex space-x-2">
                <Input
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="What do you want to learn?"
                  className="flex-1 rounded-full border-gray-200 font-work-sans py-2 px-3 text-sm focus:border-chewy-blue focus:ring-chewy-blue"
                />
                <Button 
                  onClick={sendMessage} 
                  size="icon" 
                  className="bg-chewy-blue hover:bg-blue-700 rounded-full w-9 h-9 flex items-center justify-center"
                >
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
