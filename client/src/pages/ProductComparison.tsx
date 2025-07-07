import React, { useEffect, useState, useRef } from 'react';
import { Link, useLocation } from 'wouter';
import { ArrowLeft, Package, Star, RotateCcw, Image as ImageIcon, ShoppingCart, Bot, X } from 'lucide-react';
import Header from '@/layout/Header';
import ChatWidget from '@/features/Chat/components/ChatWidget';
import { Button } from '@/ui/Buttons/Button';
import { Card, CardContent } from '@/ui/Cards/Card';
import { Badge } from '@/ui/Display/Badge';
import { useGlobalChat } from '@/features/Chat/context';

export default function ProductComparison() {
  const [, setLocation] = useLocation();
  const [showAIOverview, setShowAIOverview] = useState<{show: boolean, product: any, position?: { top: number; left: number }}>({show: false, product: null});
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

        {/* Product Comparison Grid */}
        <div className={`grid gap-6 mb-6 comparison-grid ${
          isChatSidebarOpen 
            ? 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3' // With sidebar: 1, 2, 3, 3 columns
            : 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-4'  // Without sidebar: 1, 2, 4, 4 columns
        }`}>
          {comparingProducts.map((product) => {
            const matchedCategories = getMatchedCategories(product);
            
            return (
              <Card key={product.id} className="bg-white rounded-xl shadow-sm hover:shadow-lg transition-shadow duration-300 h-full flex flex-col relative">
                <Link href={`/product/${product.id}`} className="flex-1 flex flex-col">
                  {/* Product Image */}
                  <div className="relative w-full h-32">
                    {renderImage(product)}
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
                        <span className="text-lg font-semibold text-gray-900">${product.price?.toFixed(2)}</span>
                        {product.originalPrice && product.originalPrice > (product.price || 0) && (
                          <span className="text-sm text-gray-500 line-through">${product.originalPrice?.toFixed(2)}</span>
                        )}
                      </div>
                      {(product.autoshipPrice ?? 0) > 0 && (
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-chewy-blue font-medium">${product.autoshipPrice?.toFixed(2)}</span>
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

        {/* Comparison Table */}
        {comparingProducts.length > 0 && (
          <div className="mt-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Detailed Comparison</h2>
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-700 border-b border-gray-200">
                      Feature
                    </th>
                    {comparingProducts.map((product) => (
                      <th key={product.id} className="px-4 py-3 text-left text-sm font-medium text-gray-700 border-b border-gray-200 min-w-[200px]">
                        <div className="flex items-center space-x-2">
                          <div className="w-8 h-8 bg-gray-100 rounded flex items-center justify-center">
                            {product.image ? (
                              <img 
                                src={product.image} 
                                alt={product.title}
                                className="w-6 h-6 object-cover rounded"
                              />
                            ) : (
                              <Package className="w-4 h-4 text-gray-400" />
                            )}
                          </div>
                          <div className="flex-1">
                            <div className="font-bold text-xs text-gray-900">{product.brand}</div>
                            <div className="text-xs text-gray-600 line-clamp-2">{product.title}</div>
                          </div>
                        </div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {/* AI Synthesis Row */}
                  <tr>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900 bg-gray-50">
                      AI Synthesis
                    </td>
                    {comparingProducts.map((product) => (
                      <td key={product.id} className="px-4 py-3 text-sm text-gray-700">
                        {product.should_you_buy_it ? (
                          <div className="text-xs leading-relaxed">
                            {product.should_you_buy_it}
                          </div>
                        ) : (
                          <span className="text-gray-400 italic">Not available</span>
                        )}
                      </td>
                    ))}
                  </tr>
                  
                  {/* Ingredients Row */}
                  <tr>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900 bg-gray-50">
                      Ingredients
                    </td>
                    {comparingProducts.map((product) => (
                      <td key={product.id} className="px-4 py-3 text-sm text-gray-700">
                        {product.keywords && product.keywords.length > 0 ? (
                          <div className="flex flex-wrap gap-1">
                            {product.keywords.slice(0, 8).map((keyword, index) => (
                              <Badge key={index} variant="secondary" className="text-xs px-2 py-1">
                                {keyword}
                              </Badge>
                            ))}
                            {product.keywords.length > 8 && (
                              <span className="text-xs text-gray-500">+{product.keywords.length - 8} more</span>
                            )}
                          </div>
                        ) : (
                          <span className="text-gray-400 italic">Not available</span>
                        )}
                      </td>
                    ))}
                  </tr>
                  
                  {/* Health Feature Row */}
                  <tr>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900 bg-gray-50">
                      Health Feature
                    </td>
                    {comparingProducts.map((product) => {
                      const healthFeature = getHealthFeature(product);
                      return (
                        <td key={product.id} className="px-4 py-3 text-sm text-gray-700">
                          {healthFeature ? (
                            <span className="text-xs">{healthFeature}</span>
                          ) : (
                            <span className="text-gray-400 italic">Not specified</span>
                          )}
                        </td>
                      );
                    })}
                  </tr>
                  
                  {/* Special Diet Row */}
                  <tr>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900 bg-gray-50">
                      Special Diet
                    </td>
                    {comparingProducts.map((product) => {
                      const specialDiet = getSpecialDiet(product);
                      return (
                        <td key={product.id} className="px-4 py-3 text-sm text-gray-700">
                          {specialDiet ? (
                            <span className="text-xs">{specialDiet}</span>
                          ) : (
                            <span className="text-gray-400 italic">Not specified</span>
                          )}
                        </td>
                      );
                    })}
                  </tr>
                  
                  {/* Flavor Row */}
                  <tr>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900 bg-gray-50">
                      Flavor
                    </td>
                    {comparingProducts.map((product) => {
                      const flavor = getFlavor(product);
                      return (
                        <td key={product.id} className="px-4 py-3 text-sm text-gray-700">
                          {flavor ? (
                            <span className="text-xs">{flavor}</span>
                          ) : (
                            <span className="text-gray-400 italic">Not specified</span>
                          )}
                        </td>
                      );
                    })}
                  </tr>
                  
                  {/* Breed Size Row */}
                  <tr>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900 bg-gray-50">
                      Breed Size
                    </td>
                    {comparingProducts.map((product) => {
                      const breedSize = getBreedSize(product);
                      return (
                        <td key={product.id} className="px-4 py-3 text-sm text-gray-700">
                          {breedSize ? (
                            <span className="text-xs">{breedSize}</span>
                          ) : (
                            <span className="text-gray-400 italic">Not specified</span>
                          )}
                        </td>
                      );
                    })}
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>

      {/* Use the main ChatWidget without embedded mode - it will show as sidebar */}
      <ChatWidget />
    </div>
  );
} 