import React, { useState, useEffect } from 'react';
import { RotateCcw, Search, Filter, Grid, List, ChevronDown, Star, Loader2, Target } from 'lucide-react';
import Header from '@/components/Header';
import ProductCard from '@/components/ProductCard';
import ProductFilters from '@/components/ProductFilters';
import ChatWidget from '@/components/ChatWidget';
import ComparisonFooter from '@/components/ComparisonFooter';
import { api } from '@/lib/api';
import { Product } from '../types';
import { Card, CardContent } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { useIsMobile } from '@/hooks/use-mobile';
import { useGlobalChat } from '@/contexts/ChatContext';

export default function ProductListing() {
  const [sortBy, setSortBy] = useState('relevance');
  const [chatQuery, setChatQuery] = useState('');
  const [shouldOpenChat, setShouldOpenChat] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [searchStats, setSearchStats] = useState<any>(null);
  const [selectedMatchFilters, setSelectedMatchFilters] = useState<string[]>([]);
  const [minMatchCount, setMinMatchCount] = useState<number>(0);
  const [filteredResults, setFilteredResults] = useState<Product[]>([]);
  const isMobile = useIsMobile();

  // Use global state for search results and query
  const { 
    searchResults, 
    setSearchResults, 
    currentSearchQuery, 
    setCurrentSearchQuery, 
    hasSearched, 
    setHasSearched,
    setShouldAutoOpen,
    comparingProducts,
    isInComparisonMode
  } = useGlobalChat();

  // Auto-open chatbot when navigating to this page
  useEffect(() => {
    // Check if user had closed the chatbot before
    const wasChatClosed = localStorage.getItem('chatClosed') === 'true';
    if (wasChatClosed) {
      setShouldAutoOpen(true);
      localStorage.removeItem('chatClosed'); // Reset the flag
    }
  }, [setShouldAutoOpen]);

  useEffect(() => {
    // Listen for clear chat events
    const handleClearChatEvent = () => {
      setHasSearched(false);
      setSearchStats(null);
      setSelectedMatchFilters([]);
      setMinMatchCount(0);
    };
    
    window.addEventListener('clearChat', handleClearChatEvent);
    return () => window.removeEventListener('clearChat', handleClearChatEvent);
  }, [setHasSearched]);

  useEffect(() => {
    if (searchResults.length > 0) {
      applyFilters();
    } else {
      setFilteredResults([]);
    }
  }, [searchResults, sortBy, selectedMatchFilters, minMatchCount]);

  const applyFilters = () => {
    let filtered = [...searchResults];

    // Apply minimum match count filter - count by category types, not individual matches
    if (minMatchCount > 0) {
      filtered = filtered.filter(product => {
        if (!product.search_matches) return false;
        
        // Count unique category types (the part before the colon)
        const uniqueCategories = new Set();
        product.search_matches.forEach(match => {
          if (match.field.includes(':')) {
            const [category] = match.field.split(':', 1);
            uniqueCategories.add(category.trim());
          }
        });
        
        return uniqueCategories.size >= minMatchCount;
      });
    }

    // Apply match field filters
    if (selectedMatchFilters.length > 0) {
      filtered = filtered.filter(product => 
        product.search_matches && 
        product.search_matches.some(match => 
          match.matched_terms.some(term => selectedMatchFilters.includes(term))
        )
      );
    }

    // Apply sorting
    switch (sortBy) {
      case 'price-low':
        filtered.sort((a, b) => (a.price || 0) - (b.price || 0));
        break;
      case 'price-high':
        filtered.sort((a, b) => (b.price || 0) - (a.price || 0));
        break;
      case 'rating':
        filtered.sort((a, b) => (b.rating || 0) - (a.rating || 0));
        break;
      case 'matches':
        // Sort by number of unique category types, not individual matches
        filtered.sort((a, b) => {
          const aCategories = new Set();
          const bCategories = new Set();
          
          a.search_matches?.forEach(match => {
            if (match.field.includes(':')) {
              const [category] = match.field.split(':', 1);
              aCategories.add(category.trim());
            }
          });
          
          b.search_matches?.forEach(match => {
            if (match.field.includes(':')) {
              const [category] = match.field.split(':', 1);
              bCategories.add(category.trim());
            }
          });
          
          return bCategories.size - aCategories.size;
        });
        break;
      default:
        // Keep original order (relevance)
        break;
    }

    setFilteredResults(filtered);
  };

  const handleSearch = async (query: string) => {
    const trimmedQuery = query.trim();
    setCurrentSearchQuery(trimmedQuery);
    
    if (!trimmedQuery) {
      // Clear search results if query is empty
      setSearchResults([]);
      setHasSearched(false);
      setSearchError(null);
      setSearchStats(null);
      setSelectedMatchFilters([]);
      setMinMatchCount(0);
      setCurrentSearchQuery('');
      return;
    }

    setIsSearching(true);
    setSearchError(null);
    setHasSearched(true);
    setSelectedMatchFilters([]);
    setMinMatchCount(0);

    // Add timing for performance analysis
    const searchStartTime = performance.now();

    try {
      // Use semantic search
      const searchData = await api.searchProducts(trimmedQuery, 30);
      
      const searchEndTime = performance.now();
      console.log(`🔍 Frontend search took: ${(searchEndTime - searchStartTime).toFixed(2)}ms`);
      
      // Handle API response format that returns {products, reply}
      if (searchData && typeof searchData === 'object' && 'products' in searchData) {
        setSearchResults(searchData.products);
        console.log(`📊 Received ${searchData.products.length} products`);
      } else {
        // Handle fallback case
        setSearchResults(Array.isArray(searchData) ? searchData : []);
      }
    } catch (err) {
      setSearchError(err instanceof Error ? err.message : 'Search failed');
      setSearchResults([]);
      setSearchStats(null);
    } finally {
      setIsSearching(false);
    }
  };

  const handleOpenChatWithQuery = (query: string, shouldClearChat = false) => {
    setChatQuery(query);
    setShouldOpenChat(true);
    setHasSearched(true);
    // Reset the trigger after a longer delay to ensure ChatWidget has time to process
    setTimeout(() => {
      setShouldOpenChat(false);
    }, 2000);
  };

  const handleClearChat = () => {
    // Only clear chat-related state, preserve product listings
    setChatQuery('');
    // Keep search results, search query, and filters intact
    // setHasSearched(false);  // Keep this true to maintain product display
    // setSearchResults([]);   // Keep search results visible
    // setCurrentSearchQuery(''); // Keep search query for reference
    // setSearchStats(null);   // Keep search stats for filtering
    // setSelectedMatchFilters([]); // Keep applied filters
    // setMinMatchCount(0);    // Keep match count filter
  };

  const handleFilterChange = (filters: any) => {
    // Note: This function is currently disabled to avoid conflicts with the new filtering system
    // TODO: Integrate brand and price filters with the new match-based filtering system
    console.log('Filter change requested:', filters);
  };

  const handleSortChange = (value: string) => {
    setSortBy(value);
  };

  const handleMatchFilterToggle = (field: string) => {
    setSelectedMatchFilters(prev => 
      prev.includes(field) 
        ? prev.filter(f => f !== field)
        : [...prev, field]
    );
  };

  const getFieldDisplayName = (field: string): string => {
    const fieldMap: { [key: string]: string } = {
      'CLEAN_NAME': 'Title',
      'PURCHASE_BRAND': 'Brand',
      'CATEGORY_LEVEL1': 'Category',
      'CATEGORY_LEVEL2': 'Subcategory',
      'CATEGORY_LEVEL3': 'Type',
      'DESCRIPTION_LONG': 'Description',
      'tags': 'Tags',
      'keywords': 'Keywords'
    };
    return fieldMap[field] || field;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header 
        onSearch={handleSearch} 
        onOpenChatWithQuery={handleOpenChatWithQuery}
        hasSearched={hasSearched}
      />
      
      <main className="max-w-full mx-auto px-8 sm:px-12 lg:px-16 py-8">
        {/* Autoship Banner */}
        <Card className="bg-chewy-light-blue mb-6">
          <CardContent className="p-4 flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <RotateCcw className="w-5 h-5 text-chewy-blue" />
              <span className="font-medium text-chewy-blue">Autoship</span>
            </div>
            <span className="text-sm text-gray-600">Save 5% on repeat deliveries</span>
          </CardContent>
        </Card>

        {/* Show search results header only when there's a search */}
        {hasSearched && (
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Your Search for "{currentSearchQuery}"
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                Showing {filteredResults.length} of {searchResults.length} results
                {(minMatchCount > 0 || selectedMatchFilters.length > 0) && filteredResults.length !== searchResults.length && (
                  <span className="text-blue-600 ml-1">(filtered)</span>
                )}
              </p>
            </div>
            
            {/* Sort and Filter Dropdowns - only show when there are results */}
            {filteredResults.length > 0 && (
              <div className="flex items-center space-x-4">
                {/* Match Count Filter */}
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">Minimum Categories Matched</span>
                  <Select value={minMatchCount.toString()} onValueChange={(value) => setMinMatchCount(parseInt(value))}>
                    <SelectTrigger className="w-32">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="0">Any</SelectItem>
                      <SelectItem value="1">1+</SelectItem>
                      <SelectItem value="2">2+</SelectItem>
                      <SelectItem value="3">3+</SelectItem>
                      <SelectItem value="4">4+</SelectItem>
                      <SelectItem value="5">5+</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Sort Dropdown */}
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">Sort By</span>
                  <Select value={sortBy} onValueChange={handleSortChange}>
                    <SelectTrigger className="w-48">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="relevance">Relevance</SelectItem>
                      <SelectItem value="matches">Most Matches</SelectItem>
                      <SelectItem value="price-low">Price: Low to High</SelectItem>
                      <SelectItem value="price-high">Price: High to Low</SelectItem>
                      <SelectItem value="rating">Customer Rating</SelectItem>
                      <SelectItem value="bestsellers">Best Sellers</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Search Match Summary */}
        {searchStats && searchStats.matched_fields && searchStats.matched_fields.length > 0 && (
          <Card className="bg-blue-50 border-blue-200 mb-6">
            <CardContent className="p-4">
              <div className="flex items-center space-x-2 mb-3">
                <Target className="w-4 h-4 text-blue-600" />
                <h3 className="font-semibold text-blue-900">Search Criteria Found</h3>
              </div>
              <p className="text-sm text-blue-700 mb-3">
                Found {searchStats.products_with_matches} products matching your search criteria
              </p>
              <div className="flex flex-wrap gap-2">
                {Object.entries(searchStats.term_counts || {}).map(([term, count]: [string, any]) => (
                  <Badge
                    key={term}
                    variant={selectedMatchFilters.includes(term) ? "default" : "outline"}
                    className={`cursor-pointer text-xs ${
                      selectedMatchFilters.includes(term) 
                        ? 'bg-blue-600 text-white' 
                        : 'text-blue-700 border-blue-300 hover:bg-blue-100'
                    }`}
                    onClick={() => handleMatchFilterToggle(term)}
                  >
                    {term} ({count})
                  </Badge>
                ))}
              </div>
              {selectedMatchFilters.length > 0 && (
                <div className="mt-2 text-xs text-blue-600">
                  Click criteria to filter results • {selectedMatchFilters.length} filter(s) active
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Show landing page content when no search */}
        {!hasSearched && (
          <div className="text-center py-12">
            <div className="max-w-md mx-auto">
              <Search className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500 text-lg mb-6">Find the perfect pet products with conversational search</p>
              <div className="space-y-2 text-sm text-gray-400">
                <p>• Search conversationally like "coconut oil free dog food" or "dog developed chicken allergy. Need Protein"</p>
                <p>• Follow up with the chatbot for refined recommendations</p>
              </div>
            </div>
          </div>
        )}

        {/* Show loading state for search */}
        {isSearching && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-chewy-blue" />
            <span className="ml-2 text-gray-600">Searching products...</span>
          </div>
        )}

        {/* Show search error */}
        {searchError && (
          <div className="text-center py-12">
            <p className="text-red-500 text-lg">Search error: {searchError}</p>
            <p className="text-gray-400 text-sm mt-2">Please try a different search term.</p>
          </div>
        )}

        {/* Show product results */}
        {hasSearched && !isSearching && !searchError && (
          <div className="flex gap-8">
            {!isMobile && filteredResults.length > 0 && (
              <ProductFilters onFilterChange={handleFilterChange} />
            )}

            {/* Product Grid */}
            <div className="flex-1">
              {filteredResults.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5 gap-4 auto-rows-fr">
                  {filteredResults.map((product) => (
                    <ProductCard key={product.id} product={product} />
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <p className="text-gray-500 text-lg">
                    {searchResults.length > 0 
                      ? "No products match your current filters." 
                      : "No products found matching your criteria."
                    }
                  </p>
                  <p className="text-gray-400 text-sm mt-2">
                    {searchResults.length > 0 
                      ? "Try adjusting your filters or clearing them to see more results." 
                      : "Try adjusting your search terms or ask the chatbot for help."
                    }
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      <ChatWidget 
        initialQuery={chatQuery}
        shouldOpen={shouldOpenChat}
        shouldClearChat={hasSearched}
        onClearChat={handleClearChat}
      />

      <ComparisonFooter />
    </div>
  );
}
