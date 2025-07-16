import React from 'react';
import { User, Bot, ShoppingCart, X, Star, Package, LogOut } from 'lucide-react';
import { Button } from '../../../../ui/Buttons/Button';
import { Badge } from '../../../../ui/Display/Badge';
import { ChatContext, ChatMessage } from '../../../../types';
import { getTransitionStyling, isTransitionMessage, formatMessageContent, extractQuickResponseTags } from "../../../../lib/utils";
import { QuickResponseButtons } from './QuickResponseButtons';

// Safe HTML renderer component
const SafeHtmlRenderer: React.FC<{ html: string; className?: string }> = ({ html, className }) => {
  const containerRef = React.useRef<HTMLDivElement>(null);
  
  React.useEffect(() => {
    if (containerRef.current) {
      // Create a temporary div to parse the HTML
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = html;
      
      // Clear the container
      containerRef.current.innerHTML = '';
      
      // Safely append the parsed content
      while (tempDiv.firstChild) {
        containerRef.current.appendChild(tempDiv.firstChild);
      }
    }
  }, [html]);
  
  return <div ref={containerRef} className={className} />;
};

interface ChatMessageItemProps {
  message: ChatMessage;
  onClearComparison: () => void;
  onExitProductChat: () => void;
  chatContext?: ChatContext;
  isMobile?: boolean;
  isStreaming?: boolean;
  showExitButton?: boolean;
  onTagClick?: (tag: string) => void;
}

