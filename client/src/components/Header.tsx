import { useState } from 'react';
import { Link } from 'wouter';
import { Search, ChevronDown, Flag, Headphones, User, ShoppingCart } from 'lucide-react';
import { useAuth } from '@/lib/auth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface HeaderProps {
  onSearch?: (query: string) => void;
  onOpenChatWithQuery?: (query: string) => void;
}

export default function Header({ onSearch, onOpenChatWithQuery }: HeaderProps) {
  const { user, logout } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      onSearch?.(searchQuery);
      onOpenChatWithQuery?.(searchQuery);
    }
  };

  return (
    <header className="bg-chewy-blue text-white shadow-lg sticky top-0 z-40">
      <div className="max-w-full mx-auto px-8 sm:px-12 lg:px-16">
        <div className="flex items-center justify-between h-16">
          {/* Logo Section */}
          <div className="flex items-center space-x-8">
            <div className="flex-shrink-0">
              <Link href="/">
                <img 
                  src="/attached_assets/chewy_logo_full_white_1750688464636.png" 
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
          <div className="flex-1 max-w-2xl mx-8 relative group">
            <form onSubmit={handleSearch} className="relative">
              <Input
                type="text"
                placeholder="Conversational AI Search"
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
            
            {/* Search Examples */}
            {!searchQuery && (
              <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-lg shadow-lg border border-gray-200 p-4 z-50">
                <p className="text-sm text-gray-600 mb-3 font-work-sans">Try asking:</p>
                <div className="space-y-2">
                  <button
                    onClick={() => {
                      const query = "Easiest way to deal with backyard dog poop?";
                      setSearchQuery(query);
                      onSearch?.(query);
                      onOpenChatWithQuery?.(query);
                    }}
                    className="block w-full text-left text-sm text-gray-700 hover:text-chewy-blue hover:bg-gray-50 p-2 rounded font-work-sans"
                  >
                    "Easiest way to deal with backyard dog poop?"
                  </button>
                  <button
                    onClick={() => {
                      const query = "Dog developed chicken allergy. Need protein though.";
                      setSearchQuery(query);
                      onSearch?.(query);
                      onOpenChatWithQuery?.(query);
                    }}
                    className="block w-full text-left text-sm text-gray-700 hover:text-chewy-blue hover:bg-gray-50 p-2 rounded font-work-sans"
                  >
                    "Dog developed chicken allergy. Need protein though."
                  </button>
                </div>
              </div>
            )}
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
            
            <div 
              className="flex items-center space-x-1 hover:text-chewy-yellow cursor-pointer"
              onClick={logout}
            >
              <User className="w-4 h-4" />
              <span className="text-sm">{user?.name || 'Sign In'}</span>
            </div>
            
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
