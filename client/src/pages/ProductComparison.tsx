import React, { useEffect } from 'react';
import { Link, useLocation } from 'wouter';
import { ArrowLeft, Package, Star } from 'lucide-react';
import Header from '@/components/Header';
import ChatWidget from '@/components/ChatWidget';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useGlobalChat } from '@/contexts/ChatContext';

export default function ProductComparison() {
  const [, setLocation] = useLocation();
  const { 
    comparingProducts, 
    currentSearchQuery,
    setCurrentContext,
    setIsOpen,
    setShouldAutoOpen,
    clearComparison
  } = useGlobalChat();

  // Auto-open chat when component mounts (context is set via ChatWidget chatContext prop)
  useEffect(() => {
    if (comparingProducts.length > 0) {
      setIsOpen(true);
      setShouldAutoOpen(true);
    }
  }, [comparingProducts, setIsOpen, setShouldAutoOpen]);

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

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <Header />
      
      <main className="max-w-full mx-auto px-8 sm:px-12 lg:px-16 py-8">
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
        <div className="grid gap-6" style={{ gridTemplateColumns: `repeat(${Math.min(comparingProducts.length, 4)}, 1fr)` }}>
          {comparingProducts.map((product) => (
            <Card key={product.id} className="bg-white rounded-xl shadow-sm h-full">
              <div className="relative">
                {/* Product Image */}
                <div className="w-full h-48 bg-gray-100 flex items-center justify-center rounded-t-xl">
                  {product.image ? (
                    <img 
                      src={product.image} 
                      alt={product.title}
                      className="w-full h-48 object-cover rounded-t-xl"
                    />
                  ) : (
                    <div className="text-center">
                      <Package className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                      <p className="text-sm text-gray-500">Image not available</p>
                    </div>
                  )}
                </div>
              </div>
              
              <CardContent className="p-4">
                {/* Product Title and Brand */}
                <div className="mb-3">
                  <div className="flex items-center space-x-2 mb-2">
                    <Badge variant="outline" className="text-xs font-medium text-gray-600 border-gray-300">
                      {product.brand}
                    </Badge>
                  </div>
                  <h3 className="text-sm font-medium text-gray-900 line-clamp-3 leading-5">
                    {product.title}
                  </h3>
                </div>

                {/* Rating */}
                <div className="flex items-center mb-3">
                  <div className="flex text-sm">
                    {renderStars(product.rating || 0)}
                  </div>
                  <span className="text-sm text-gray-600 ml-2">{product.rating?.toFixed(1)}</span>
                  <span className="text-xs text-gray-500 ml-1">
                    ({product.reviewCount && product.reviewCount > 1000 ? `${(product.reviewCount / 1000).toFixed(1)}K` : product.reviewCount})
                  </span>
                </div>

                {/* Pricing */}
                <div className="space-y-2 mb-3">
                  <div className="flex items-center space-x-2">
                    <span className="text-lg font-semibold text-gray-900">${product.price}</span>
                    {product.originalPrice && product.originalPrice > (product.price || 0) && (
                      <span className="text-sm text-gray-500 line-through">${product.originalPrice}</span>
                    )}
                  </div>
                  {(product.autoshipPrice ?? 0) > 0 && (
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-chewy-blue font-medium">${product.autoshipPrice}</span>
                      <span className="text-xs text-chewy-blue">Autoship</span>
                    </div>
                  )}
                </div>

                {/* Categories Matched */}
                {product.search_matches && product.search_matches.length > 0 && (
                  <div className="mb-3">
                    <div className="text-xs font-medium text-gray-700 mb-1">Categories Matched</div>
                    <div className="flex flex-wrap gap-1">
                      {product.search_matches.slice(0, 2).map((match, index) => {
                        const category = match.field.includes(':') 
                          ? match.field.split(':', 2)[1].trim() 
                          : match.matched_terms[0];
                        return (
                          <Badge
                            key={index}
                            className="text-xs px-1.5 py-0.5 bg-blue-50 text-blue-700 border border-blue-200 rounded-md"
                          >
                            {category}
                          </Badge>
                        );
                      })}
                      {product.search_matches.length > 2 && (
                        <Badge className="text-xs px-1.5 py-0.5 bg-gray-50 text-gray-600 border border-gray-200 rounded-md">
                          +{product.search_matches.length - 2}
                        </Badge>
                      )}
                    </div>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="space-y-2">
                  <Button className="w-full bg-chewy-blue hover:bg-blue-700 text-white rounded-lg h-9 text-sm">
                    Add to Cart
                  </Button>
                  <Link href={`/product/${product.id}`}>
                    <Button variant="outline" className="w-full border-gray-300 text-gray-700 hover:bg-gray-50 rounded-lg h-9 text-sm">
                      View Details
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Instructions */}
        <div className="mt-8 text-center">
          <p className="text-gray-600 text-sm">
            Use the chat below to ask questions about these products or get recommendations
          </p>
        </div>
      </main>

      {/* Chat Widget - positioned at bottom */}
      <ChatWidget 
        chatContext={{ type: 'comparison', products: comparingProducts }}
        onClearChat={() => {}}
      />
    </div>
  );
} 