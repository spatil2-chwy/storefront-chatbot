import { useState } from 'react';
import { Link } from 'wouter';
import { Search, ChevronDown, Flag, Headphones, User, ShoppingCart } from 'lucide-react';
import { useAuth } from '@/lib/auth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface HeaderProps {
  onSearch?: (query: string) => void;
}

export default function Header({ onSearch }: HeaderProps) {
  const { user, logout } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch?.(searchQuery);
  };

  return (
    <header className="bg-chewy-blue text-white shadow-lg sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
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
          <div className="flex-1 max-w-lg mx-8">
            <form onSubmit={handleSearch} className="relative">
              <Input
                type="text"
                placeholder="Search for products..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2 text-gray-900 bg-white border border-gray-300 rounded-lg focus:outline-none focus:border-chewy-blue focus:ring-2 focus:ring-chewy-blue focus:ring-opacity-50"
              />
              <button
                type="submit"
                className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-chewy-blue"
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
