import { useState } from 'react';
import { Link } from 'wouter';
import { Search, ChevronDown, Flag, Headphones, User, ShoppingCart } from 'lucide-react';
import { useAuth } from '@/lib/auth';
import { Button } from '@/ui/Buttons/Button';
import { Input } from '@/ui/Input/Input';
import { useIsMobile } from '@/hooks/use-mobile';

interface HeaderProps {
  onSearch?: (query: string) => void;
  onOpenChatWithQuery?: (query: string) => void;
  hasSearched?: boolean;
}

export default function Header({ onSearch, onOpenChatWithQuery, hasSearched }: HeaderProps) {
  const { user } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const isMobile = useIsMobile();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      onSearch?.(searchQuery);
      setSearchQuery(''); // Clear search input after submission
    }
  };

  if (isMobile) {
    return (
      <header className="bg-chewy-blue text-white shadow-lg sticky top-0 z-40">
        <div className="max-w-full mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            {/* Search Bar Only */}
            <div className="flex-1">
              <form onSubmit={handleSearch} className="relative">
                <Input
                  type="text"
                  placeholder={hasSearched ? "Ask a new question" : "Conversational AI Search"}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full px-4 py-3 text-gray-900 bg-white border border-gray-300 rounded-lg focus:outline-none focus:border-chewy-blue focus:ring-2 focus:ring-chewy-blue focus:ring-opacity-50 font-work-sans"
                />
                <button
                  type="submit"
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-chewy-blue"
                >
                  <Search className="w-5 h-5" />
                </button>
              </form>
            </div>
            {/* User and Cart Icons */}
            <div className="flex items-center space-x-4 ml-4">
              <Link href="/profile">
                <div className="flex items-center space-x-1 hover:text-chewy-yellow cursor-pointer">
                  <User className="w-5 h-5" />
                </div>
              </Link>
              <div className="flex items-center space-x-1 hover:text-chewy-yellow cursor-pointer">
                <ShoppingCart className="w-5 h-5" />
              </div>
            </div>
          </div>
        </div>
      </header>
    );
  }

  // Desktop version
  return (
    <header className="bg-chewy-blue text-white shadow-lg sticky top-0 z-40">
      <div className="max-w-full mx-auto px-8 sm:px-12 lg:px-16">
        <div className="flex items-center justify-between h-16">
          {/* Logo Section */}
          <div className="flex items-center space-x-8">
            <div className="flex-shrink-0">
              <Link href="/">
                <img 
                  src="/chewy-logo-white.png" 
                  alt="Chewy" 
                  className="h-8 cursor-pointer"
                />
              </Link>
            </div>
            
            {/* Navigation Menu */}
            <nav className="hidden md:flex space-x-8">
              <div className="relative group">
                <button className="flex items-center space-x-1 hover:text-chewy-yellow transition-colors">
                  <span>Dog</span>
                  <ChevronDown className="w-4 h-4" />
                </button>
              </div>
              <div className="relative group">
                <button className="flex items-center space-x-1 hover:text-chewy-yellow transition-colors">
                  <span>Cat</span>
                  <ChevronDown className="w-4 h-4" />
                </button>
              </div>
              <div className="relative group">
                <button className="flex items-center space-x-1 hover:text-chewy-yellow transition-colors">
                  <span>Other Animals</span>
                  <ChevronDown className="w-4 h-4" />
                </button>
              </div>
              <div className="relative group">
                <button className="flex items-center space-x-1 hover:text-chewy-yellow transition-colors">
                  <span>Pharmacy</span>
                  <ChevronDown className="w-4 h-4" />
                </button>
              </div>
            </nav>
          </div>

          {/* Search Bar */}
          <div className="flex-1 max-w-2xl mx-8">
            <form onSubmit={handleSearch} className="relative">
              <Input
                type="text"
                placeholder={hasSearched ? "Ask a new question" : "Conversational AI Search"}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-3 text-gray-900 bg-white border border-gray-300 rounded-lg focus:outline-none focus:border-chewy-blue focus:ring-2 focus:ring-chewy-blue focus:ring-opacity-50 font-work-sans"
              />
              <button
                type="submit"
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-chewy-blue"
              >
                <Search className="w-5 h-5" />
              </button>
            </form>
          </div>

          {/* User Actions */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1 text-sm">
              <Flag className="w-4 h-4" />
              <span>USA</span>
              <ChevronDown className="w-3 h-3" />
            </div>
            
            <Button
              variant="secondary"
              className="bg-white text-chewy-blue hover:bg-gray-100"
            >
              Use App
            </Button>
            
            <div className="flex items-center space-x-1 hover:text-chewy-yellow cursor-pointer">
              <Headphones className="w-4 h-4" />
              <span className="text-sm">24/7 Help</span>
            </div>
            
            <Link href="/profile">
              <div className="flex items-center space-x-1 hover:text-chewy-yellow cursor-pointer">
                <User className="w-4 h-4" />
                <span className="text-sm">{user?.name || 'Sign In'}</span>
              </div>
            </Link>
            
            <div className="flex items-center space-x-1 hover:text-chewy-yellow cursor-pointer">
              <ShoppingCart className="w-4 h-4" />
              <span className="text-sm">Cart</span>
            </div>
          </div>
        </div>
      </div>
      
      {/* Promotional Banner */}
      <div className="bg-chewy-yellow text-chewy-blue text-center py-2 text-sm font-medium">
        $20 eGift card with $49+ on 1st order* use WELCOME
      </div>
    </header>
  );
}
