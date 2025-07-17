import React, { useState } from 'react';
import { ShoppingCart } from 'lucide-react';
import { Button } from '@/ui/Buttons/Button';
import { Badge } from '@/ui/Display/Badge';
import { useCart } from '../context';
import CartDrawer from './CartDrawer';

export default function CartIcon() {
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const { getTotalItems } = useCart();

  const totalItems = getTotalItems();

  return (
    <>
      <Button
        variant="ghost"
        size="icon"
        className="relative text-gray-600 hover:text-gray-900"
        onClick={() => setIsDrawerOpen(true)}
      >
        <ShoppingCart className="w-6 h-6" />
        {totalItems > 0 && (
          <Badge 
            variant="destructive" 
            className="absolute -top-2 -right-2 h-5 w-5 p-0 flex items-center justify-center text-xs bg-chewy-blue hover:bg-blue-700"
          >
            {totalItems > 99 ? '99+' : totalItems}
          </Badge>
        )}
      </Button>

      <CartDrawer 
        isOpen={isDrawerOpen} 
        onClose={() => setIsDrawerOpen(false)} 
      />
    </>
  );
}
