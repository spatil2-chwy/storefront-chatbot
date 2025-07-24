import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'wouter';
import { ArrowLeft, ShoppingCart, Truck, CreditCard, MapPin, User, Check, AlertCircle } from 'lucide-react';
import Header from '@/layout/Header';
import { Button } from '@/ui/Buttons/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/ui/Cards/Card';
import { Input } from '@/ui/Input/Input';
import { Label } from '@/ui/Input/Label';
import { RadioGroup, RadioGroupItem } from '@/ui/RadioButtons/RadioGroup';
import { Checkbox } from '@/ui/Checkboxes/Checkbox';
import { Badge } from '@/ui/Display/Badge';
import { useCart } from '@/features/cart/context';
import { useAuth } from '@/lib/auth';
import { useToast } from '@/hooks/use-toast';
import { ordersApi, OrderCreate, OrderItem } from '@/lib/api/orders';
import { useInteractions } from '@/hooks/use-interactions';

interface CheckoutFormData {
  // Shipping Information
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  address: string;
  city: string;
  state: string;
  zipCode: string;
  
  // Payment Information
  cardNumber: string;
  expiryDate: string;
  cvv: string;
  cardName: string;
  
  // Billing Address
  billingAddressSameAsShipping: boolean;
  billingAddress: string;
  billingCity: string;
  billingState: string;
  billingZipCode: string;
}

