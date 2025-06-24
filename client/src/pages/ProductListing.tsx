import React, { useState, useEffect } from 'react';
import { RotateCcw, Search, Filter, Grid, List, ChevronDown, Star } from 'lucide-react';
import Header from '@/components/Header';
import ProductCard from '@/components/ProductCard';
import ProductFilters from '@/components/ProductFilters';
import ChatWidget from '@/components/ChatWidget';
import { mockProducts } from '@/lib/mockData';
import { Product } from '../types';
import { Card, CardContent } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

export default function ProductListing() {
  const [products, setProducts] = useState<Product[]>(mockProducts);
  const [filteredProducts, setFilteredProducts] = useState<Product[]>(mockProducts);
  const [searchQuery, setSearchQuery] = useState('grain free dog food');
  const [sortBy, setSortBy] = useState('relevance');
  const [chatQuery, setChatQuery] = useState('');
  const [shouldOpenChat, setShouldOpenChat] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  useEffect(() => {
    // Listen for clear chat events
    const handleClearChat = () => {
      setHasSearched(false);
    };
    
    window.addEventListener('clearChat', handleClearChat);
    return () => window.removeEventListener('clearChat', handleClearChat);
  }, []);

  useEffect(() => {
    applyFilters();
  }, [products, searchQuery]);

  const applyFilters = () => {
    // Always show all products for demo purposes
    let filtered = [...products];

    // Apply sorting
    switch (sortBy) {
      case 'price-low':
        filtered.sort((a, b) => a.price - b.price);
        break;
      case 'price-high':
        filtered.sort((a, b) => b.price - a.price);
        break;
      case 'rating':
        filtered.sort((a, b) => b.rating - a.rating);
        break;
      default:
        // Keep original order (relevance)
        break;
    }

    setFilteredProducts(filtered);
  };

  const handleSearch = (query: string) => {
    setSearchQuery(query || 'grain free dog food');
    // For demo purposes, always show products regardless of search query
    setFilteredProducts(mockProducts);
  };

  const handleOpenChatWithQuery = (query: string, shouldClearChat = false) => {
    setChatQuery(query);
    setShouldOpenChat(true);
    setHasSearched(true);
    // Reset the trigger after a longer delay to ensure ChatWidget has time to process
    setTimeout(() => {
      setShouldOpenChat(false);
    }, 2000); // Increased from 1000ms to 2000ms
  };

  const handleClearChat = () => {
    setChatQuery(''); // Clear the initial query
    setHasSearched(false);
  };

  const handleFilterChange = (filters: any) => {
    let filtered = [...mockProducts];

    // Apply brand filters
    if (filters.brands && filters.brands.length > 0) {
      filtered = filtered.filter(product => 
        filters.brands.includes(product.brand)
      );
    }

    // Apply price range filters
    if (filters.priceRange) {
      filtered = filtered.filter(product => 
        product.price >= filters.priceRange[0] && product.price <= filters.priceRange[1] * 10
      );
    }

    setProducts(filtered);
  };

  const handleProductFilter = (keywords: string[]) => {
    if (keywords.length === 0) return;
    
    const filtered = mockProducts.filter(product =>
      keywords.some(keyword =>
        product.keywords.includes(keyword) ||
        product.title.toLowerCase().includes(keyword.toLowerCase())
      )
    );
    
    setProducts(filtered);
  };

  const handleSortChange = (value: string) => {
    setSortBy(value);
    applyFilters();
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

        {/* Search Results Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Your Search for "{searchQuery}"
            </h1>
            <p className="text-sm text-gray-600 mt-1">
              Showing {filteredProducts.length} results
            </p>
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
                <SelectItem value="price-low">Price: Low to High</SelectItem>
                <SelectItem value="price-high">Price: High to Low</SelectItem>
                <SelectItem value="rating">Customer Rating</SelectItem>
                <SelectItem value="bestsellers">Best Sellers</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="flex gap-8">
          <ProductFilters onFilterChange={handleFilterChange} />

          {/* Product Grid */}
          <div className="flex-1">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5 gap-4">
              {filteredProducts.map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
            
            {filteredProducts.length === 0 && (
              <div className="text-center py-12">
                <p className="text-gray-500 text-lg">No products found matching your criteria.</p>
                <p className="text-gray-400 text-sm mt-2">Try adjusting your filters or search terms.</p>
              </div>
            )}
          </div>
        </div>
      </main>

      <ChatWidget 
        onProductFilter={handleProductFilter} 
        initialQuery={chatQuery}
        shouldOpen={shouldOpenChat}
        shouldClearChat={hasSearched}
        onClearChat={handleClearChat}
        chatContext={{ type: 'general' }}
      />
    </div>
  );
}