export const ChatMessageItem: React.FC<ChatMessageItemProps> = ({
  message,
  onClearComparison,
  onExitProductChat,
  chatContext,
  isMobile = false,
  isStreaming = false,
  showExitButton = false,
  onTagClick,
}) => {
  const isUser = message.sender === 'user';
  const isTransition = isTransitionMessage(message);
  
  // Helper function to render star ratings
  const renderStars = (rating: number) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;
    
    for (let i = 0; i < fullStars; i++) {
      stars.push(<Star key={i} className="w-3 h-3 fill-yellow-400 text-yellow-400" />);
    }
    
    if (hasHalfStar) {
      stars.push(<Star key="half" className="w-3 h-3 fill-yellow-400 text-yellow-400 opacity-50" />);
    }
    
    const remainingStars = 5 - Math.ceil(rating);
    for (let i = 0; i < remainingStars; i++) {
      stars.push(<Star key={`empty-${i}`} className="w-3 h-3 text-gray-300" />);
    }
    
    return stars;
  };

  // Helper function to render product image
  const renderProductImage = (product: any) => {
    if (!product.image || product.image === '') {
      return (
        <div className="w-12 h-12 bg-gray-100 flex items-center justify-center rounded">
          <Package className="w-6 h-6 text-gray-400" />
        </div>
      );
    }
    
    return (
      <div className="w-12 h-12 bg-gray-50 flex items-center justify-center rounded">
        <img 
          src={product.image} 
          alt={product.title}
          className="w-10 h-10 object-cover rounded"
        />
      </div>
    );
  };

  // Handle transition messages
  if (isTransition) {
    // For comparison transition messages with product data, show enhanced display
    if (message.content.includes('Now comparing:') && message.comparisonProducts && message.comparisonProducts.length > 0) {
      return (
        <div className="flex justify-start items-start space-x-2">
          {/* Tylee Avatar */}
          <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center flex-shrink-0">
            <Bot className="w-4 h-4 text-white" />
          </div>
          
          {/* Enhanced comparison message */}
          <div className="max-w-lg bg-purple-50 border border-purple-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <ShoppingCart className="w-4 h-4 text-purple-600" />
                <span className="text-sm font-medium text-purple-700">
                  Now comparing {message.comparisonProducts.length} products
                </span>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={onClearComparison}
                className="text-purple-600 hover:text-purple-700 hover:bg-purple-100 p-1"
              >
                <X className="w-3 h-3" />
              </Button>
            </div>
            
            {/* Display products in a grid */}
            <div className="grid grid-cols-1 gap-3">
              {message.comparisonProducts.map((product, index) => (
                <div key={product.id || index} className="bg-white rounded-lg p-3 border border-purple-100">
                  <div className="flex items-center space-x-3">
                    {renderProductImage(product)}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-1">
                        <Badge variant="outline" className="text-xs font-medium text-gray-600 border-gray-300">
                          {product.brand}
                        </Badge>
                      </div>
                      <div className="text-sm font-medium text-gray-900 mb-1 line-clamp-2">
                        {product.title}
                      </div>
                      <div className="flex items-center space-x-3">
                        <span className="text-sm font-semibold text-gray-900">
                          ${product.price?.toFixed(2)}
                        </span>
                        {product.rating && (
                          <div className="flex items-center space-x-1">
                            <div className="flex">
                              {renderStars(product.rating)}
                            </div>
                            <span className="text-xs text-gray-600">
                              {product.rating.toFixed(1)}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      );
    }

    // For individual product transition messages, show enhanced display
    if (message.content.includes('Now discussing:') && message.transitionType === 'product' && (message.productData || chatContext?.product)) {
      const product = message.productData || chatContext?.product;
      
      return (
        <div className="flex justify-start items-start space-x-2">
          {/* Tylee Avatar */}
          <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center flex-shrink-0">
            <Bot className="w-4 h-4 text-white" />
          </div>
          
          {/* Enhanced product discussion message */}
          <div className="max-w-lg bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <Package className="w-4 h-4 text-green-600" />
                <span className="text-sm font-medium text-green-700">
                  Now discussing
                </span>
              </div>
            </div>
            
            {/* Display product information */}
            <div className="bg-white rounded-lg p-3 border border-green-100">
              <div className="flex items-center space-x-3">
                {renderProductImage(product)}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    <Badge variant="outline" className="text-xs font-medium text-gray-600 border-gray-300">
                      {product?.brand}
                    </Badge>
                  </div>
                  <div className="text-sm font-medium text-gray-900 mb-1 line-clamp-2">
                    {product?.title}
                  </div>
                  <div className="flex items-center space-x-3">
                    <span className="text-sm font-semibold text-gray-900">
                      ${product?.price?.toFixed(2)}
                    </span>
                    {product?.rating && (
                      <div className="flex items-center space-x-1">
                        <div className="flex">
                          {renderStars(product.rating)}
                        </div>
                        <span className="text-xs text-gray-600">
                          {product.rating.toFixed(1)}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Exit discussion button */}
            {showExitButton && (
              <div className="mt-3">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={onExitProductChat}
                  className="w-full text-green-700 hover:text-green-800 border-green-200 hover:bg-green-100"
                >
                  <LogOut className="w-3 h-3 mr-2" />
                  Exit Discussion
                </Button>
              </div>
            )}
          </div>
        </div>
      );
    }
    
    // For other transition messages, show simple display
    return (
      <div className={`px-4 py-2 rounded-lg text-sm text-center ${getTransitionStyling(message)}`}>
        {message.content}
      </div>
    );
  }

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} items-start space-x-2`}>
      {/* Tylee Avatar - only for AI messages */}
      {!isUser && (
        <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center flex-shrink-0">
          <Bot className="w-4 h-4 text-white" />
        </div>
      )}
      
      {/* Message Content */}
      <div className={`max-w-xs lg:max-w-md ${
        isUser 
          ? 'bg-chewy-blue text-white' 
          : 'bg-gray-100 text-gray-900'
      } rounded-lg overflow-hidden`}>
        
        {/* Show comparison mode indicator for messages without product data */}
        {!isUser && message.content.includes('Now comparing:') && (!message.comparisonProducts || message.comparisonProducts.length === 0) && (
          <div className="flex items-center justify-between p-2 bg-purple-50 border-b border-purple-200">
            <div className="flex items-center space-x-2">
              <ShoppingCart className="w-4 h-4 text-purple-600" />
              <span className="text-sm font-medium text-purple-700">Comparison Mode</span>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClearComparison}
              className="text-purple-600 hover:text-purple-700 hover:bg-purple-100 p-1"
            >
              <X className="w-3 h-3" />
            </Button>
          </div>
        )}
        
        {/* Display comparison products if available (for non-comparison messages) */}
        {!isUser && !message.content.includes('Now comparing:') && message.comparisonProducts && message.comparisonProducts.length > 0 && (
          <div className="p-3 border-b border-gray-200">
            <div className="text-xs font-medium text-gray-600 mb-2">Comparing Products:</div>
            <div className="space-y-2">
              {message.comparisonProducts.slice(0, 3).map((product, index) => (
                <div key={product.id || index} className="flex items-center space-x-2">
                  {renderProductImage(product)}
                  <div className="flex-1 min-w-0">
                    <div className="text-xs font-medium text-gray-900 truncate">
                      {product.brand} {product.title}
                    </div>
                    <div className="flex items-center space-x-1 mt-1">
                      <span className="text-xs font-semibold text-gray-900">
                        ${product.price?.toFixed(2)}
                      </span>
                      {product.rating && (
                        <div className="flex items-center space-x-1">
                          <div className="flex">
                            {renderStars(product.rating)}
                          </div>
                          <span className="text-xs text-gray-600">
                            {product.rating.toFixed(1)}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              {message.comparisonProducts.length > 3 && (
                <div className="text-xs text-gray-500 text-center">
                  +{message.comparisonProducts.length - 3} more products
                </div>
              )}
            </div>
          </div>
        )}
        
        {/* Message text - hide for comparison messages since we show products above */}
        <div className={`p-3 ${isUser ? 'text-white' : 'text-gray-900'}`}>
          {!message.content.includes('Now comparing:') && (
            <>
              {/* Show typing indicator for empty streaming messages */}
              {isStreaming && !message.content.trim() ? (
                <div className="flex items-center space-x-1 text-gray-500">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                  </div>
                  <span className="text-sm">Tylee is typing...</span>
                </div>
              ) : (
                <div>
                  {message.sender === 'ai' ? (
                    (() => {
                      const { cleanContent, tags } = extractQuickResponseTags(message.content);
                      
                      return (
                        <>
                          <div className="text-sm">
                            <SafeHtmlRenderer 
                              html={formatMessageContent(cleanContent)} 
                              className="prose prose-sm max-w-none"
                            />
                          </div>
                          {tags.length > 0 && onTagClick && (
                            <QuickResponseButtons 
                              tags={tags} 
                              onTagClick={onTagClick} 
                            />
                          )}
                        </>
                      );
                    })()
                  ) : (
                    <div className="text-sm">
                      {/* Display image if present */}
                      {message.imageUrl && (
                        <div className="mb-2">
                          <img 
                            src={message.imageUrl} 
                            alt="User uploaded" 
                            className="max-w-full h-auto rounded-lg border"
                            style={{ maxHeight: '200px' }}
                          />
                        </div>
                      )}
                      {message.content}
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
      
      {/* User avatar */}
      {isUser && (
        <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center flex-shrink-0">
          <User className="w-4 h-4 text-gray-600" />
        </div>
      )}
    </div>
  );
};