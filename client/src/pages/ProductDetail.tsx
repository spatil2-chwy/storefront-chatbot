import React, { useState, useEffect } from 'react';
import { useRoute, Link } from 'wouter';
import { ArrowLeft, Heart, RotateCcw, Truck, Undo, Loader2, Image as ImageIcon } from 'lucide-react';
import Header from '@/components/Header';
import ChatWidget from '@/components/ChatWidget';
import SearchMatches from '@/components/SearchMatches';
import { useProduct } from '@/hooks/useProducts';
import { Product } from '../types';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { useGlobalChat } from '@/contexts/ChatContext';

export default function ProductDetail() {
  const [match, params] = useRoute('/product/:id');
  const [selectedImage, setSelectedImage] = useState('');
  const [purchaseOption, setPurchaseOption] = useState('autoship');
  const [quantity, setQuantity] = useState('1');

  // Use the custom hook to fetch product data
  const { product, loading, error } = useProduct(params?.id ? parseInt(params.id) : null);
  
  // Get search query from global state
  const { currentSearchQuery, setShouldAutoOpen } = useGlobalChat();

  const currentPrice = product?.price || 0;
  const autoshipPrice = product?.autoshipPrice || 0;
  const hasAutoship = autoshipPrice > 0;

  // Auto-open chatbot when navigating to this page
  useEffect(() => {
    // Check if user had closed the chatbot before
    const wasChatClosed = localStorage.getItem('chatClosed') === 'true';
    if (wasChatClosed) {
      setShouldAutoOpen(true);
      localStorage.removeItem('chatClosed'); // Reset the flag
    }
  }, [setShouldAutoOpen]);

  // Set default purchase option based on autoship availability
  useEffect(() => {
    if (product) {
      setPurchaseOption(hasAutoship ? 'autoship' : 'buyonce');
    }
  }, [product, hasAutoship]);

  useEffect(() => {
    if (product && product.images && product.images.length > 0) {
      setSelectedImage(product.images[0]);
    } else if (product && product.image) {
      setSelectedImage(product.image);
    }
  }, [product]);

  const renderStars = (rating: number) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;
    
    for (let i = 0; i < fullStars; i++) {
      stars.push(<span key={i} className="text-yellow-400">★</span>);
    }
    
    if (hasHalfStar) {
      stars.push(<span key="half" className="text-yellow-400">☆</span>);
    }
    
    const remainingStars = 5 - Math.ceil(rating);
    for (let i = 0; i < remainingStars; i++) {
      stars.push(<span key={`empty-${i}`} className="text-gray-300">☆</span>);
    }
    
    return stars;
  };

  const renderImage = (imageSrc: string, altText: string, className: string) => {
    if (!imageSrc || imageSrc === '') {
      return (
        <div className={`${className} bg-gray-100 flex items-center justify-center`}>
          <div className="text-center">
            <ImageIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">Image not available</p>
          </div>
        </div>
      );
    }

    return (
      <img 
        src={imageSrc} 
        alt={altText}
        className={className}
        onError={(e) => {
          const target = e.target as HTMLImageElement;
          target.style.display = 'none';
          target.nextElementSibling?.classList.remove('hidden');
        }}
      />
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="max-w-full mx-auto px-8 sm:px-12 lg:px-16 py-8">
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-chewy-blue" />
            <span className="ml-2 text-gray-600">Loading product...</span>
          </div>
        </main>
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="max-w-full mx-auto px-8 sm:px-12 lg:px-16 py-8">
          <div className="text-center py-12">
            <p className="text-red-500 text-lg">
              {error || 'Product not found'}
            </p>
            <p className="text-gray-400 text-sm mt-2">Please try again or go back to search results.</p>
            <Link href="/" className="inline-block mt-4 text-chewy-blue hover:underline">
              Back to search results
            </Link>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="max-w-full mx-auto px-8 sm:px-12 lg:px-16 py-8">
        {/* Breadcrumb */}
        <nav className="flex mb-6 text-sm">
          <Link href="/" className="text-chewy-blue hover:underline flex items-center space-x-1">
            <ArrowLeft className="w-4 h-4" />
            <span>Back to search results for "{currentSearchQuery}"</span>
          </Link>
        </nav>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          {/* Product Images */}
          <div className="space-y-4">
            <div className="relative">
              {renderImage(selectedImage || product?.image || '', product.title || 'Product', "w-full h-96 object-cover rounded-xl")}
              {/* Fallback image (hidden by default) */}
              <div className="w-full h-96 bg-gray-100 flex items-center justify-center rounded-xl hidden">
                <div className="text-center">
                  <ImageIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">Image not available</p>
                </div>
              </div>
              {product.deal && (
                <div className="absolute top-4 left-4">
                  <Badge className="bg-red-500 text-white">Deal</Badge>
                </div>
              )}
              <button className="absolute top-4 right-4 p-3 rounded-full bg-white shadow-lg hover:bg-gray-50">
                <Heart className="w-5 h-5 text-gray-400" />
              </button>
            </div>
            
            {/* Thumbnail Images */}
            {product.images && product.images.length > 1 && (
              <div className="flex space-x-2">
                {product.images.map((image, index) => (
                  <div key={index} className="relative">
                    <div 
                      onClick={() => setSelectedImage(image)}
                      className="cursor-pointer"
                    >
                      {renderImage(image, `Product view ${index + 1}`, `w-16 h-16 object-cover rounded-lg border-2 ${
                        selectedImage === image ? 'border-chewy-blue' : 'border-gray-300 hover:border-chewy-blue'
                      }`)}
                      {/* Fallback thumbnail (hidden by default) */}
                      <div className={`w-16 h-16 bg-gray-100 flex items-center justify-center rounded-lg border-2 hidden ${
                        selectedImage === image ? 'border-chewy-blue' : 'border-gray-300 hover:border-chewy-blue'
                      }`}>
                        <ImageIcon className="w-6 h-6 text-gray-400" />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
            
            {/* Show main product image as thumbnail if no additional images */}
            {(!product.images || product.images.length <= 1) && product.image && (
              <div className="flex space-x-2">
                <div className="relative">
                  <div className="cursor-pointer">
                    {renderImage(product.image, product.title || 'Product', `w-16 h-16 object-cover rounded-lg border-2 border-chewy-blue`)}
                    {/* Fallback thumbnail (hidden by default) */}
                    <div className="w-16 h-16 bg-gray-100 flex items-center justify-center rounded-lg border-2 border-chewy-blue hidden">
                      <ImageIcon className="w-6 h-6 text-gray-400" />
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Product Details */}
          <div className="space-y-6">
            <div>
              <div className="flex items-center space-x-3 mb-2">
                <Badge variant="outline" className="text-xs font-medium text-gray-600 border-gray-300">
                  {product.brand}
                </Badge>
                {product.deal && (
                  <Badge className="bg-red-500 text-white text-xs font-medium">Deal</Badge>
                )}
              </div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">{product.title}</h1>
              
              {/* Search Matches - show detailed match information */}
              {product.search_matches && product.search_matches.length > 0 && (
                <Card className="bg-blue-50 border-blue-200 mb-4">
                  <CardContent className="p-4">
                    <SearchMatches 
                      matches={product.search_matches} 
                      showTitle={true}
                      maxMatches={10}
                    />
                  </CardContent>
                </Card>
              )}
              
              <div className="flex items-center mt-3">
                <div className="flex items-center">
                  <div className="flex">
                    {renderStars(product.rating || 0)}
                  </div>
                  <span className="text-sm text-gray-600 ml-2">{product.rating?.toFixed(1)}</span>
                  <span className="text-sm text-chewy-blue ml-2 hover:underline cursor-pointer">
                    {product.reviewCount} Ratings
                  </span>
                  <span className="text-sm text-gray-500 ml-2">56 Answered Questions</span>
                </div>
              </div>
            </div>

            {/* Pricing Section */}
            <Card className="bg-gray-50">
              <CardContent className="p-6">
                <RadioGroup value={purchaseOption} onValueChange={setPurchaseOption}>
                  {/* Autoship Option - only show if available */}
                  {hasAutoship && (
                    <>
                      <div className="flex items-center space-x-2 mb-4">
                        <RadioGroupItem value="autoship" id="autoship" />
                        <Label htmlFor="autoship" className="flex items-center space-x-2 cursor-pointer">
                          <RotateCcw className="w-4 h-4 text-chewy-blue" />
                          <span className="font-medium">Autoship</span>
                          <span className="text-sm text-gray-600">Easy, repeat deliveries</span>
                        </Label>
                      </div>
                      
                      {purchaseOption === 'autoship' && (
                        <div className="ml-6 mb-4">
                          <div className="text-2xl font-bold text-gray-900">${autoshipPrice.toFixed(2)}</div>
                          <div className="text-sm text-gray-600">
                            <span className="text-green-600 font-medium">Save 5% on your first Autoship order. Details</span>
                          </div>
                          <div className="text-sm text-chewy-blue font-medium">
                            ${(autoshipPrice * 0.95).toFixed(2)} (-5%) future orders
                          </div>
                        </div>
                      )}
                    </>
                  )}

                  {/* Buy Once Option */}
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="buyonce" id="buyonce" />
                    <Label htmlFor="buyonce" className="font-medium cursor-pointer">Buy once</Label>
                  </div>
                  
                  {purchaseOption === 'buyonce' && (
                    <div className="ml-6 mt-2">
                      <div className="text-xl font-semibold text-gray-900">${currentPrice.toFixed(2)}</div>
                      {product.originalPrice && product.originalPrice > currentPrice && (
                        <div className="text-sm text-gray-500 line-through">${product.originalPrice.toFixed(2)}</div>
                      )}
                    </div>
                  )}
                </RadioGroup>
              </CardContent>
            </Card>

            {/* Quantity and Add to Cart */}
            <div className="space-y-4">
              <div className="flex items-center space-x-4">
                <Label className="font-medium text-gray-900">Quantity:</Label>
                <Select value={quantity} onValueChange={setQuantity}>
                  <SelectTrigger className="w-20">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {[1, 2, 3, 4, 5].map(num => (
                      <SelectItem key={num} value={num.toString()}>{num}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <span className="text-sm text-gray-600">in Stock</span>
              </div>
              
              <div className="text-sm text-green-600 font-medium flex items-center space-x-1">
                <Truck className="w-4 h-4" />
                <span>FREE 1-3 day delivery</span>
              </div>
              
              <div className="text-sm text-gray-600 flex items-center space-x-1">
                <Undo className="w-4 h-4" />
                <span>Free 365-day returns Details</span>
              </div>

              <Button className="w-full bg-chewy-blue hover:bg-blue-700 text-white py-4 px-6 rounded-xl font-semibold text-lg">
                <div className="flex items-center justify-center space-x-2">
                  {hasAutoship ? (
                    <>
                      <span>Set Up</span>
                      <RotateCcw className="w-4 h-4" />
                      <span>Autoship</span>
                    </>
                  ) : (
                    <span>Add to Cart</span>
                  )}
                </div>
              </Button>
            </div>

            {/* Product Description */}
            {product.description && (
              <div className="border-t pt-6">
                <h3 className="font-semibold text-gray-900 mb-4">Product Description</h3>
                <p className="text-gray-600 text-sm leading-relaxed">{product.description}</p>
              </div>
            )}

            {/* Keywords/Tags */}
            {product.keywords && product.keywords.length > 0 && (
              <div className="border-t pt-6">
                <h3 className="font-semibold text-gray-900 mb-4">Product Ingredients</h3>
                <div className="flex flex-wrap gap-2">
                  {product.keywords.map((keyword, index) => (
                    <Badge key={index} variant="secondary" className="text-xs">
                      {keyword}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      <ChatWidget 
        onClearChat={() => {}} 
        chatContext={{ type: 'product', product: product }}
      />
    </div>
  );
}
