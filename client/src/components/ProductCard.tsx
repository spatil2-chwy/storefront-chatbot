import React from 'react';
import { Link } from 'wouter';
import { Bot, RotateCcw, Image as ImageIcon, Check, ShoppingCart, MessageSquare } from 'lucide-react';
import { Product } from '../types';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import SearchMatches from './SearchMatches';
import { useGlobalChat } from '../contexts/ChatContext';

interface ProductCardProps {
  product: Product;
}

export default function ProductCard({ product }: ProductCardProps) {
  const { 
    comparingProducts, 
    addToComparison, 
    removeFromComparison, 
    isInComparisonMode,
    setCurrentContext,
    setIsOpen,
    setShouldAutoOpen
  } = useGlobalChat();

  const isSelected = comparingProducts.some(p => p.id === product.id);

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
        <div className="w-full h-48 bg-gray-100 flex items-center justify-center">
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
        className="w-full h-48 object-cover"
        onError={(e) => {
          const target = e.target as HTMLImageElement;
          target.style.display = 'none';
          target.nextElementSibling?.classList.remove('hidden');
        }}
      />
    );
  };

  const handleCompareChange = (checked: boolean) => {
    if (checked) {
      addToComparison(product);
    } else {
      removeFromComparison(product.id!);
    }
  };

  const handleChatClick = () => {
    setCurrentContext({ type: 'product', product });
    setIsOpen(true);
    setShouldAutoOpen(true);
  };

  const handleAddToCart = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    // Add to cart functionality would go here
    console.log('Add to cart:', product.title);
  };

  // Extract categories from search matches for the new section
  const getMatchedCategories = () => {
    if (!product.search_matches) return [];
    
    const categories = new Set<string>();
    product.search_matches.forEach(match => {
      if (match.field.includes(':')) {
        const [category, value] = match.field.split(':', 2);
        categories.add(value.trim());
      } else {
        match.matched_terms.forEach(term => categories.add(term));
      }
    });
    
    return Array.from(categories);
  };

  const matchedCategories = getMatchedCategories();

  return (
    <Card className="bg-white rounded-xl shadow-sm hover:shadow-lg transition-shadow duration-300 h-full flex flex-col">
      <Link href={`/product/${product.id}`} className="flex-1 flex flex-col">
        {/* Product Image */}
        <div className="relative w-full h-48">
          {renderImage()}
          {/* Fallback image (hidden by default) */}
          <div className="w-full h-48 bg-gray-100 flex items-center justify-center hidden">
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

          {/* Categories Matched Section */}
          {matchedCategories.length > 0 && (
            <div className="mb-3">
              <div className="text-xs font-medium text-gray-700 mb-2">Categories Matched</div>
              <div className="flex flex-wrap gap-1">
                {matchedCategories.slice(0, 3).map((category, index) => (
                  <Badge
                    key={index}
                    className="text-xs px-2 py-1 bg-blue-50 text-blue-700 border border-blue-200 rounded-md"
                  >
                    {category}
                  </Badge>
                ))}
                {matchedCategories.length > 3 && (
                  <Badge className="text-xs px-2 py-1 bg-gray-50 text-gray-600 border border-gray-200 rounded-md">
                    +{matchedCategories.length - 3} more
                  </Badge>
                )}
              </div>
            </div>
          )}
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
            className="border-gray-300 w-5 h-5"
          />
          <label
            htmlFor={`compare-${product.id}`}
            className="text-sm cursor-pointer text-gray-700"
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
  );
}
