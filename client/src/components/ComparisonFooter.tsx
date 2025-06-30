import React from 'react';
import { useLocation } from 'wouter';
import { X, Package, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Product } from '../types';
import { useGlobalChat } from '../contexts/ChatContext';

export default function ComparisonFooter() {
  const [, setLocation] = useLocation();
  const { 
    comparingProducts, 
    removeFromComparison, 
    clearComparison
  } = useGlobalChat();

  // Don't render if no products
  if (comparingProducts.length < 1) {
    return null;
  }

  const handleCompare = () => {
    // Navigate to comparison page
    setLocation('/compare');
  };

  const handleRemoveProduct = (productId: number) => {
    removeFromComparison(productId);
  };

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t-2 border-gray-200 shadow-lg z-40 p-4">
      <div className="max-w-full mx-auto px-8 sm:px-12 lg:px-16">
        <div className="flex items-center justify-between">
          {/* Product List */}
          <div className="flex items-center space-x-4 flex-1 overflow-x-auto">
            {comparingProducts.map((product) => (
              <div key={product.id} className="relative flex-shrink-0">
                <div className="bg-gray-50 rounded-lg p-3 border border-gray-200 w-32">
                  {/* Remove button */}
                  <button
                    onClick={() => handleRemoveProduct(product.id!)}
                    className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center hover:bg-red-600 transition-colors"
                  >
                    <X className="w-3 h-3" />
                  </button>
                  
                  {/* Product Image */}
                  <div className="w-full h-16 bg-white rounded border border-gray-100 flex items-center justify-center mb-2">
                    {product.image ? (
                      <img 
                        src={product.image} 
                        alt={product.title}
                        className="w-12 h-12 object-cover rounded"
                      />
                    ) : (
                      <Package className="w-6 h-6 text-gray-400" />
                    )}
                  </div>
                  
                  {/* Product Title */}
                  <p className="text-xs text-gray-700 text-center line-clamp-2 leading-tight">
                    {product.title}
                  </p>
                </div>
              </div>
            ))}
          </div>

          {/* Compare Button */}
          <div className="flex items-center space-x-3 ml-4">
            <span className="text-sm text-gray-600">
              {comparingProducts.length} product{comparingProducts.length !== 1 ? 's' : ''} selected
            </span>
            <Button
              onClick={handleCompare}
              className="bg-chewy-blue hover:bg-blue-700 text-white px-6 py-2 rounded-lg flex items-center space-x-2"
            >
              <span>Compare</span>
              <ArrowRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
} 