export default function Checkout() {
  const [, setLocation] = useLocation();
  const { cart, getTotalItems, getTotalPrice, clearCart } = useCart();
  const { user } = useAuth();
  const { toast } = useToast();
  const { logPurchase } = useInteractions();

  const [formData, setFormData] = useState<CheckoutFormData>({
    firstName: user?.name?.split(' ')[0] || '',
    lastName: user?.name?.split(' ')[1] || '',
    email: user?.email || '',
    phone: '',
    address: '',
    city: '',
    state: '',
    zipCode: '',
    cardNumber: '',
    expiryDate: '',
    cvv: '',
    cardName: user?.name || '',
    billingAddressSameAsShipping: true,
    billingAddress: '',
    billingCity: '',
    billingState: '',
    billingZipCode: '',
  });

  const [currentStep, setCurrentStep] = useState(1);
  const [isProcessing, setIsProcessing] = useState(false);
  const [orderPlaced, setOrderPlaced] = useState(false);

  // Redirect if cart is empty
  useEffect(() => {
    if (!cart || cart.items.length === 0) {
      setLocation('/');
    }
  }, [cart, setLocation]);

  const handleInputChange = (field: keyof CheckoutFormData, value: string | boolean) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const calculateShipping = () => {
    // Free shipping for orders over $49
    const subtotal = getTotalPrice();
    return subtotal >= 49 ? 0 : 5.99;
  };

  const calculateTax = () => {
    // Simple tax calculation (8.5%)
    return getTotalPrice() * 0.085;
  };

  const calculateTotal = () => {
    return getTotalPrice() + calculateShipping() + calculateTax();
  };

  const validateStep = (step: number): boolean => {
    switch (step) {
      case 1: // Shipping
        return !!(formData.firstName && formData.lastName && formData.email && 
                 formData.address && formData.city && formData.state && formData.zipCode);
      case 2: // Payment
        return !!(formData.cardNumber && formData.expiryDate && formData.cvv && formData.cardName);
      default:
        return true;
    }
  };

  const handleNextStep = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => prev + 1);
    } else {
      toast({
        title: "Missing Information",
        description: "Please fill in all required fields to continue.",
        variant: "destructive",
      });
    }
  };

  const handlePlaceOrder = async () => {
    if (!validateStep(2)) {
      toast({
        title: "Missing Information",
        description: "Please fill in all required fields to place your order.",
        variant: "destructive",
      });
      return;
    }

    if (!user?.customer_id) {
      toast({
        title: "Authentication Required",
        description: "Please log in to place an order.",
        variant: "destructive",
      });
      return;
    }

    if (!cart || cart.items.length === 0) {
      toast({
        title: "Empty Cart",
        description: "Your cart is empty. Please add items before placing an order.",
        variant: "destructive",
      });
      return;
    }

    setIsProcessing(true);

    try {
      // Convert cart items to order items
      const orderItems: OrderItem[] = cart.items.map(item => ({
        product_id: item.product.id!,
        product_title: item.product.title || '',
        product_brand: item.product.brand || '',
        product_image: item.product.image || '',
        quantity: item.quantity,
        purchase_option: item.purchaseOption,
        unit_price: item.price,
        total_price: item.price * item.quantity
      }));

      // Prepare order data
      const orderData: OrderCreate = {
        customer_id: user.customer_id,
        subtotal: getTotalPrice(),
        shipping_cost: calculateShipping(),
        tax_amount: calculateTax(),
        total_amount: calculateTotal(),
        
        // Shipping Information
        shipping_first_name: formData.firstName,
        shipping_last_name: formData.lastName,
        shipping_email: formData.email,
        shipping_phone: formData.phone,
        shipping_address: formData.address,
        shipping_city: formData.city,
        shipping_state: formData.state,
        shipping_zip_code: formData.zipCode,
        
        // Payment Information (masked for security)
        payment_method: "credit_card",
        card_last_four: formData.cardNumber.slice(-4),
        cardholder_name: formData.cardName,
        
        // Billing Address (if different from shipping)
        billing_address: formData.billingAddressSameAsShipping ? undefined : formData.billingAddress,
        billing_city: formData.billingAddressSameAsShipping ? undefined : formData.billingCity,
        billing_state: formData.billingAddressSameAsShipping ? undefined : formData.billingState,
        billing_zip_code: formData.billingAddressSameAsShipping ? undefined : formData.billingZipCode,
        
        items: orderItems
      };

      // Create the order
      const order = await ordersApi.createOrder(orderData);
      
      // Log purchase interactions for each item
      for (const item of cart.items) {
        await logPurchase(item.product, item.quantity, item.purchaseOption);
      }
      
      // Clear cart and show success
      clearCart();
      setOrderPlaced(true);
      
      toast({
        title: "Order Placed Successfully!",
        description: `Your order #${order.order_id} for ${getTotalItems()} items has been placed.`,
      });

    } catch (error: any) {
      console.error('Order creation failed:', error);
      toast({
        title: "Order Failed",
        description: error.message || "There was an error processing your order. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsProcessing(false);
    }
  };

  if (orderPlaced) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Card className="text-center py-12">
            <CardContent>
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <Check className="w-8 h-8 text-green-600" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900 mb-4">Order Placed Successfully!</h1>
              <p className="text-gray-600 mb-6">
                Thank you for your order. You'll receive a confirmation email shortly.
              </p>
              <div className="space-y-4">
                <Button 
                  onClick={() => setLocation('/')}
                  className="bg-chewy-blue hover:bg-blue-700"
                >
                  Continue Shopping
                </Button>
                <Button 
                  variant="outline"
                  onClick={() => setLocation('/profile')}
                >
                  View Order History
                </Button>
              </div>
            </CardContent>
          </Card>
        </main>
      </div>
    );
  }

  if (!cart || cart.items.length === 0) {
    return null; // Will redirect via useEffect
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Breadcrumb */}
        <nav className="flex mb-6 text-sm">
          <Link href="/" className="text-chewy-blue hover:underline flex items-center space-x-1">
            <ArrowLeft className="w-4 h-4" />
            <span>Continue Shopping</span>
          </Link>
        </nav>

        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-center space-x-8">
            {[
              { step: 1, title: 'Shipping', icon: Truck },
              { step: 2, title: 'Payment', icon: CreditCard },
              { step: 3, title: 'Review', icon: Check }
            ].map(({ step, title, icon: Icon }) => (
              <div
                key={step}
                className={`flex items-center space-x-2 ${
                  currentStep >= step ? 'text-chewy-blue' : 'text-gray-400'
                }`}
              >
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center ${
                    currentStep >= step 
                      ? 'bg-chewy-blue text-white' 
                      : 'bg-gray-200 text-gray-400'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                </div>
                <span className="font-medium">{title}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Form */}
          <div className="lg:col-span-2 space-y-6">
            {/* Step 1: Shipping Information */}
            {currentStep === 1 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Truck className="w-5 h-5" />
                    <span>Shipping Information</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="firstName">First Name *</Label>
                      <Input
                        id="firstName"
                        value={formData.firstName}
                        onChange={(e) => handleInputChange('firstName', e.target.value)}
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="lastName">Last Name *</Label>
                      <Input
                        id="lastName"
                        value={formData.lastName}
                        onChange={(e) => handleInputChange('lastName', e.target.value)}
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="email">Email Address *</Label>
                    <Input
                      id="email"
                      type="email"
                      value={formData.email}
                      onChange={(e) => handleInputChange('email', e.target.value)}
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="phone">Phone Number</Label>
                    <Input
                      id="phone"
                      type="tel"
                      value={formData.phone}
                      onChange={(e) => handleInputChange('phone', e.target.value)}
                    />
                  </div>

                  <div>
                    <Label htmlFor="address">Street Address *</Label>
                    <Input
                      id="address"
                      value={formData.address}
                      onChange={(e) => handleInputChange('address', e.target.value)}
                      required
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <Label htmlFor="city">City *</Label>
                      <Input
                        id="city"
                        value={formData.city}
                        onChange={(e) => handleInputChange('city', e.target.value)}
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="state">State *</Label>
                      <Input
                        id="state"
                        value={formData.state}
                        onChange={(e) => handleInputChange('state', e.target.value)}
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="zipCode">ZIP Code *</Label>
                      <Input
                        id="zipCode"
                        value={formData.zipCode}
                        onChange={(e) => handleInputChange('zipCode', e.target.value)}
                        required
                      />
                    </div>
                  </div>

                  <div className="pt-4">
                    <Button 
                      onClick={handleNextStep}
                      className="w-full bg-chewy-blue hover:bg-blue-700"
                    >
                      Continue to Payment
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Step 2: Payment Information */}
            {currentStep === 2 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <CreditCard className="w-5 h-5" />
                    <span>Payment Information</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="cardNumber">Card Number *</Label>
                    <Input
                      id="cardNumber"
                      placeholder="1234 5678 9012 3456"
                      value={formData.cardNumber}
                      onChange={(e) => handleInputChange('cardNumber', e.target.value)}
                      required
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="expiryDate">Expiry Date *</Label>
                      <Input
                        id="expiryDate"
                        placeholder="MM/YY"
                        value={formData.expiryDate}
                        onChange={(e) => handleInputChange('expiryDate', e.target.value)}
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="cvv">CVV *</Label>
                      <Input
                        id="cvv"
                        placeholder="123"
                        value={formData.cvv}
                        onChange={(e) => handleInputChange('cvv', e.target.value)}
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="cardName">Name on Card *</Label>
                    <Input
                      id="cardName"
                      value={formData.cardName}
                      onChange={(e) => handleInputChange('cardName', e.target.value)}
                      required
                    />
                  </div>

                  <div className="pt-4 space-y-3">
                    <Button 
                      onClick={handleNextStep}
                      className="w-full bg-chewy-blue hover:bg-blue-700"
                    >
                      Review Order
                    </Button>
                    <Button 
                      variant="outline"
                      onClick={() => setCurrentStep(1)}
                      className="w-full"
                    >
                      Back to Shipping
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Step 3: Review Order */}
            {currentStep === 3 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Check className="w-5 h-5" />
                    <span>Review Your Order</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Shipping Address */}
                  <div>
                    <h3 className="font-semibold mb-2">Shipping Address</h3>
                    <div className="text-sm text-gray-600">
                      <p>{formData.firstName} {formData.lastName}</p>
                      <p>{formData.address}</p>
                      <p>{formData.city}, {formData.state} {formData.zipCode}</p>
                      <p>{formData.email}</p>
                    </div>
                  </div>

                  {/* Payment Method */}
                  <div>
                    <h3 className="font-semibold mb-2">Payment Method</h3>
                    <div className="text-sm text-gray-600">
                      <p>**** **** **** {formData.cardNumber.slice(-4)}</p>
                      <p>{formData.cardName}</p>
                    </div>
                  </div>

                  <div className="pt-4 space-y-3">
                    <Button 
                      onClick={handlePlaceOrder}
                      disabled={isProcessing}
                      className="w-full bg-green-600 hover:bg-green-700 text-white"
                    >
                      {isProcessing ? 'Processing...' : 'Place Order'}
                    </Button>
                    <Button 
                      variant="outline"
                      onClick={() => setCurrentStep(2)}
                      className="w-full"
                      disabled={isProcessing}
                    >
                      Back to Payment
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Order Summary */}
          <div className="lg:col-span-1">
            <Card className="sticky top-4">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <ShoppingCart className="w-5 h-5" />
                  <span>Order Summary</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Cart Items */}
                <div className="space-y-3">
                  {cart.items.map((item) => (
                    <div key={item.id} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                      <div className="w-12 h-12 bg-gray-200 rounded-lg overflow-hidden flex-shrink-0">
                        {item.product.image ? (
                          <img
                            src={item.product.image}
                            alt={item.product.title}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center">
                            <ShoppingCart className="w-4 h-4 text-gray-400" />
                          </div>
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {item.product.brand} {item.product.title}
                        </p>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-gray-500">Qty: {item.quantity}</span>
                          <span className="text-sm font-semibold">${(item.price * item.quantity).toFixed(2)}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Order Totals */}
                <div className="border-t pt-4 space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Subtotal:</span>
                    <span>${getTotalPrice().toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Shipping:</span>
                    <span>{calculateShipping() === 0 ? 'FREE' : `$${calculateShipping().toFixed(2)}`}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Tax:</span>
                    <span>${calculateTax().toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-lg font-bold border-t pt-2">
                    <span>Total:</span>
                    <span className="text-chewy-blue">${calculateTotal().toFixed(2)}</span>
                  </div>
                </div>

                {/* Shipping Notice */}
                {getTotalPrice() < 49 && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                    <div className="flex items-start space-x-2">
                      <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                      <div className="text-sm">
                        <p className="font-medium text-blue-900">Almost there!</p>
                        <p className="text-blue-700">
                          Add ${(49 - getTotalPrice()).toFixed(2)} more for free shipping
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}
