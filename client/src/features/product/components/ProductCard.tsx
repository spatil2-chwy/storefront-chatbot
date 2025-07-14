import React, { useState } from 'react';
import { Link } from 'wouter';
import { Sparkles, RotateCcw, Image as ImageIcon, Check, ShoppingCart, MessageSquare, X } from 'lucide-react';
import { Product } from '../../../types';
import { Card, CardContent } from '@/ui/Cards/Card';
import { Badge } from '@/ui/Display/Badge';
import { Button } from '@/ui/Buttons/Button';
import { Checkbox } from '@/ui/Checkboxes/Checkbox';
import SearchMatches from './SearchMatches';
import { useGlobalChat } from '../../Chat/context';

interface ProductCardProps {
  product: Product;
}

export default function ProductCard({ product }: ProductCardProps) {
  const [showAISynthesisFull, setShowAISynthesisFull] = useState(false);
  const { 
    comparingProducts, 
    addToComparison, 
    removeFromComparison, 
    setCurrentContext,
    setIsOpen: setGlobalChatOpen,
    currentContext,
    addTransitionMessage
  } = useGlobalChat();

  const isSelected = comparingProducts.some(p => p.id === product.id);
  const isComparisonFull = comparingProducts.length >= 4 && !isSelected;

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

  const renderImage = () => {
    if (!product.image || product.image === '') {
      return (
        <div className="w-full h-48 bg-gray-50 flex items-center justify-center">
          <div className="text-center">
            <ImageIcon className="w-12 h-12 text-gray-400 mx-auto mb-2" />
            <p className="text-sm text-gray-500">Image not available</p>
          </div>
        </div>
      );
    }

    return (
      <div className="w-full h-48 bg-gray-50 flex items-center justify-center relative">
        <img 
          src={product.image} 
          alt={product.title}
          className="max-w-full max-h-full object-contain"
          onError={(e) => {
            const target = e.target as HTMLImageElement;
            target.style.display = 'none';
            const fallback = target.parentElement?.querySelector('.image-fallback');
            if (fallback) {
              fallback.classList.remove('hidden');
            }
          }}
        />
        {/* Fallback image placeholder */}
        <div className="image-fallback hidden absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <ImageIcon className="w-12 h-12 text-gray-400 mx-auto mb-2" />
            <p className="text-sm text-gray-500">Image not available</p>
          </div>
        </div>
      </div>
    );
  };

  const handleCompareChange = (checked: boolean) => {
    if (checked) {
      addToComparison(product);
    } else {
      removeFromComparison(product.id!);
    }
  };

  const handleChatClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    // Set product context and open side chat instead of modal
    const newContext = { type: 'product' as const, product: product };
    
    // Add transition message to show "Now Discussing" if context is changing
    if (currentContext.type !== 'product' || currentContext.product?.id !== product.id) {
      addTransitionMessage(currentContext, newContext);
    }
    
    setCurrentContext(newContext);
    setGlobalChatOpen(true);
  };



  const handleAddToCart = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    // Add to cart functionality would go here
    console.log('Add to cart:', product.title);
  };

  // Extract categories from search matches for the new section
  const getMatchedCategories = () => {
    if (!product.search_matches) {
      console.log('No search matches found for product:', product.id);
      return [];
    }
    
    console.log('Search matches for product:', product.id, product.search_matches);
    
    const categories = new Set<string>();
    product.search_matches.forEach(match => {
      console.log('Processing match:', match);
      if (match.field.includes(':')) {
        const [category, value] = match.field.split(':', 2);
        console.log('Split field:', category, value);
        categories.add(value.trim());
      } else {
        console.log('No colon in field, using matched_terms:', match.matched_terms);
        match.matched_terms.forEach(term => categories.add(term));
      }
    });
    
    const result = Array.from(categories);
    console.log('Final categories for product:', product.id, result);
    return result;
  };

  const matchedCategories = getMatchedCategories();

  return (
    <>
      <Card className="bg-white rounded-xl shadow-sm hover:shadow-lg transition-shadow duration-300 h-full flex flex-col relative">
        <Link href={`/product/${product.id}`} className="flex-1 flex flex-col">
          {/* Product Image */}
          <div className="relative w-full h-48 bg-gray-50">
            {renderImage()}
          </div>
          
          <CardContent className="p-4 flex-1 flex flex-col">
            {/* Original Product Information */}
            <div className="mb-2 flex-shrink-0">
              <h4 className="line-clamp-3 text-sm h-16 leading-5 font-normal">
                <span className="font-bold text-[13px] mr-1 align-middle">{product.brand}</span>
                <span className="text-[13px] align-middle">{product.title}</span>
              </h4>
            </div>
            
            <div className="flex items-center mb-2 flex-shrink-0 h-5">
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
            
            <div className="space-y-1 mb-2 flex-shrink-0 min-h-[2.5rem]">
              <div className="flex items-center space-x-2">
                <span className="text-lg font-semibold text-gray-900">${product.price?.toFixed(2)}</span>
                {product.originalPrice && product.originalPrice > (product.price || 0) && (
                  <span className="text-sm text-gray-500 line-through">${product.originalPrice.toFixed(2)}</span>
                )}
              </div>
              {(product.autoshipPrice ?? 0) > 0 && (
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-chewy-blue font-medium">${(product.autoshipPrice ?? 0).toFixed(2)}</span>
                  <div className="flex items-center space-x-1">
                    <RotateCcw className="w-3 h-3 text-chewy-blue" />
                    <span className="text-xs text-chewy-blue font-medium">Autoship</span>
                  </div>
                </div>
              )}
            </div>

            {/* Categories Matched Section - Fixed height container */}
            <div className="mb-2 flex-shrink-0 min-h-[3rem]">
              {matchedCategories.length > 0 && (
                <>
                  <div className="text-xs font-medium text-gray-700 mb-1">Categories Matched</div>
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
                </>
              )}
            </div>

            {/* AI Synthesis Section - Aligned at top */}
            {product.should_you_buy_it && (
              <div className="mb-2 flex-shrink-0">
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 relative">
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 mt-0.5">
                      <Sparkles className="w-4 h-4 text-gray-500" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <h3 className="text-xs font-semibold text-gray-900">Should you buy it?</h3>
                      </div>
                      <div className="text-gray-700 text-xs leading-relaxed">
                        <div className="line-clamp-2">
                          {product.should_you_buy_it}
                        </div>
                        {product.should_you_buy_it && product.should_you_buy_it.length > 80 && (
                          <div className="relative">
                            <span
                              onMouseEnter={() => setShowAISynthesisFull(true)}
                              onMouseLeave={() => setShowAISynthesisFull(false)}
                              className="text-blue-600 hover:text-blue-800 text-xs font-medium mt-1 underline cursor-pointer transition-colors duration-200"
                            >
                              Show More
                            </span>
                            
                            {/* Hover tooltip with full review */}
                            {showAISynthesisFull && (
                              <div className="absolute bottom-full left-0 mb-2 w-80 bg-white rounded-lg shadow-xl border border-gray-200 p-4 z-50">
                                <div className="flex items-start space-x-2 mb-2">
                                  <div className="flex-shrink-0 mt-0.5">
                                    <Sparkles className="w-4 h-4 text-gray-500" />
                                  </div>
                                  <h3 className="text-sm font-semibold text-gray-900">Should you buy it?</h3>
                                </div>
                                <div className="text-gray-700 text-xs leading-relaxed">
                                  {product.should_you_buy_it}
                                </div>
                                {/* Arrow pointing down to the button */}
                                <div className="absolute top-full left-4 w-0 h-0 border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-white"></div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            {/* Spacer to push bottom content down */}
            <div className="flex-1"></div>
          </CardContent>
        </Link>

        {/* Add to Cart Button */}
        <div className="px-4 pb-3">
          <Button
            onClick={handleAddToCart}
            className="w-full bg-chewy-blue hover:bg-blue-700 text-white rounded-lg h-10 flex items-center justify-center space-x-2"
          >
            <ShoppingCart className="w-4 h-4" />
            <span>Add to Cart</span>
          </Button>
        </div>

        {/* Bottom Controls */}
        <div className="px-4 pb-4 flex items-center justify-between">
          {/* Compare Checkbox */}
          <div className="flex items-center space-x-2">
            <Checkbox
              id={`compare-${product.id}`}
              checked={isSelected}
              onCheckedChange={handleCompareChange}
              disabled={isComparisonFull}
              className="border-gray-300 w-5 h-5"
              title={isComparisonFull ? "Maximum 4 products can be compared" : ""}
            />
            <label
              htmlFor={`compare-${product.id}`}
              className={`text-sm cursor-pointer ${isComparisonFull ? 'text-gray-400' : 'text-gray-700'}`}
              title={isComparisonFull ? "Maximum 4 products can be compared" : ""}
            >
              Compare
            </label>
          </div>

          {/* Chat Button */}
          <Button
            onClick={handleChatClick}
            variant="ghost"
            size="sm"
            className="text-gray-600 hover:text-chewy-blue hover:bg-blue-50 p-2 h-auto"
          >
            <MessageSquare className="!w-8 !h-8 stroke-gray-300 stroke-1" />
            <span className="text-sm">Chat</span>
          </Button>
        </div>


      </Card>
    </>
  );
}
