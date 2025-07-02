import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'wouter';
import { ArrowLeft, Package, Star, RotateCcw, Image as ImageIcon, ShoppingCart, Bot, X } from 'lucide-react';
import Header from '@/components/Header';
import ChatWidget from '@/components/ChatWidget';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useGlobalChat } from '@/contexts/ChatContext';

export default function ProductComparison() {
  const [, setLocation] = useLocation();
  const [showAIOverview, setShowAIOverview] = useState<{show: boolean, product: any, position?: { top: number; left: number }}>({show: false, product: null});
  const { 
    comparingProducts, 
    currentSearchQuery,
    currentContext,
    setCurrentContext,
    setIsOpen,
    setShouldAutoOpen,
    clearComparison,
    addTransitionMessage
  } = useGlobalChat();

  // Auto-open chat when component mounts and set comparison context
  useEffect(() => {
    if (comparingProducts.length > 0) {
      const previousContext = currentContext;
      const newContext = { type: 'comparison' as const, products: comparingProducts };
      
      // Add transition message if context is changing
      if (previousContext.type !== 'comparison' || 
          !previousContext.products || 
          previousContext.products.length !== comparingProducts.length) {
        addTransitionMessage(previousContext, newContext);
      }
      
      setCurrentContext(newContext);
      setIsOpen(true);
      setShouldAutoOpen(true);
    }
  }, [comparingProducts, setIsOpen, setShouldAutoOpen, setCurrentContext, addTransitionMessage, currentContext]);

  // Redirect back if no products to compare
  useEffect(() => {
    if (comparingProducts.length === 0) {
      setLocation('/');
    }
  }, [comparingProducts.length, setLocation]);

  const handleExitComparison = () => {
    clearComparison();
    setCurrentContext({ type: 'general' });
    setLocation('/');
  };

  const renderStars = (rating: number) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;
    
    for (let i = 0; i < fullStars; i++) {
      stars.push(<span key={i} className="text-yellow-400">★</span>);
    }
    
    if (hasHalfStar) {
      stars.push(<span key="half" className="text-yellow-400">☆</span>);
    }
    
    const remainingStars = 5 - Math.ceil(rating);
    for (let i = 0; i < remainingStars; i++) {
      stars.push(<span key={`empty-${i}`} className="text-gray-300">☆</span>);
    }
    
    return stars;
  };

  const renderImage = (product: any) => {
    if (!product.image || product.image === '') {
      return (
        <div className="w-full h-32 bg-gray-100 flex items-center justify-center">
          <div className="text-center">
            <ImageIcon className="w-12 h-12 text-gray-400 mx-auto mb-2" />
            <p className="text-sm text-gray-500">Image not available</p>
          </div>
        </div>
      );
    }

    return (
      <img 
        src={product.image} 
        alt={product.title}
        className="w-full h-32 object-cover"
        onError={(e) => {
          const target = e.target as HTMLImageElement;
          target.style.display = 'none';
          target.nextElementSibling?.classList.remove('hidden');
        }}
      />
    );
  };

  // Extract categories from search matches for each product
  const getMatchedCategories = (product: any) => {
    if (!product.search_matches) return [];
    
    const categories = new Set<string>();
    product.search_matches.forEach((match: any) => {
      if (match.field.includes(':')) {
        const [category, value] = match.field.split(':', 2);
        categories.add(value.trim());
      } else {
        match.matched_terms.forEach((term: string) => categories.add(term));
      }
    });
    
    return Array.from(categories);
  };

  const handleAddToCart = (product: any) => {
    console.log('Add to cart:', product.title);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header />
      
      {/* Should You Buy It AI Overview Tooltip */}
      {showAIOverview.show && showAIOverview.product && showAIOverview.product.should_you_buy_it && (
        <div className="fixed z-50" style={{
          top: `${showAIOverview.position?.top || 0}px`,
          left: `${showAIOverview.position?.left || 0}px`
        }}>
          <div 
            className="absolute bottom-full right-0 mb-2 w-80 bg-white rounded-lg shadow-xl border border-gray-200 p-4"
            onMouseEnter={() => setShowAIOverview({show: true, product: showAIOverview.product})}
            onMouseLeave={() => setShowAIOverview({show: false, product: null})}
          >
            <div className="flex items-center space-x-2 mb-3">
              <div className="w-6 h-6 bg-chewy-blue rounded-full flex items-center justify-center">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <h3 className="text-sm font-semibold text-gray-900">Should You Buy It?</h3>
            </div>
            <div className="text-gray-700 text-xs leading-relaxed mb-2">
              <div className="font-medium text-gray-900 mb-1 text-xs">
                {showAIOverview.product.brand} {showAIOverview.product.title}
              </div>
              {showAIOverview.product.should_you_buy_it}
            </div>
            {/* Arrow pointing down to the button */}
            <div className="absolute top-full right-4 w-0 h-0 border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-white"></div>
          </div>
        </div>
      )}
      
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header with Exit Button */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-4">
            <Button
              onClick={handleExitComparison}
              variant="ghost"
              className="flex items-center space-x-2 text-chewy-blue hover:text-blue-700 hover:bg-blue-50"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back to search results</span>
              {currentSearchQuery && <span className="text-gray-500">for "{currentSearchQuery}"</span>}
            </Button>
          </div>
          
          <div className="text-right">
            <h1 className="text-2xl font-bold text-gray-900">
              Product Comparison
            </h1>
            <p className="text-sm text-gray-600 mt-1">
              Comparing {comparingProducts.length} product{comparingProducts.length !== 1 ? 's' : ''}
            </p>
          </div>
        </div>

        {/* Product Comparison Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 mb-6">
          {comparingProducts.map((product) => {
            const matchedCategories = getMatchedCategories(product);
            
            return (
              <Card key={product.id} className="bg-white rounded-xl shadow-sm hover:shadow-lg transition-shadow duration-300 h-full flex flex-col relative">
                <Link href={`/product/${product.id}`} className="flex-1 flex flex-col">
                  {/* Product Image */}
                  <div className="relative w-full h-32">
                    {renderImage(product)}
                    {/* Fallback image (hidden by default) */}
                    <div className="w-full h-32 bg-gray-100 flex items-center justify-center hidden">
                      <div className="text-center">
                        <ImageIcon className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                        <p className="text-sm text-gray-500">Image not available</p>
                      </div>
                    </div>
                  </div>
                  
                  <CardContent className="p-4 flex-1 flex flex-col">
                    {/* Original Product Information */}
                    <div className="mb-3">
                      <h4 className="line-clamp-4 text-sm h-15 leading-5 font-normal">
                        <span className="font-bold text-[13px] mr-1 align-middle">{product.brand}</span>
                        <span className="text-[13px] align-middle">{product.title}</span>
                      </h4>
                    </div>
                    
                    <div className="flex items-center mb-2">
                      <div className="flex items-center">
                        <div className="flex text-sm">
                          {renderStars(product.rating || 0)}
                        </div>
                        <span className="text-sm text-gray-600 ml-2">{product.rating?.toFixed(1)}</span>
                        <span className="text-xs text-gray-500 ml-1">
                          ({product.reviewCount && product.reviewCount > 1000 ? `${(product.reviewCount / 1000).toFixed(1)}K` : product.reviewCount})
                        </span>
                      </div>
                    </div>
                    
                    <div className="space-y-1 mb-3">
                      <div className="flex items-center space-x-2">
                        <span className="text-lg font-semibold text-gray-900">${product.price}</span>
                        {product.originalPrice && product.originalPrice > (product.price || 0) && (
                          <span className="text-sm text-gray-500 line-through">${product.originalPrice}</span>
                        )}
                      </div>
                      {(product.autoshipPrice ?? 0) > 0 && (
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-chewy-blue font-medium">${product.autoshipPrice}</span>
                          <div className="flex items-center space-x-1">
                            <RotateCcw className="w-3 h-3 text-chewy-blue" />
                            <span className="text-xs text-chewy-blue font-medium">Autoship</span>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Categories Matched Section - Show limited categories */}
                    {matchedCategories.length > 0 && (
                      <div className="mb-3">
                        <div className="text-xs font-medium text-gray-700 mb-2">Categories Matched</div>
                        <div className="flex flex-wrap gap-1">
                          {matchedCategories.map((category, index) => (
                            <Badge
                              key={index}
                              className="text-xs px-2 py-1 bg-blue-50 text-blue-700 border border-blue-200 rounded-md"
                            >
                              {category}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Link>

                {/* Should You Buy It Button - Top right corner */}
                {product.should_you_buy_it && (
                  <div className="absolute top-2 right-2">
                    <button
                      onMouseEnter={(e) => {
                        const rect = e.currentTarget.getBoundingClientRect();
                        setShowAIOverview({
                          show: true, 
                          product,
                          position: { top: rect.top, left: rect.left }
                        });
                      }}
                      onMouseLeave={() => setShowAIOverview({show: false, product: null})}
                      className="w-8 h-8 bg-black hover:bg-gray-800 text-white rounded-full flex items-center justify-center shadow-lg z-10 relative"
                      title="Should You Buy It?"
                    >
                      <Bot className="w-4 h-4" />
                    </button>
                  </div>
                )}

                {/* Add to Cart Button */}
                <div className="px-4 pb-3">
                  <Button
                    onClick={() => handleAddToCart(product)}
                    className="w-full bg-chewy-blue hover:bg-blue-700 text-white rounded-lg h-10 flex items-center justify-center space-x-2"
                  >
                    <ShoppingCart className="w-4 h-4" />
                    <span>Add to Cart</span>
                  </Button>
                </div>

                {/* Bottom Controls - View Details button only */}
                <div className="px-4 pb-4">
                  <Link href={`/product/${product.id}`}>
                    <Button variant="outline" className="w-full border-gray-300 text-gray-700 hover:bg-gray-50 rounded-lg h-9 text-sm">
                      View Details
                    </Button>
                  </Link>
                </div>
              </Card>
            );
          })}
        </div>

        {/* Chat Widget - positioned higher up */}
        <div className="h-72 border border-gray-200 bg-white">
          <ChatWidget 
            chatContext={{ type: 'comparison', products: comparingProducts }}
            onClearChat={() => {}}
          />
        </div>
      </main>
    </div>
  );
} 