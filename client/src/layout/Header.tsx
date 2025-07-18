import { useState } from 'react';
import { Link } from 'wouter';
import { Search, ChevronDown, Flag, Headphones, User } from 'lucide-react';
import { useAuth } from '@/lib/auth';
import { Button } from '@/ui/Buttons/Button';
import { Input } from '@/ui/Input/Input';
import CartIcon from '@/features/cart/components/CartIcon';

interface HeaderProps {
  onSearch?: (query: string) => void;
  onOpenChatWithQuery?: (query: string) => void;
  hasSearched?: boolean;
}

export default function Header({ onSearch, onOpenChatWithQuery, hasSearched }: HeaderProps) {
  const { user } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      onSearch?.(searchQuery);
      setSearchQuery(''); // Clear search input after submission
    }
  };


  return (
    <header className="bg-chewy-blue text-white shadow-lg sticky top-0 z-40">
      <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
        {/* Main Header Row */}
        <div className="flex items-center justify-between h-16 min-w-0">
          {/* Logo Section */}
          <div className="flex items-center flex-shrink-0">
            <div className="flex-shrink-0">
              <Link href="/">
                <img 
                  src="/chewy-logo-white.png" 
                  alt="Chewy" 
                  className="h-6 sm:h-7 lg:h-8 cursor-pointer"
                />
              </Link>
            </div>
          </div>

          {/* Search Bar - Hidden on mobile */}
          <div className="hidden sm:flex flex-1 max-w-xl mx-4 lg:mx-8 min-w-0">
            <form onSubmit={handleSearch} className="relative w-full">
              <Input
                type="text"
                placeholder={hasSearched ? "Ask a new question" : "Conversational AI Search"}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2 lg:py-3 text-gray-900 bg-white border border-gray-300 rounded-lg focus:outline-none focus:border-chewy-blue focus:ring-2 focus:ring-chewy-blue focus:ring-opacity-50 font-work-sans text-sm"
              />
              <button
                type="submit"
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-chewy-blue"
              >
                <Search className="w-4 h-4 lg:w-5 lg:h-5" />
              </button>
            </form>
          </div>

          {/* User Actions */}
          <div className="flex items-center space-x-2 sm:space-x-3 lg:space-x-4 flex-shrink-0">
            <div className="hidden lg:flex items-center space-x-1 text-sm">
              <Flag className="w-4 h-4" />
              <span>USA</span>
              <ChevronDown className="w-3 h-3" />
            </div>
            
            <Button
              variant="secondary"
              className="bg-white text-chewy-blue hover:bg-gray-100 text-sm px-3 py-1.5"
            >
              Use App
            </Button>
            
            <div className="hidden lg:flex items-center space-x-1 hover:text-chewy-yellow cursor-pointer">
              <Headphones className="w-4 h-4" />
              <span className="text-sm">24/7 Help</span>
            </div>
            
            <Link href="/profile">
              <div className="flex items-center space-x-1 hover:text-chewy-yellow cursor-pointer">
                <User className="w-4 h-4" />
                <span className="text-sm hidden sm:inline lg:inline">{user?.name || 'Account'}</span>
              </div>
            </Link>
            
            <CartIcon />
          </div>
        </div>

        {/* Navigation Row - Desktop/Tablet */}
        <div className="hidden md:flex items-center justify-between py-2">
          <nav className="flex space-x-6 lg:space-x-8">
            <div className="relative group">
              <button className="flex items-center space-x-1 hover:text-chewy-yellow transition-colors text-sm">
                <span>Dog</span>
                <ChevronDown className="w-3 h-3" />
              </button>
            </div>
            <div className="relative group">
              <button className="flex items-center space-x-1 hover:text-chewy-yellow transition-colors text-sm">
                <span>Cat</span>
                <ChevronDown className="w-3 h-3" />
              </button>
            </div>
            <div className="relative group">
              <button className="flex items-center space-x-1 hover:text-chewy-yellow transition-colors text-sm">
                <span>Other Animals</span>
                <ChevronDown className="w-3 h-3" />
              </button>
            </div>
            <div className="relative group">
              <button className="flex items-center space-x-1 hover:text-chewy-yellow transition-colors text-sm">
                <span>Pharmacy</span>
                <ChevronDown className="w-3 h-3" />
              </button>
            </div>
            <div className="relative group">
              <button className="flex items-center space-x-1 hover:text-chewy-yellow transition-colors text-sm">
                <span>Services</span>
                <ChevronDown className="w-3 h-3" />
              </button>
            </div>
            <button className="hover:text-chewy-yellow transition-colors text-sm">
              Learn
            </button>
            <button className="hover:text-chewy-yellow transition-colors text-sm">
              Today's Deals
            </button>
          </nav>
          
          <div className="hidden lg:flex items-center space-x-4 text-sm">
            <div className="flex items-center space-x-1 hover:text-chewy-yellow cursor-pointer">
              <span>🐾 Flea & Tick</span>
            </div>
            <span className="text-chewy-yellow">Free delivery on first-time orders over $35</span>
          </div>
        </div>

        {/* Mobile Search Bar */}
        <div className="sm:hidden pb-3">
          <form onSubmit={handleSearch} className="relative">
            <Input
              type="text"
              placeholder={hasSearched ? "Ask a new question" : "Search"}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-3 text-gray-900 bg-white border border-gray-300 rounded-lg focus:outline-none focus:border-chewy-blue focus:ring-2 focus:ring-chewy-blue focus:ring-opacity-50 font-work-sans text-sm"
            />
            <button
              type="submit"
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-chewy-blue"
            >
              <Search className="w-5 h-5" />
            </button>
          </form>
        </div>
      </div>
      
      {/* Promotional Banner */}
      <div className="bg-chewy-yellow text-chewy-blue text-center py-2 text-sm font-medium">
        $20 eGift card with $49+ on 1st order* use WELCOME
      </div>
    </header>
  );
}
