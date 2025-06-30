import React from 'react';
import { Link } from 'wouter';
import { Bot, RotateCcw, Image as ImageIcon, Check } from 'lucide-react';
import { Product } from '../types';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
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
  const isMaxReached = comparingProducts.length >= 3 && !isSelected;
  const [showTooltip, setShowTooltip] = React.useState(false);

  // Debug: Log the should_you_buy_it field
  React.useEffect(() => {
    console.log('Product should_you_buy_it:', product.should_you_buy_it);
  }, [product.should_you_buy_it]);

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

  const handleCompareClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (isSelected) {
      console.log('Removing from comparison...');
      removeFromComparison(product.id!);
    } else if (!isMaxReached) {
      console.log('Adding to comparison...');
      addToComparison(product);
    }
  };

  const handleAIClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    // Set the product context to transition to product discussion mode
    setCurrentContext({ type: 'product', product });
    
    // Open the chat widget
    setIsOpen(true);
    setShouldAutoOpen(true);
  };

  return (
    <Link href={`/product/${product.id}`}>
      <Card className="bg-white rounded-xl shadow-sm hover:shadow-lg transition-shadow duration-300 cursor-pointer h-full flex flex-col">
        <div className="relative w-full h-48">
          {renderImage()}
          {/* Fallback image (hidden by default) */}
          <div className="w-full h-48 bg-gray-100 flex items-center justify-center hidden">
            <div className="text-center">
              <ImageIcon className="w-12 h-12 text-gray-400 mx-auto mb-2" />
              <p className="text-sm text-gray-500">Image not available</p>
            </div>
          </div>
          
          {/* Compare checkbox */}
          <div className="absolute top-2 left-2">
            <div className="flex items-center space-x-1">
              <button
                onClick={handleCompareClick}
                disabled={isMaxReached}
                className={`p-5.5 rounded transition-all duration-200 ${
                  isSelected 
                    ? 'bg-chewy-blue text-white shadow-md' 
                    : isMaxReached
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-transparent text-white hover:bg-white/20 shadow-md hover:shadow-lg'
                }`}
              >
                {isSelected ? (
                  <Check className="w-3 h-3" />
                ) : (
                  <div className="w-3 h-3 border-2 border-current rounded-sm" />
                )}
              </button>
              <Badge 
                className={`text-[9px] px-1.5 py-0.5 ${
                  isSelected 
                    ? 'bg-chewy-blue text-white' 
                    : isMaxReached
                    ? 'bg-gray-300 text-gray-500'
                    : 'bg-black/50 text-white border border-white/30'
                }`}
              >
                Compare
              </Badge>
            </div>
          </div>
          
          {/* AI insights button - always top right of image */}
          <button 
            className="absolute top-2 right-2 p-2 rounded-full bg-white shadow-md hover:bg-gray-50"
            onMouseEnter={() => setShowTooltip(true)}
            onMouseLeave={() => setShowTooltip(false)}
            onClick={handleAIClick}
          >
            <Bot className="w-4 h-4 text-gray-400" />
            {product.should_you_buy_it && showTooltip && (
              <div className="absolute right-1/2 translate-x-1/2 bottom-full mb-2 w-64 p-3 bg-gray-900 text-white text-xs rounded-lg shadow-lg z-50 flex flex-col items-center">
                <div className="whitespace-pre-line text-center">{product.should_you_buy_it}</div>
                <div className="mt-2 pt-2 border-t border-gray-700 font-medium text-center">Click to discuss</div>
                {/* Arrow */}
                <div className="w-3 h-3 bg-gray-900 rotate-45 absolute left-1/2 -bottom-1.5 -translate-x-1/2 z-50"></div>
              </div>
            )}
          </button>
        </div>
        
        <CardContent className="p-4 flex-1 flex flex-col">
          <div className="mb-2">
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
          
          <div className="space-y-1 mt-auto mb-3">
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
          
          {/* Search Matches - show which categories/fields matched at the bottom */}
          <SearchMatches 
            matches={product.search_matches} 
            className="border-t pt-2 mt-auto" 
            showTitle={false}
          />
        </CardContent>
      </Card>
    </Link>
  );
}
