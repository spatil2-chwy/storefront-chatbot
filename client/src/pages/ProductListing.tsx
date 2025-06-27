import React, { useState, useEffect } from 'react';
import { RotateCcw, Search, Filter, Grid, List, ChevronDown, Star, Loader2 } from 'lucide-react';
import Header from '@/components/Header';
import ProductCard from '@/components/ProductCard';
import ProductFilters from '@/components/ProductFilters';
import ChatWidget from '@/components/ChatWidget';
import { api } from '@/lib/api';
import { Product } from '../types';
import { Card, CardContent } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useIsMobile } from '@/hooks/use-mobile';
import { useGlobalChat } from '@/contexts/ChatContext';

export default function ProductListing() {
  const [sortBy, setSortBy] = useState('relevance');
  const [chatQuery, setChatQuery] = useState('');
  const [shouldOpenChat, setShouldOpenChat] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const isMobile = useIsMobile();

  // Use global state for search results and query
  const { 
    searchResults, 
    setSearchResults, 
    currentSearchQuery, 
    setCurrentSearchQuery, 
    hasSearched, 
    setHasSearched 
  } = useGlobalChat();

  useEffect(() => {
    // Listen for clear chat events
    const handleClearChat = () => {
      setHasSearched(false);
    };
    
    window.addEventListener('clearChat', handleClearChat);
    return () => window.removeEventListener('clearChat', handleClearChat);
  }, [setHasSearched]);

  useEffect(() => {
    if (searchResults.length > 0) {
      applyFilters();
    }
  }, [searchResults, sortBy]);

  const applyFilters = () => {
    let filtered = [...searchResults];

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
      default:
        // Keep original order (relevance)
        break;
    }

    setSearchResults(filtered);
  };

  const handleSearch = async (query: string) => {
    const trimmedQuery = query.trim();
    setCurrentSearchQuery(trimmedQuery);
    
    if (!trimmedQuery) {
      // Clear search results if query is empty
      setSearchResults([]);
      setHasSearched(false);
      setSearchError(null);
      return;
    }

    setIsSearching(true);
    setSearchError(null);
    setHasSearched(true);

    try {
      // Use semantic search
      const searchResults = await api.searchProducts(trimmedQuery, 30);
      setSearchResults(searchResults);
    } catch (err) {
      setSearchError(err instanceof Error ? err.message : 'Search failed');
      setSearchResults([]);
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
    setChatQuery('');
    setHasSearched(false);
  };

  const handleFilterChange = (filters: any) => {
    let filtered = [...searchResults];

    // Apply brand filters
    if (filters.brands && filters.brands.length > 0) {
      filtered = filtered.filter(product => 
        product.brand && filters.brands.includes(product.brand)
      );
    }

    // Apply price range filters
    if (filters.priceRange) {
      filtered = filtered.filter(product => 
        product.price && product.price >= filters.priceRange[0] && product.price <= filters.priceRange[1] * 10
      );
    }

    setSearchResults(filtered);
  };

  const handleSortChange = (value: string) => {
    setSortBy(value);
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
                Showing {searchResults.length} results
              </p>
            </div>
            
            {/* Sort Dropdown - only show when there are results */}
            {searchResults.length > 0 && (
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">Sort By</span>
                <Select value={sortBy} onValueChange={handleSortChange}>
                  <SelectTrigger className="w-48">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="relevance">Relevance</SelectItem>
                    <SelectItem value="price-low">Price: Low to High</SelectItem>
                    <SelectItem value="price-high">Price: High to Low</SelectItem>
                    <SelectItem value="rating">Customer Rating</SelectItem>
                    <SelectItem value="bestsellers">Best Sellers</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            )}
          </div>
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
            {!isMobile && searchResults.length > 0 && (
              <ProductFilters onFilterChange={handleFilterChange} />
            )}

            {/* Product Grid */}
            <div className="flex-1">
              {searchResults.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5 gap-4 auto-rows-fr">
                  {searchResults.map((product) => (
                    <ProductCard key={product.id} product={product} />
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <p className="text-gray-500 text-lg">No products found matching your criteria.</p>
                  <p className="text-gray-400 text-sm mt-2">Try adjusting your search terms or ask the chatbot for help.</p>
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
        chatContext={{ type: 'general' }}
      />
    </div>
  );
}
