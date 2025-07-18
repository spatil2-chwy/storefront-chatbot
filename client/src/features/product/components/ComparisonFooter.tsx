import React from 'react';
import { useLocation } from 'wouter';
import { X, Package, ArrowRight } from 'lucide-react';
import { Button } from '@/ui/Buttons/Button';
import { Product } from '../../../types';
import { useGlobalChat } from '../../Chat/context';

export default function ComparisonFooter() {
  const [, setLocation] = useLocation();
  const { 
    comparingProducts, 
    removeFromComparison, 
    clearComparison,
    isOpen: isChatOpen
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

  // Create array of 4 slots, filling with products and empty slots
  const slots = Array.from({ length: 4 }, (_, index) => {
    return comparingProducts[index] || null;
  });

  // Adjust positioning when sidebar is open
  const footerClasses = `fixed bottom-0 left-0 bg-white border-t-2 border-gray-200 shadow-lg z-40 p-4 transition-all duration-300 ${
    isChatOpen 
      ? 'right-0 md:right-[420px] lg:right-[450px] xl:right-[480px]' // Account for moderately wider sidebar width on different screen sizes
      : 'right-0'
  }`;

  return (
    <div className={footerClasses}>
      <div className="max-w-full mx-auto px-8 sm:px-12 lg:px-16">
        <div className="flex items-center justify-between">
          {/* Product Slots */}
          <div className="flex items-center space-x-3 flex-1">
            {slots.map((product, index) => (
              <div key={index} className="flex-1 max-w-xs">
                {product ? (
                  // Filled slot
                  <div className="relative">
                    <div className="bg-gray-50 rounded-lg p-3 border border-gray-200 h-20">
                      {/* Remove button */}
                      <button
                        onClick={() => handleRemoveProduct(product.id!)}
                        className="absolute -top-2 -right-2 bg-chewy-blue text-white rounded-full w-5 h-5 flex items-center justify-center hover:bg-blue-700 transition-colors"
                      >
                        <X className="w-3 h-3" />
                      </button>
                      
                      {/* Product content - image left, title right */}
                      <div className="flex items-center space-x-3 h-full">
                        {/* Product Image */}
                        <div className="w-12 h-12 bg-white rounded border border-gray-100 flex items-center justify-center flex-shrink-0">
                          {product.image ? (
                            <img 
                              src={product.image} 
                              alt={product.title}
                              className="w-10 h-10 object-cover rounded"
                            />
                          ) : (
                            <Package className="w-5 h-5 text-gray-400" />
                          )}
                        </div>
                        
                        {/* Product Title */}
                        <p className="text-xs text-gray-700 line-clamp-3 leading-tight flex-1">
                          {product.title}
                        </p>
                      </div>
                    </div>
                  </div>
                ) : (
                  // Empty slot
                  <div className="bg-gray-50 rounded-lg border-2 border-dashed border-gray-300 h-20 flex items-center justify-center">
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Compare Button */}
          <div className="flex items-center space-x-3 ml-6">
            <span className="text-sm text-gray-600">
              {comparingProducts.length} of 4 selected
            </span>
            <Button
              onClick={handleCompare}
              disabled={comparingProducts.length < 2}
              className="bg-chewy-blue hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white px-6 py-2 rounded-lg flex items-center space-x-2"
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