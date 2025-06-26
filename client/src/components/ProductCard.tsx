import React from 'react';
import { Link } from 'wouter';
import { Heart, RotateCcw, Image as ImageIcon } from 'lucide-react';
import { Product } from '../types';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface ProductCardProps {
  product: Product;
}

export default function ProductCard({ product }: ProductCardProps) {
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

  return (
    <Link href={`/product/${product.id}`}>
      <Card className="bg-white rounded-xl shadow-sm hover:shadow-lg transition-shadow duration-300 overflow-hidden cursor-pointer h-full flex flex-col">
        <div className="relative">
          {renderImage()}
          {/* Fallback image (hidden by default) */}
          <div className="w-full h-48 bg-gray-100 flex items-center justify-center hidden">
            <div className="text-center">
              <ImageIcon className="w-12 h-12 text-gray-400 mx-auto mb-2" />
              <p className="text-sm text-gray-500">Image not available</p>
            </div>
          </div>
          <button className="absolute top-2 right-2 p-2 rounded-full bg-white shadow-md hover:bg-gray-50">
            <Heart className="w-4 h-4 text-gray-400" />
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
              <span className="text-sm text-gray-600 ml-2">{product.rating}</span>
              <span className="text-xs text-gray-500 ml-1">
                ({product.reviewCount && product.reviewCount > 1000 ? `${(product.reviewCount / 1000).toFixed(1)}K` : product.reviewCount})
              </span>
            </div>
          </div>
          
          <div className="space-y-1 mt-auto">
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
        </CardContent>
      </Card>
    </Link>
  );
}
