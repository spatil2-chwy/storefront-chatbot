import React, { useEffect, useState, useRef, useCallback } from 'react';
import { Link, useLocation } from 'wouter';
import { ArrowLeft, Package, Sparkles, RotateCcw, Image as ImageIcon, ShoppingCart, X } from 'lucide-react';
import Header from '@/layout/Header';
import ChatWidget from '@/features/chat/components/ChatWidget';
import { Button } from '@/ui/Buttons/Button';
import { Card, CardContent } from '@/ui/Cards/Card';
import { Badge } from '@/ui/Display/Badge';
import { useGlobalChat } from '@/features/chat/context';
import { useCart } from '@/features/cart/context';
import { getPetIcon } from '@/lib/utils/pet-icons';

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

  const { addToCart } = useCart();

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
    if (!product?.id) {
      console.error('Cannot add product to cart: product ID is missing');
      return;
    }

    // Determine purchase option based on autoship availability
    const purchaseOption = (product.autoshipPrice && product.autoshipPrice > 0) ? 'autoship' : 'buyonce';
    
    // Add to cart with quantity 1
    addToCart(product, 1, purchaseOption);
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

  // New helper functions for AI synthesis and relevant metadata
  const getComparisonRows = () => {
    const rows = [];
    
    // AI Synthesis Section
    rows.push({
      id: 'section_ai',
      type: 'section_header',
      title: 'AI Analysis',
      color: 'from-blue-500 to-blue-600',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      textColor: 'text-blue-800'
    });
    
    // AI Synthesis Row (always first)
    rows.push({
      id: 'ai_synthesis',
      title: 'AI Recommendation',
      subtitle: 'What Tylee thinks',
      icon: '🤖',
      color: 'from-blue-500 to-blue-600',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      textColor: 'text-blue-800',
      getValue: (product: any) => product.should_you_buy_it,
      type: 'ai_synthesis'
    });

    // What Customers Love (if available)
    const hasCustomerLove = comparingProducts.some(p => p.what_customers_love);
    if (hasCustomerLove) {
      rows.push({
        id: 'customer_love',
        title: 'Customer Highlights',
        subtitle: 'What pet parents love',
        icon: '❤️',
        color: 'from-pink-500 to-pink-600',
        bgColor: 'bg-pink-50',
        borderColor: 'border-pink-200',
        textColor: 'text-pink-800',
        getValue: (product: any) => product.what_customers_love,
        type: 'ai_synthesis'
      });
    }

    // What to Watch Out For (if available)
    const hasWatchOut = comparingProducts.some(p => p.what_to_watch_out_for);
    if (hasWatchOut) {
      rows.push({
        id: 'watch_out',
        title: 'Considerations',
        subtitle: 'Things to be aware of',
        icon: '⚠️',
        color: 'from-orange-500 to-orange-600',
        bgColor: 'bg-orange-50',
        borderColor: 'border-orange-200',
        textColor: 'text-orange-800',
        getValue: (product: any) => product.what_to_watch_out_for,
        type: 'ai_synthesis'
      });
    }

    // Product Metadata Section
    rows.push({
      id: 'section_metadata',
      type: 'section_header',
      title: 'Product Details',
      color: 'from-purple-500 to-purple-600',
      bgColor: 'bg-purple-50',
      borderColor: 'border-purple-200',
      textColor: 'text-purple-800'
    });

    // Brand
    const hasBrand = comparingProducts.some(p => p.brand);
    if (hasBrand) {
      rows.push({
        id: 'brand',
        title: 'Brand',
        subtitle: 'Manufacturer',
        icon: '🏢',
        color: 'from-red-500 to-red-600',
        bgColor: 'bg-red-50',
        borderColor: 'border-red-200',
        textColor: 'text-red-800',
        getValue: (product: any) => product.brand,
        type: 'metadata'
      });
    }

    // Product Type/Category
    const hasProductType = comparingProducts.some(p => p.product_type || p.category_level_1);
    if (hasProductType) {
      rows.push({
        id: 'product_type',
        title: 'Product Type',
        subtitle: 'Category classification',
        icon: '🏷️',
        color: 'from-purple-500 to-purple-600',
        bgColor: 'bg-purple-50',
        borderColor: 'border-purple-200',
        textColor: 'text-purple-800',
        getValue: (product: any) => product.product_type || product.category_level_1,
        type: 'metadata'
      });
    }

    // Merch Classification
    const hasMerchClassification = comparingProducts.some(p => p.merch_classification1 || p.merch_classification2 || p.merch_classification3 || p.merch_classification4);
    if (hasMerchClassification) {
      rows.push({
        id: 'merch_classification',
        title: 'Classification',
        subtitle: 'Merchandising category',
        icon: '📊',
        color: 'from-indigo-500 to-indigo-600',
        bgColor: 'bg-indigo-50',
        borderColor: 'border-indigo-200',
        textColor: 'text-indigo-800',
        getValue: (product: any) => {
          const classifications = [
            product.merch_classification1,
            product.merch_classification2,
            product.merch_classification3,
            product.merch_classification4
          ].filter(Boolean);
          return classifications.length > 0 ? classifications.join(', ') : null;
        },
        type: 'metadata'
      });
    }

    // Life Stage
    const hasLifeStage = comparingProducts.some(p => p.life_stage || p.lifestage);
    if (hasLifeStage) {
      rows.push({
        id: 'life_stage',
        title: 'Life Stage',
        subtitle: 'Age appropriateness',
        icon: '🐾',
        color: 'from-green-500 to-green-600',
        bgColor: 'bg-green-50',
        borderColor: 'border-green-200',
        textColor: 'text-green-800',
        getValue: (product: any) => product.life_stage || product.lifestage,
        type: 'metadata'
      });
    }

    // Pet Type (only if different from product type)
    const hasPetType = comparingProducts.some(p => p.attr_pet_type || p.pet_types);
    
    if (hasPetType) {
      // Check if pet type and product type are the same for all products
      const sameValues = comparingProducts.every(product => {
        const petType = product.attr_pet_type || product.pet_types;
        const productType = product.product_type || product.category_level_1;
        return petType === productType;
      });
      
      if (!sameValues) {
        rows.push({
          id: 'pet_type',
          title: 'Pet Type',
          subtitle: 'Dog, cat, or other',
          icon: getPetIcon('DOG'), // Default to dog icon for pet type comparison
          color: 'from-indigo-500 to-indigo-600',
          bgColor: 'bg-indigo-50',
          borderColor: 'border-indigo-200',
          textColor: 'text-indigo-800',
          getValue: (product: any) => product.attr_pet_type || product.pet_types,
          type: 'metadata'
        });
      }
    }

    // Breed Size (if available)
    const hasBreedSize = comparingProducts.some(p => getBreedSize(p));
    if (hasBreedSize) {
      rows.push({
        id: 'breed_size',
        title: 'Breed Size',
        subtitle: 'Target size range',
        icon: '📏',
        color: 'from-teal-500 to-teal-600',
        bgColor: 'bg-teal-50',
        borderColor: 'border-teal-200',
        textColor: 'text-teal-800',
        getValue: getBreedSize,
        type: 'metadata'
      });
    }

    // Food Form (for food products)
    const hasFoodForm = comparingProducts.some(p => p.attr_food_form);
    if (hasFoodForm) {
      rows.push({
        id: 'food_form',
        title: 'Food Form',
        subtitle: 'Dry, wet, or other',
        icon: '🥘',
        color: 'from-amber-500 to-amber-600',
        bgColor: 'bg-amber-50',
        borderColor: 'border-amber-200',
        textColor: 'text-amber-800',
        getValue: (product: any) => product.attr_food_form,
        type: 'metadata'
      });
    }

    // Special Diet (if available)
    const hasSpecialDiet = comparingProducts.some(p => getSpecialDiet(p));
    if (hasSpecialDiet) {
      rows.push({
        id: 'special_diet',
        title: 'Special Diet',
        subtitle: 'Dietary requirements',
        icon: '🥗',
        color: 'from-blue-500 to-blue-600',
        bgColor: 'bg-blue-50',
        borderColor: 'border-blue-200',
        textColor: 'text-blue-800',
        getValue: getSpecialDiet,
        type: 'metadata'
      });
    }

    // Health Features (if available)
    const hasHealthFeatures = comparingProducts.some(p => getHealthFeature(p));
    if (hasHealthFeatures) {
      rows.push({
        id: 'health_features',
        title: 'Health Benefits',
        subtitle: 'Special health features',
        icon: '💊',
        color: 'from-red-500 to-red-600',
        bgColor: 'bg-red-50',
        borderColor: 'border-red-200',
        textColor: 'text-red-800',
        getValue: getHealthFeature,
        type: 'metadata'
      });
    }

    // Flavor (if available)
    const hasFlavor = comparingProducts.some(p => getFlavor(p));
    if (hasFlavor) {
      rows.push({
        id: 'flavor',
        title: 'Flavor',
        subtitle: 'Primary taste',
        icon: '🍖',
        color: 'from-orange-500 to-orange-600',
        bgColor: 'bg-orange-50',
        borderColor: 'border-orange-200',
        textColor: 'text-orange-800',
        getValue: getFlavor,
        type: 'metadata'
      });
    }

    // Ingredients Section
    const hasIngredients = comparingProducts.some(p => p.keywords && p.keywords.length > 0);
    if (hasIngredients) {
      rows.push({
        id: 'section_ingredients',
        type: 'section_header',
        title: 'Ingredients & Components',
        color: 'from-green-500 to-green-600',
        bgColor: 'bg-green-50',
        borderColor: 'border-green-200',
        textColor: 'text-green-800'
      });
      
      rows.push({
        id: 'ingredients',
        title: 'Key Ingredients',
        subtitle: 'Important components',
        icon: '🥬',
        color: 'from-green-500 to-green-600',
        bgColor: 'bg-green-50',
        borderColor: 'border-green-200',
        textColor: 'text-green-800',
        getValue: (product: any) => product.keywords,
        type: 'ingredients'
      });
    }

    return rows;
  };

  // State for text truncation
  const [expandedText, setExpandedText] = useState<{[key: string]: boolean}>({});

  const toggleTextExpansion = (rowId: string, productId: number) => {
    const key = `${rowId}_${productId}`;
    setExpandedText(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  // Function to check if text needs truncation based on height
  const checkTextHeight = (textRef: React.RefObject<HTMLDivElement>) => {
    if (!textRef.current) return false;
    const lineHeight = 20; // Approximate line height for text-sm
    const maxHeight = lineHeight * 3; // 3 lines
    return textRef.current.scrollHeight > maxHeight;
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
            
            <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full min-w-[800px] table-fixed">
                  <thead className="sticky top-0 z-10">
                    <tr className="bg-gradient-to-r from-gray-50 to-gray-100 border-b-2 border-gray-200 shadow-md">
                      <th className="px-6 py-6 text-left w-56 bg-white/80 backdrop-blur-sm">
                        <div className="flex items-center space-x-3">
                          <div className="w-3 h-3 bg-chewy-blue rounded-full shadow-sm"></div>
                          <span className="text-sm font-bold text-gray-800 uppercase tracking-wider">Product</span>
                        </div>
                      </th>
                      {comparingProducts.map((product, index) => (
                        <th key={product.id} className="px-6 py-6 text-left bg-white/80 backdrop-blur-sm" style={{width: `calc((100% - 12rem) / ${comparingProducts.length})`}}>
                          <div className="bg-white rounded-xl border-2 border-gray-200 p-4 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105">
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
                              <div className="absolute -top-2 -right-2 w-6 h-6 bg-chewy-blue text-white rounded-full flex items-center justify-center text-xs font-bold shadow-lg">
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
                                    <div className="flex text-xs">
                                      {renderStars(product.rating)}
                                    </div>
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
                                
                                <button
                                  onClick={() => handleAddToCart(product)}
                                  className="w-full bg-chewy-blue hover:bg-blue-700 text-white text-xs font-medium py-2 px-3 rounded-lg transition-colors duration-200 flex items-center justify-center space-x-1"
                                >
                                  <ShoppingCart className="w-3 h-3" />
                                  <span>Add to Cart</span>
                                </button>
                              </div>
                            </div>
                          </div>
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {getComparisonRows().map((row, rowIndex) => {
                      // Section header row
                      if (row.type === 'section_header') {
                        return (
                          <tr key={row.id} className="bg-gradient-to-r from-gray-50 to-gray-100 border-b-2 border-gray-200">
                            <td colSpan={comparingProducts.length + 1} className="px-6 py-4">
                              <div className="flex items-center">
                                <div className="text-lg font-bold text-gray-900">{row.title}</div>
                              </div>
                            </td>
                          </tr>
                        );
                      }

                      // Regular data row with alternating colors
                      const isEvenRow = rowIndex % 2 === 0;
                      const rowBgClass = isEvenRow ? 'bg-white' : 'bg-gray-50/30';
                      
                      return (
                        <tr key={row.id} className={`${rowBgClass} hover:bg-blue-50/50 transition-all duration-300 group`}>
                          <td className="px-6 py-6 border-r border-gray-100 w-56">
                            <div className="flex items-start space-x-3">
                              <div className={`w-8 h-8 bg-gradient-to-r ${row.color} rounded-lg flex items-center justify-center shadow-md group-hover:shadow-lg transition-all duration-300 transform group-hover:scale-110 flex-shrink-0 mt-1`}>
                                <span className="text-white text-sm font-bold">{row.icon}</span>
                              </div>
                              <div className="min-w-0 flex-1">
                                <div className="text-sm font-semibold text-gray-900 leading-tight whitespace-normal">{row.title}</div>
                                <div className="text-xs text-gray-500 leading-tight mt-1 whitespace-normal">{row.subtitle}</div>
                              </div>
                            </div>
                          </td>
                          {comparingProducts.map((product) => {
                            const value = row.getValue?.(product);
                            
                            // Special handling for ingredients row
                            if (row.type === 'ingredients' && Array.isArray(value)) {
                              const productId = product.id ?? 0;
                              const isExpanded = expandedIngredients[productId] || false;
                              const showCount = isExpanded ? value.length || 0 : 4;
                              const visibleKeywords = value.slice(0, showCount) || [];
                              const hasMore = (value.length || 0) > 4;

                                                           return (
                               <td key={product.id} className="px-6 py-6 align-top">
                                 {value && value.length > 0 ? (
                                    <div className="space-y-4">
                                      <div className={`overflow-hidden transition-all duration-500 ease-in-out ${
                                        isExpanded ? 'max-h-96' : 'max-h-24'
                                      }`}>
                                        <div className={`${isExpanded ? 'overflow-y-auto' : ''} ${isExpanded ? 'pr-2' : ''}`}>
                                          <div className="flex flex-wrap gap-2 justify-start">
                                            {visibleKeywords.map((keyword: string, index: number) => (
                                              <div
                                                key={index}
                                                className="transform transition-all duration-300 ease-in-out hover:scale-105"
                                                style={{
                                                  transitionDelay: `${index > 3 ? (index - 4) * 50 : 0}ms`
                                                }}
                                              >
                                                <Badge 
                                                  className="text-sm px-3 py-2 bg-green-100 text-green-800 border-2 border-green-200 rounded-full font-medium hover:bg-green-200 hover:border-green-300 transition-all duration-200 shadow-sm hover:shadow-md"
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
                                            className="inline-flex items-center space-x-2 text-sm text-chewy-blue hover:text-blue-700 font-medium transition-all duration-200 hover:scale-105 bg-blue-50 hover:bg-blue-100 px-4 py-2 rounded-lg"
                                          >
                                            <span>
                                              {isExpanded 
                                                ? `Show less` 
                                                : `Show ${value.length - 4} more ingredients`
                                              }
                                            </span>
                                            <div className={`transform transition-transform duration-200 ${isExpanded ? 'rotate-180' : ''}`}>
                                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                              </svg>
                                            </div>
                                          </button>
                                        </div>
                                      )}
                                    </div>
                                  ) : (
                                    <div className="text-left py-6">
                                      <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center mb-3">
                                        <X className="w-5 h-5 text-gray-400" />
                                      </div>
                                      <span className="text-sm text-gray-400 italic">Not available</span>
                                    </div>
                                  )}
                                </td>
                              );
                            }
                            
                            // Special handling for AI synthesis rows (longer text with read more)
                            if (row.type === 'ai_synthesis' && typeof value === 'string') {
                              const textKey = `${row.id}_${product.id}`;
                              const isTextExpanded = expandedText[textKey] || false;
                              const textRef = useRef<HTMLDivElement>(null);
                              const [needsTruncation, setNeedsTruncation] = useState(false);

                              // Check if text needs truncation after render
                              useEffect(() => {
                                if (textRef.current) {
                                  const lineHeight = 24; // Actual line height for text-sm leading-relaxed
                                  const maxHeight = lineHeight * 3; // 3 lines
                                  setNeedsTruncation(textRef.current.scrollHeight > maxHeight);
                                }
                              }, [value]);

                              return (
                                <td key={product.id} className="px-6 py-6 align-top">
                                  {value ? (
                                    <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 hover:bg-gray-100 transition-colors duration-200">
                                      <div 
                                        ref={textRef}
                                        className={`text-sm leading-relaxed text-gray-700 text-left ${
                                          !isTextExpanded && needsTruncation ? 'overflow-hidden' : ''
                                        }`}
                                        style={{
                                          maxHeight: !isTextExpanded && needsTruncation ? '70px' : 'none'
                                        }}
                                      >
                                        {value}
                                      </div>
                                      {needsTruncation && (
                                        <button
                                          onClick={() => toggleTextExpansion(row.id, product.id!)}
                                          className="mt-3 text-sm text-chewy-blue hover:text-blue-700 font-medium transition-colors duration-200 hover:underline"
                                        >
                                          {isTextExpanded ? 'Read less' : 'Read more'}
                                        </button>
                                      )}
                                    </div>
                                  ) : (
                                    <div className="text-left py-6">
                                      <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center mb-3">
                                        <X className="w-5 h-5 text-gray-400" />
                                      </div>
                                      <span className="text-sm text-gray-400 italic">Not available</span>
                                    </div>
                                  )}
                                </td>
                              );
                            }
                            
                            // Default handling for metadata rows
                            return (
                              <td key={product.id} className="px-6 py-6 align-top">
                                {value ? (
                                  <div className={`${row.bgColor} border-2 ${row.borderColor} rounded-lg p-4 text-left hover:shadow-md transition-all duration-200 inline-block`}>
                                    <span className={`text-sm font-medium ${row.textColor}`}>{value}</span>
                                  </div>
                                ) : (
                                  <div className="text-left py-6">
                                    <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center mb-3">
                                      <X className="w-5 h-5 text-gray-400" />
                                    </div>
                                    <span className="text-sm text-gray-400 italic">Not specified</span>
                                  </div>
                                )}
                              </td>
                            );
                          })}
                        </tr>
                      );
                    })}
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