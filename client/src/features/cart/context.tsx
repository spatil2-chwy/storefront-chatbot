import React, { createContext, useContext, useState, ReactNode, useCallback, useEffect } from 'react';
import { Cart, CartItem, Product } from '../../types';
import { useToast } from '../../hooks/use-toast';
import { useInteractions } from '../../hooks/use-interactions';

interface CartContextType {
  cart: Cart | null;
  addToCart: (product: Product, quantity: number, purchaseOption: 'buyonce' | 'autoship') => void;
  removeFromCart: (itemId: string) => void;
  updateQuantity: (itemId: string, quantity: number) => void;
  clearCart: () => void;
  getTotalItems: () => number;
  getTotalPrice: () => number;
  getCartItemCount: (productId: number) => number;
  isInCart: (productId: number) => boolean;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};

interface CartProviderProps {
  children: ReactNode;
}

export const CartProvider: React.FC<CartProviderProps> = ({ children }) => {
  const [cart, setCart] = useState<Cart | null>(null);
  const { toast } = useToast();
  const { logAddToCart } = useInteractions();

  // Initialize cart on component mount
  useEffect(() => {
    const savedCart = localStorage.getItem('shopping-cart');
    if (savedCart) {
      try {
        const parsedCart = JSON.parse(savedCart);
        // Convert date strings back to Date objects
        parsedCart.createdAt = new Date(parsedCart.createdAt);
        parsedCart.updatedAt = new Date(parsedCart.updatedAt);
        parsedCart.items = parsedCart.items.map((item: any) => ({
          ...item,
          addedAt: new Date(item.addedAt)
        }));
        setCart(parsedCart);
      } catch (error) {
        console.error('Error parsing saved cart:', error);
        // Initialize with empty cart if parsing fails
        initializeEmptyCart();
      }
    } else {
      initializeEmptyCart();
    }
  }, []);

  // Save cart to localStorage whenever it changes
  useEffect(() => {
    if (cart) {
      localStorage.setItem('shopping-cart', JSON.stringify(cart));
    }
  }, [cart]);

  const initializeEmptyCart = useCallback(() => {
    const emptyCart: Cart = {
      id: `cart-${Date.now()}`,
      items: [],
      totalItems: 0,
      totalPrice: 0,
      createdAt: new Date(),
      updatedAt: new Date()
    };
    setCart(emptyCart);
  }, []);

  const updateCartTotals = useCallback((items: CartItem[]): { totalItems: number; totalPrice: number } => {
    const totalItems = items.reduce((sum, item) => sum + item.quantity, 0);
    const totalPrice = items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    return { totalItems, totalPrice };
  }, []);

  const addToCart = useCallback((product: Product, quantity: number = 1, purchaseOption: 'buyonce' | 'autoship' = 'buyonce') => {
    if (!product.id) {
      console.error('Cannot add product to cart: product ID is missing');
      return;
    }

    setCart(prevCart => {
      if (!prevCart) return null;

      const existingItemIndex = prevCart.items.findIndex(
        item => item.product.id === product.id && item.purchaseOption === purchaseOption
      );

      let newItems: CartItem[];

      if (existingItemIndex >= 0) {
        // Update existing item quantity
        newItems = [...prevCart.items];
        newItems[existingItemIndex] = {
          ...newItems[existingItemIndex],
          quantity: newItems[existingItemIndex].quantity + quantity
        };
      } else {
        // Add new item
        const price = purchaseOption === 'autoship' && product.autoshipPrice 
          ? product.autoshipPrice 
          : product.price || 0;

        const newItem: CartItem = {
          id: `cart-item-${Date.now()}-${Math.random()}`,
          product,
          quantity,
          purchaseOption,
          addedAt: new Date(),
          price
        };
        newItems = [...prevCart.items, newItem];
      }

      const { totalItems, totalPrice } = updateCartTotals(newItems);

      return {
        ...prevCart,
        items: newItems,
        totalItems,
        totalPrice,
        updatedAt: new Date()
      };
    });

    // Log the add to cart interaction
    logAddToCart(product, quantity);

    // Show success toast
    toast({
      title: "Added to cart!",
      description: `${product.brand} ${product.title} has been added to your cart.`,
      duration: 3000,
    });
  }, [updateCartTotals, toast, logAddToCart]);

  const removeFromCart = useCallback((itemId: string) => {
    setCart(prevCart => {
      if (!prevCart) return null;

      const newItems = prevCart.items.filter(item => item.id !== itemId);
      const { totalItems, totalPrice } = updateCartTotals(newItems);

      return {
        ...prevCart,
        items: newItems,
        totalItems,
        totalPrice,
        updatedAt: new Date()
      };
    });

    // Show removal toast
    toast({
      title: "Removed from cart",
      description: "Item has been removed from your cart.",
      duration: 2000,
    });
  }, [updateCartTotals, toast]);

  const updateQuantity = useCallback((itemId: string, quantity: number) => {
    if (quantity <= 0) {
      removeFromCart(itemId);
      return;
    }

    setCart(prevCart => {
      if (!prevCart) return null;

      const newItems = prevCart.items.map(item =>
        item.id === itemId ? { ...item, quantity } : item
      );

      const { totalItems, totalPrice } = updateCartTotals(newItems);

      return {
        ...prevCart,
        items: newItems,
        totalItems,
        totalPrice,
        updatedAt: new Date()
      };
    });
  }, [updateCartTotals, removeFromCart]);

  const clearCart = useCallback(() => {
    setCart(prevCart => {
      if (!prevCart) return null;

      return {
        ...prevCart,
        items: [],
        totalItems: 0,
        totalPrice: 0,
        updatedAt: new Date()
      };
    });
  }, []);

  const getTotalItems = useCallback(() => {
    return cart?.totalItems || 0;
  }, [cart]);

  const getTotalPrice = useCallback(() => {
    return cart?.totalPrice || 0;
  }, [cart]);

  const getCartItemCount = useCallback((productId: number) => {
    if (!cart) return 0;
    return cart.items
      .filter(item => item.product.id === productId)
      .reduce((sum, item) => sum + item.quantity, 0);
  }, [cart]);

  const isInCart = useCallback((productId: number) => {
    if (!cart) return false;
    return cart.items.some(item => item.product.id === productId);
  }, [cart]);

  return (
    <CartContext.Provider
      value={{
        cart,
        addToCart,
        removeFromCart,
        updateQuantity,
        clearCart,
        getTotalItems,
        getTotalPrice,
        getCartItemCount,
        isInCart,
      }}
    >
      {children}
    </CartContext.Provider>
  );
};
