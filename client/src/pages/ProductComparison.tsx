import React, { useEffect, useState, useRef } from 'react';
import { Link, useLocation } from 'wouter';
import { ArrowLeft, Package, Sparkles, RotateCcw, Image as ImageIcon, ShoppingCart, X } from 'lucide-react';
import Header from '@/layout/Header';
import ChatWidget from '@/features/Chat/components/ChatWidget';
import { Button } from '@/ui/Buttons/Button';
import { Card, CardContent } from '@/ui/Cards/Card';
import { Badge } from '@/ui/Display/Badge';
import { useGlobalChat } from '@/features/Chat/context';

export default function ProductComparison() {
  const [, setLocation] = useLocation();
  const [showAIOverview, setShowAIOverview] = useState<{show: boolean, product: any, position?: { top: number; left: number }}>({show: false, product: null});
  const [expandedIngredients, setExpandedIngredients] = useState<{[key: number]: boolean}>({});
  const contextInitialized = useRef(false);
  const { 
    comparingProducts, 
    currentSearchQuery,
    currentContext,
    setCurrentContext,
    setIsOpen,
    setShouldAutoOpen,
    clearComparison,
    addTransitionMessage,
    isOpen: isChatSidebarOpen
  } = useGlobalChat();

  // Auto-open chat when component mounts and set comparison context
  useEffect(() => {
    if (comparingProducts.length > 0 && !contextInitialized.current) {
      const newContext = { type: 'comparison' as const, products: comparingProducts };
      
      // Add transition message if context is changing (only when increasing products or first time)
      if (currentContext.type !== 'comparison' || 
          !currentContext.products || 
          currentContext.products.length < comparingProducts.length) {
        addTransitionMessage(currentContext, newContext);
      }
      
      setCurrentContext(newContext);
      setIsOpen(true);
      setShouldAutoOpen(true);
      
      contextInitialized.current = true;
    }
  }, [comparingProducts, currentContext, setIsOpen, setShouldAutoOpen, setCurrentContext, addTransitionMessage]);

  const handleExitComparison = () => {
    clearComparison();
    // Always go back to the main product listing page (which is at root "/")
    setLocation('/');
  };

  const toggleIngredients = (productId: number) => {
    setExpandedIngredients(prev => ({
      ...prev,
      [productId]: !prev[productId]
    }));
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
      <div className="w-full h-32 bg-gray-50 flex items-center justify-center relative">
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

  // Helper functions to extract comparison data from available fields
  const getHealthFeature = (product: any) => {
    if (!product.keywords) return null;
    const healthKeywords = product.keywords.filter((keyword: string) => 
      keyword.toLowerCase().includes('health') || 
      keyword.toLowerCase().includes('vitamin') ||
      keyword.toLowerCase().includes('supplement') ||
      keyword.toLowerCase().includes('probiotic') ||
      keyword.toLowerCase().includes('digestive') ||
      keyword.toLowerCase().includes('joint') ||
      keyword.toLowerCase().includes('dental')
    );
    return healthKeywords.length > 0 ? healthKeywords.join(', ') : null;
  };

  const getSpecialDiet = (product: any) => {
    if (!product.keywords) return null;
    const dietKeywords = product.keywords.filter((keyword: string) => 
      keyword.toLowerCase().includes('grain') ||
      keyword.toLowerCase().includes('free') ||
      keyword.toLowerCase().includes('organic') ||
      keyword.toLowerCase().includes('natural') ||
      keyword.toLowerCase().includes('limited') ||
      keyword.toLowerCase().includes('sensitive') ||
      keyword.toLowerCase().includes('allergy') ||
      keyword.toLowerCase().includes('hypoallergenic')
    );
    return dietKeywords.length > 0 ? dietKeywords.join(', ') : null;
  };

  const getFlavor = (product: any) => {
    // Check keywords first
    if (product.keywords) {
      const flavorKeywords = product.keywords.filter((keyword: string) => 
        keyword.toLowerCase().includes('chicken') ||
        keyword.toLowerCase().includes('beef') ||
        keyword.toLowerCase().includes('salmon') ||
        keyword.toLowerCase().includes('turkey') ||
        keyword.toLowerCase().includes('duck') ||
        keyword.toLowerCase().includes('lamb') ||
        keyword.toLowerCase().includes('fish') ||
        keyword.toLowerCase().includes('pork') ||
        keyword.toLowerCase().includes('venison')
      );
      if (flavorKeywords.length > 0) return flavorKeywords.join(', ');
    }
    
    // Check title for flavor information
    if (product.title) {
      const title = product.title.toLowerCase();
      const flavors = ['chicken', 'beef', 'salmon', 'turkey', 'duck', 'lamb', 'fish', 'pork', 'venison'];
      const foundFlavors = flavors.filter(flavor => title.includes(flavor));
      if (foundFlavors.length > 0) return foundFlavors.join(', ');
    }
    
    return null;
  };

  const getBreedSize = (product: any) => {
    // Check keywords first
    if (product.keywords) {
      const sizeKeywords = product.keywords.filter((keyword: string) => 
        keyword.toLowerCase().includes('small') ||
        keyword.toLowerCase().includes('medium') ||
        keyword.toLowerCase().includes('large') ||
        keyword.toLowerCase().includes('puppy') ||
        keyword.toLowerCase().includes('adult') ||
        keyword.toLowerCase().includes('senior') ||
        keyword.toLowerCase().includes('toy') ||
        keyword.toLowerCase().includes('giant')
      );
      if (sizeKeywords.length > 0) return sizeKeywords.join(', ');
    }
    
    // Check title for size information
    if (product.title) {
      const title = product.title.toLowerCase();
      const sizes = ['small breed', 'medium breed', 'large breed', 'toy breed', 'giant breed', 'puppy', 'adult', 'senior'];
      const foundSizes = sizes.filter(size => title.includes(size));
      if (foundSizes.length > 0) return foundSizes.join(', ');
    }
    
    return null;
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
              <div className="w-6 h-6 bg-gray-200 rounded-full flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-gray-600" />
              </div>
              <h3 className="text-sm font-semibold text-gray-900">AI Synthesis</h3>
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
      
      <main className="flex-1 max-w-full mx-auto px-4 sm:px-6 lg:px-8 py-8" data-main-content>
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

        {/* Comparison Table */}
        {comparingProducts.length > 0 && (
          <div className="mt-8">
            {/* <div className="flex items-center space-x-3 mb-6">
              <div className="w-8 h-8 bg-gradient-to-r from-chewy-blue to-blue-600 rounded-lg flex items-center justify-center">
                <Package className="w-4 h-4 text-white" />
              </div>
              <h2 className="text-xl font-bold text-gray-900">Detailed Comparison</h2>
              <div className="flex-1 h-px bg-gradient-to-r from-gray-300 to-transparent"></div>
            </div> */}
            
            {/* Featured Products Header
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl border border-blue-200 p-6 mb-6">
              <div className="text-center mb-4">
                <h3 className="text-lg font-bold text-gray-900 mb-2">Comparing Products</h3>
                <p className="text-sm text-gray-600">Side-by-side comparison of your selected items</p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {comparingProducts.map((product, index) => (
                  <div key={product.id} className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm hover:shadow-md transition-all duration-200">
                    <div className="relative mb-3">
                      <div className="w-full h-24 bg-gray-50 rounded-lg flex items-center justify-center overflow-hidden">
                        {product.image ? (
                          <img 
                            src={product.image} 
                            alt={product.title}
                            className="max-w-full max-h-full object-contain"
                          />
                        ) : (
                          <Package className="w-8 h-8 text-gray-400" />
                        )}
                      </div>
                      <div className="absolute -top-2 -right-2 w-6 h-6 bg-chewy-blue text-white rounded-full flex items-center justify-center text-xs font-bold">
                        {index + 1}
                      </div>
                    </div>
                    
                    <div className="text-center">
                      <div className="font-bold text-sm text-gray-900 mb-1">{product.brand}</div>
                      <div className="text-xs text-gray-600 line-clamp-2 mb-3 leading-relaxed">{product.title}</div>
                      
                      <div className="space-y-2">
                        <div className="text-lg font-bold text-chewy-blue">${product.price?.toFixed(2)}</div>
                        
                        {product.rating && (
                          <div className="flex items-center justify-center space-x-1">
                            <Star className="w-3 h-3 text-yellow-400 fill-current" />
                            <span className="text-xs font-medium text-gray-600">{product.rating.toFixed(1)}</span>
                            <span className="text-xs text-gray-500">
                              ({product.reviewCount && product.reviewCount > 1000 ? `${(product.reviewCount / 1000).toFixed(1)}K` : product.reviewCount})
                            </span>
                          </div>
                        )}
                        
                        {(product.autoshipPrice ?? 0) > 0 && (
                          <div className="flex items-center justify-center space-x-1">
                            <RotateCcw className="w-3 h-3 text-chewy-blue" />
                            <span className="text-xs text-chewy-blue font-medium">${product.autoshipPrice?.toFixed(2)} Autoship</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div> */}
            
            <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full min-w-[800px]">
                  <thead>
                    <tr className="bg-gradient-to-r from-gray-50 to-gray-100 border-b border-gray-200">
                      <th className="px-6 py-4 text-left">
                        <div className="flex items-center space-x-2">
                          <div className="w-2 h-2 bg-chewy-blue rounded-full"></div>
                          <span className="text-sm font-semibold text-gray-800 uppercase tracking-wide">Feature</span>
                        </div>
                      </th>
                      {comparingProducts.map((product, index) => (
                        <th key={product.id} className="px-6 py-4 text-left min-w-[220px]">
                          <div className="flex items-center space-x-3">
                            <div className="relative">
                              <div className="w-12 h-12 bg-gradient-to-br from-gray-100 to-gray-200 rounded-xl flex items-center justify-center shadow-sm">
                                {product.image ? (
                                  <img 
                                    src={product.image} 
                                    alt={product.title}
                                    className="w-10 h-10 object-cover rounded-lg"
                                  />
                                ) : (
                                  <Package className="w-6 h-6 text-gray-400" />
                                )}
                              </div>
                              <div className="absolute -top-1 -right-1 w-5 h-5 bg-chewy-blue text-white rounded-full flex items-center justify-center text-xs font-bold">
                                {index + 1}
                              </div>
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="font-bold text-sm text-gray-900 mb-1">{product.brand}</div>
                              <div className="text-xs text-gray-600 line-clamp-2 leading-relaxed mb-2">{product.title}</div>
                              <div className="flex items-center space-x-2 mb-1">
                                <span className="text-lg font-bold text-chewy-blue">${product.price?.toFixed(2)}</span>
                                {product.originalPrice && product.originalPrice > (product.price || 0) && (
                                  <span className="text-xs text-gray-500 line-through">${product.originalPrice?.toFixed(2)}</span>
                                )}
                              </div>
                              <div className="flex items-center space-x-2">
                                {product.rating && (
                                  <div className="flex items-center space-x-1">
                                    <div className="flex text-xs">
                                      {renderStars(product.rating)}
                                    </div>
                                    <span className="text-xs font-medium text-gray-600">{product.rating.toFixed(1)}</span>
                                    <span className="text-xs text-gray-500">
                                      ({product.reviewCount && product.reviewCount > 1000 ? `${(product.reviewCount / 1000).toFixed(1)}K` : product.reviewCount})
                                    </span>
                                  </div>
                                )}
                              </div>
                              {(product.autoshipPrice ?? 0) > 0 && (
                                <div className="flex items-center space-x-1 mt-1">
                                  <RotateCcw className="w-3 h-3 text-chewy-blue" />
                                  <span className="text-xs text-chewy-blue font-medium">${product.autoshipPrice?.toFixed(2)} Autoship</span>
                                </div>
                              )}
                            </div>
                          </div>
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {/* AI Synthesis Row */}
                    <tr className="hover:bg-gray-50/50 transition-colors duration-200">
                      <td className="px-6 py-5">
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 bg-gray-200 rounded-lg flex items-center justify-center">
                            <Sparkles className="w-4 h-4 text-gray-600" />
                          </div>
                          <div>
                            <div className="text-sm font-semibold text-gray-900">AI Synthesis</div>
                            <div className="text-xs text-gray-500">Expert recommendation</div>
                          </div>
                        </div>
                      </td>
                      {comparingProducts.map((product) => (
                        <td key={product.id} className="px-6 py-5">
                          {product.should_you_buy_it ? (
                            <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                              <div className="text-sm leading-relaxed text-gray-700">
                                {product.should_you_buy_it}
                              </div>
                            </div>
                          ) : (
                            <div className="text-center py-4">
                              <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                                <X className="w-4 h-4 text-gray-400" />
                              </div>
                              <span className="text-sm text-gray-400 italic">Not available</span>
                            </div>
                          )}
                        </td>
                      ))}
                    </tr>
                    
                    {/* Ingredients Row */}
                    <tr className="hover:bg-gray-50/50 transition-colors duration-200">
                      <td className="px-6 py-5">
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 bg-gradient-to-r from-green-500 to-green-600 rounded-lg flex items-center justify-center">
                            <span className="text-white text-xs font-bold">🥬</span>
                          </div>
                          <div>
                            <div className="text-sm font-semibold text-gray-900">Ingredients</div>
                            <div className="text-xs text-gray-500">Key components</div>
                          </div>
                        </div>
                      </td>
                      {comparingProducts.map((product) => {
                        const productId = product.id ?? 0;
                        const isExpanded = expandedIngredients[productId] || false;
                        const showCount = isExpanded ? product.keywords?.length || 0 : 4;
                        const visibleKeywords = product.keywords?.slice(0, showCount) || [];
                        const hasMore = (product.keywords?.length || 0) > 4;

                        return (
                          <td key={product.id} className="px-6 py-5">
                            {product.keywords && product.keywords.length > 0 ? (
                              <div className="space-y-3">
                                {/* Ingredients container with consistent styling */}
                                <div className={`overflow-hidden transition-all duration-300 ease-in-out ${
                                  isExpanded ? 'max-h-96' : 'max-h-20'
                                }`}>
                                  <div className={`${isExpanded ? 'overflow-y-auto' : ''} ${isExpanded ? 'pr-2' : ''}`}>
                                    <div className="flex flex-wrap gap-1.5 justify-center">
                                      {visibleKeywords.map((keyword, index) => (
                                        <div
                                          key={index}
                                          className="transform transition-all duration-300 ease-in-out"
                                          style={{
                                            transitionDelay: `${index > 3 ? (index - 4) * 50 : 0}ms`
                                          }}
                                        >
                                          <Badge 
                                            className="text-xs px-2.5 py-1 bg-green-50 text-green-700 border border-green-200 rounded-full font-medium hover:bg-green-100 transition-colors duration-200"
                                          >
                                            {keyword}
                                          </Badge>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                </div>
                                
                                {hasMore && (
                                  <div className="text-center">
                                    <button
                                      onClick={() => toggleIngredients(productId)}
                                      className="inline-flex items-center space-x-1 text-xs text-chewy-blue hover:text-blue-700 font-medium transition-all duration-200 hover:scale-105"
                                    >
                                      <span>
                                        {isExpanded 
                                          ? `Show less` 
                                          : `Show ${product.keywords.length - 4} more ingredients`
                                        }
                                      </span>
                                      <div className={`transform transition-transform duration-200 ${isExpanded ? 'rotate-180' : ''}`}>
                                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                        </svg>
                                      </div>
                                    </button>
                                  </div>
                                )}
                              </div>
                            ) : (
                              <div className="text-center py-4">
                                <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                                  <X className="w-4 h-4 text-gray-400" />
                                </div>
                                <span className="text-sm text-gray-400 italic">Not available</span>
                              </div>
                            )}
                          </td>
                        );
                      })}
                    </tr>
                    
                    {/* Health Feature Row */}
                    <tr className="hover:bg-gray-50/50 transition-colors duration-200">
                      <td className="px-6 py-5">
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 bg-gradient-to-r from-red-500 to-pink-500 rounded-lg flex items-center justify-center">
                            <span className="text-white text-xs font-bold">❤️</span>
                          </div>
                          <div>
                            <div className="text-sm font-semibold text-gray-900">Health Feature</div>
                            <div className="text-xs text-gray-500">Special benefits</div>
                          </div>
                        </div>
                      </td>
                      {comparingProducts.map((product) => {
                        const healthFeature = getHealthFeature(product);
                        return (
                          <td key={product.id} className="px-6 py-5">
                            {healthFeature ? (
                              <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-center">
                                <span className="text-sm font-medium text-red-800">{healthFeature}</span>
                              </div>
                            ) : (
                              <div className="text-center py-4">
                                <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                                  <X className="w-4 h-4 text-gray-400" />
                                </div>
                                <span className="text-sm text-gray-400 italic">Not specified</span>
                              </div>
                            )}
                          </td>
                        );
                      })}
                    </tr>
                    
                    {/* Special Diet Row */}
                    <tr className="hover:bg-gray-50/50 transition-colors duration-200">
                      <td className="px-6 py-5">
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
                            <span className="text-white text-xs font-bold">🥗</span>
                          </div>
                          <div>
                            <div className="text-sm font-semibold text-gray-900">Special Diet</div>
                            <div className="text-xs text-gray-500">Dietary requirements</div>
                          </div>
                        </div>
                      </td>
                      {comparingProducts.map((product) => {
                        const specialDiet = getSpecialDiet(product);
                        return (
                          <td key={product.id} className="px-6 py-5">
                            {specialDiet ? (
                              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-center">
                                <span className="text-sm font-medium text-blue-800">{specialDiet}</span>
                              </div>
                            ) : (
                              <div className="text-center py-4">
                                <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                                  <X className="w-4 h-4 text-gray-400" />
                                </div>
                                <span className="text-sm text-gray-400 italic">Not specified</span>
                              </div>
                            )}
                          </td>
                        );
                      })}
                    </tr>
                    
                    {/* Flavor Row */}
                    <tr className="hover:bg-gray-50/50 transition-colors duration-200">
                      <td className="px-6 py-5">
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 bg-gradient-to-r from-orange-500 to-orange-600 rounded-lg flex items-center justify-center">
                            <span className="text-white text-xs font-bold">🍖</span>
                          </div>
                          <div>
                            <div className="text-sm font-semibold text-gray-900">Flavor</div>
                            <div className="text-xs text-gray-500">Primary taste</div>
                          </div>
                        </div>
                      </td>
                      {comparingProducts.map((product) => {
                        const flavor = getFlavor(product);
                        return (
                          <td key={product.id} className="px-6 py-5">
                            {flavor ? (
                              <div className="bg-orange-50 border border-orange-200 rounded-lg p-3 text-center">
                                <span className="text-sm font-medium text-orange-800">{flavor}</span>
                              </div>
                            ) : (
                              <div className="text-center py-4">
                                <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                                  <X className="w-4 h-4 text-gray-400" />
                                </div>
                                <span className="text-sm text-gray-400 italic">Not specified</span>
                              </div>
                            )}
                          </td>
                        );
                      })}
                    </tr>
                    
                    {/* Breed Size Row */}
                    <tr className="hover:bg-gray-50/50 transition-colors duration-200">
                      <td className="px-6 py-5">
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 bg-gradient-to-r from-indigo-500 to-indigo-600 rounded-lg flex items-center justify-center">
                            <span className="text-white text-xs font-bold">🐕</span>
                          </div>
                          <div>
                            <div className="text-sm font-semibold text-gray-900">Breed Size</div>
                            <div className="text-xs text-gray-500">Target size range</div>
                          </div>
                        </div>
                      </td>
                      {comparingProducts.map((product) => {
                        const breedSize = getBreedSize(product);
                        return (
                          <td key={product.id} className="px-6 py-5">
                            {breedSize ? (
                              <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-3 text-center">
                                <span className="text-sm font-medium text-indigo-800">{breedSize}</span>
                              </div>
                            ) : (
                              <div className="text-center py-4">
                                <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                                  <X className="w-4 h-4 text-gray-400" />
                                </div>
                                <span className="text-sm text-gray-400 italic">Not specified</span>
                              </div>
                            )}
                          </td>
                        );
                      })}
                    </tr>
                  </tbody>
                </table>
              </div>
              
              {/* Table Footer */}
              <div className="bg-gradient-to-r from-gray-50 to-gray-100 px-6 py-4 border-t border-gray-200">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <Package className="w-4 h-4" />
                    <span>Comparing {comparingProducts.length} products side by side</span>
                  </div>
                  <div className="text-xs text-gray-500">
                    Scroll horizontally to view all details →
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Use the main ChatWidget without embedded mode - it will show as sidebar */}
      <ChatWidget />
    </div>
  );
} 