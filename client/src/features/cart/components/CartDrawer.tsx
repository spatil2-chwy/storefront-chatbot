import React, { useState } from 'react';
import { createPortal } from 'react-dom';
import { ShoppingCart, X, Plus, Minus, Trash2, RotateCcw } from 'lucide-react';
import { Button } from '@/ui/Buttons/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/ui/Cards/Card';
import { Badge } from '@/ui/Display/Badge';
import { useCart } from '../context';
import { Link, useLocation } from 'wouter';

interface CartDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function CartDrawer({ isOpen, onClose }: CartDrawerProps) {
  const { cart, removeFromCart, updateQuantity, clearCart, getTotalItems, getTotalPrice } = useCart();
  const [, setLocation] = useLocation();

  const handleQuantityChange = (itemId: string, newQuantity: number) => {
    if (newQuantity <= 0) {
      removeFromCart(itemId);
    } else {
      updateQuantity(itemId, newQuantity);
    }
  };

  const formatPrice = (price: number) => {
    return `$${price.toFixed(2)}`;
  };

  if (!isOpen) return null;

  const drawerContent = (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        style={{ 
          zIndex: 999998,
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          width: '100vw',
          height: '100vh'
        }}
        onClick={onClose}
      />
      
      {/* Cart Drawer */}
      <div 
        className="fixed right-0 top-0 h-full w-full max-w-md bg-white shadow-xl transform transition-transform"
        style={{ 
          zIndex: 999999,
          height: '100vh'
        }}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <CardHeader className="border-b border-gray-200 flex-shrink-0">
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center space-x-2">
                <ShoppingCart className="w-5 h-5" />
                <span>Shopping Cart</span>
                {getTotalItems() > 0 && (
                  <Badge variant="secondary" className="ml-2">
                    {getTotalItems()} {getTotalItems() === 1 ? 'item' : 'items'}
                  </Badge>
                )}
              </CardTitle>
              <Button
                variant="ghost"
                size="icon"
                onClick={onClose}
                className="text-gray-500 hover:text-gray-700"
              >
                <X className="w-5 h-5" />
              </Button>
            </div>
          </CardHeader>

          {/* Cart Content */}
          <div className="flex-1 overflow-y-auto">
            {!cart || cart.items.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full p-8 text-center">
                <ShoppingCart className="w-16 h-16 text-gray-300 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Your cart is empty</h3>
                <p className="text-gray-500 mb-6">Add some products to get started!</p>
                <Button onClick={onClose} className="bg-chewy-blue hover:bg-blue-700">
                  Continue Shopping
                </Button>
              </div>
            ) : (
              <div className="p-4 space-y-4">
                {cart.items.map((item) => (
                  <Card key={item.id} className="border border-gray-200">
                    <CardContent className="p-4">
                      <div className="flex items-start space-x-3">
                        {/* Product Image */}
                        <div className="flex-shrink-0 w-16 h-16 bg-gray-100 rounded-lg overflow-hidden">
                          {item.product.image ? (
                            <img
                              src={item.product.image}
                              alt={item.product.title}
                              className="w-full h-full object-cover"
                            />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center text-gray-400">
                              <ShoppingCart className="w-6 h-6" />
                            </div>
                          )}
                        </div>

                        {/* Product Details */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex-1">
                              <Link
                                href={`/product/${item.product.id}`}
                                className="text-sm font-medium text-gray-900 hover:text-chewy-blue line-clamp-2"
                                onClick={onClose}
                              >
                                {item.product.brand} {item.product.title}
                              </Link>
                              
                              {/* Purchase Option Badge */}
                              <div className="flex items-center space-x-2 mt-1">
                                {item.purchaseOption === 'autoship' ? (
                                  <Badge variant="outline" className="text-xs border-chewy-blue text-chewy-blue">
                                    <RotateCcw className="w-3 h-3 mr-1" />
                                    Autoship
                                  </Badge>
                                ) : (
                                  <Badge variant="outline" className="text-xs">
                                    One-time
                                  </Badge>
                                )}
                              </div>
                            </div>

                            {/* Remove Button */}
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => removeFromCart(item.id)}
                              className="text-gray-400 hover:text-red-500 ml-2"
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>

                          {/* Price and Quantity Controls */}
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-2">
                              {/* Quantity Controls */}
                              <div className="flex items-center border border-gray-300 rounded-md">
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-8 w-8 p-0"
                                  onClick={() => handleQuantityChange(item.id, item.quantity - 1)}
                                >
                                  <Minus className="w-3 h-3" />
                                </Button>
                                <span className="px-3 py-1 text-sm font-medium min-w-[2rem] text-center">
                                  {item.quantity}
                                </span>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-8 w-8 p-0"
                                  onClick={() => handleQuantityChange(item.id, item.quantity + 1)}
                                >
                                  <Plus className="w-3 h-3" />
                                </Button>
                              </div>
                            </div>

                            {/* Price */}
                            <div className="text-right">
                              <div className="text-sm font-semibold text-gray-900">
                                {formatPrice(item.price * item.quantity)}
                              </div>
                              {item.quantity > 1 && (
                                <div className="text-xs text-gray-500">
                                  {formatPrice(item.price)} each
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}

                {/* Clear Cart Button */}
                {cart.items.length > 0 && (
                  <div className="pt-4 border-t border-gray-200">
                    <Button
                      variant="outline"
                      onClick={clearCart}
                      className="w-full text-red-600 hover:text-red-700 hover:bg-red-50"
                    >
                      <Trash2 className="w-4 h-4 mr-2" />
                      Clear Cart
                    </Button>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Footer with totals and checkout */}
          {cart && cart.items.length > 0 && (
            <div className="border-t border-gray-200 p-4 bg-gray-50 flex-shrink-0">
              <div className="space-y-3">
                {/* Total */}
                <div className="flex items-center justify-between text-lg font-semibold text-gray-900">
                  <span>Total:</span>
                  <span className="text-chewy-blue">
                    {formatPrice(getTotalPrice())}
                  </span>
                </div>

                {/* Shipping Notice */}
                <p className="text-xs text-gray-600 text-center">
                  Free shipping on orders over $49
                </p>

                {/* Checkout Button */}
                <Button 
                  className="w-full bg-chewy-blue hover:bg-blue-700 text-white font-medium py-3"
                  onClick={() => {
                    onClose();
                    setLocation('/checkout');
                  }}
                >
                  Proceed to Checkout
                </Button>

                {/* Continue Shopping */}
                <Button 
                  variant="outline" 
                  className="w-full text-gray-700 border-gray-300 hover:bg-gray-100"
                  onClick={onClose}
                >
                  Continue Shopping
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );

  // Render the cart drawer using a portal to ensure it's at the top level
  return createPortal(drawerContent, document.body);
}
