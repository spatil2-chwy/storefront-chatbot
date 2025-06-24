import React, { useState, useEffect } from 'react';
import { useRoute, Link } from 'wouter';
import { ArrowLeft, Heart, RotateCcw, Truck, Undo } from 'lucide-react';
import Header from '@/components/Header';
import ChatWidget from '@/components/ChatWidget';
import { mockProducts } from '@/lib/mockData';
import { Product } from '../types';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';

export default function ProductDetail() {
  const [match, params] = useRoute('/product/:id');
  const [product, setProduct] = useState<Product | null>(null);
  const [selectedFlavor, setSelectedFlavor] = useState('');
  const [selectedSize, setSelectedSize] = useState('');
  const [selectedImage, setSelectedImage] = useState('');
  const [purchaseOption, setPurchaseOption] = useState('autoship');
  const [quantity, setQuantity] = useState('1');

  useEffect(() => {
    if (params?.id) {
      const foundProduct = mockProducts.find(p => p.id === parseInt(params.id));
      if (foundProduct) {
        setProduct(foundProduct);
        setSelectedFlavor(foundProduct.flavors[0] || '');
        setSelectedSize(foundProduct.sizes[0]?.name || '');
        setSelectedImage(foundProduct.images[0] || foundProduct.image);
      }
    }
  }, [params?.id]);

  if (!product) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <p className="text-center text-gray-500">Product not found</p>
        </div>
      </div>
    );
  }

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

  const selectedSizeData = product.sizes.find(size => size.name === selectedSize);
  const currentPrice = selectedSizeData?.price || product.price;
  const autoshipPrice = currentPrice * 0.95; // 5% discount

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="max-w-full mx-auto px-8 sm:px-12 lg:px-16 py-8">
        {/* Breadcrumb */}
        <nav className="flex mb-6 text-sm">
          <Link href="/" className="text-chewy-blue hover:underline flex items-center space-x-1">
            <ArrowLeft className="w-4 h-4" />
            <span>Back to search results for "grain free dog food"</span>
          </Link>
        </nav>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          {/* Product Images */}
          <div className="space-y-4">
            <div className="relative">
              <img 
                src={selectedImage} 
                alt={product.title}
                className="w-full h-96 object-cover rounded-xl"
              />
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
            <div className="flex space-x-2">
              {product.images.map((image, index) => (
                <img
                  key={index}
                  src={image}
                  alt={`Product view ${index + 1}`}
                  className={`w-16 h-16 object-cover rounded-lg cursor-pointer border-2 ${
                    selectedImage === image ? 'border-chewy-blue' : 'border-gray-300 hover:border-chewy-blue'
                  }`}
                  onClick={() => setSelectedImage(image)}
                />
              ))}
            </div>
          </div>

          {/* Product Details */}
          <div className="space-y-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">{product.title}</h1>
              <p className="text-sm text-gray-600">
                By <span className="text-chewy-blue hover:underline cursor-pointer">{product.brand}</span>
              </p>
              
              <div className="flex items-center mt-3">
                <div className="flex items-center">
                  <div className="flex">
                    {renderStars(product.rating)}
                  </div>
                  <span className="text-sm text-gray-600 ml-2">{product.rating}</span>
                  <span className="text-sm text-chewy-blue ml-2 hover:underline cursor-pointer">
                    {product.reviewCount} Ratings
                  </span>
                  <span className="text-sm text-gray-500 ml-2">56 Answered Questions</span>
                </div>
              </div>
            </div>

            {/* Flavor Selection */}
            <div>
              <h3 className="font-medium text-gray-900 mb-3">
                Flavor: <span className="text-chewy-blue">{selectedFlavor}</span>
              </h3>
              <div className="flex flex-wrap gap-2">
                {product.flavors.map((flavor) => (
                  <Button
                    key={flavor}
                    variant={selectedFlavor === flavor ? "default" : "outline"}
                    onClick={() => setSelectedFlavor(flavor)}
                    className={selectedFlavor === flavor ? "bg-chewy-blue hover:bg-blue-700" : ""}
                  >
                    {flavor}
                  </Button>
                ))}
              </div>
            </div>

            {/* Size Selection */}
            <div>
              <h3 className="font-medium text-gray-900 mb-3">
                Size: <span className="text-chewy-blue">{selectedSize}</span>
              </h3>
              <div className="grid grid-cols-2 gap-3">
                {product.sizes.map((size) => (
                  <Button
                    key={size.name}
                    variant={selectedSize === size.name ? "default" : "outline"}
                    onClick={() => setSelectedSize(size.name)}
                    className={`p-3 text-left h-auto flex flex-col items-start ${
                      selectedSize === size.name 
                        ? "bg-chewy-light-blue border-chewy-blue text-chewy-blue" 
                        : "hover:border-chewy-blue"
                    }`}
                  >
                    <div className="font-medium">{size.name}</div>
                    <div className="text-sm text-gray-600">{size.pricePerLb}</div>
                  </Button>
                ))}
              </div>
            </div>

            {/* Pricing Section */}
            <Card className="bg-gray-50">
              <CardContent className="p-6">
                <RadioGroup value={purchaseOption} onValueChange={setPurchaseOption}>
                  {/* Autoship Option */}
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
                        <span className="text-green-600 font-medium">Save 36% up to $201 on your first Autoship order. Details</span>
                      </div>
                      <div className="text-sm text-chewy-blue font-medium">
                        ${(autoshipPrice * 0.94).toFixed(2)} (-6%) future orders
                      </div>
                    </div>
                  )}

                  {/* Buy Once Option */}
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="buyonce" id="buyonce" />
                    <Label htmlFor="buyonce" className="font-medium cursor-pointer">Buy once</Label>
                  </div>
                  
                  {purchaseOption === 'buyonce' && (
                    <div className="ml-6 mt-2">
                      <div className="text-xl font-semibold text-gray-900">${currentPrice.toFixed(2)}</div>
                      <div className="text-sm text-gray-600">
                        <span>{selectedSizeData?.pricePerLb}</span>
                      </div>
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
                  <span>Set Up</span>
                  <RotateCcw className="w-4 h-4" />
                  <span>Autoship</span>
                </div>
              </Button>
            </div>

            {/* Similar Items */}
            <div className="border-t pt-6">
              <h3 className="font-semibold text-gray-900 mb-4">Try this similar item by Chewy</h3>
              <Card className="p-4 border border-gray-200">
                <div className="flex items-center space-x-4">
                  <div className="relative">
                    <Badge className="absolute -top-2 -left-2 bg-red-500 text-white text-xs">Deal</Badge>
                    <img 
                      src={mockProducts[0].image} 
                      alt="Similar product"
                      className="w-16 h-16 object-cover rounded-lg"
                    />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 text-sm">American Journey Limited...</h4>
                    <div className="flex items-center mt-1">
                      <div className="flex text-yellow-400 text-xs">
                        <span>★★★★★</span>
                      </div>
                      <span className="text-xs text-gray-600 ml-1">4.4 (3.5K)</span>
                    </div>
                    <div className="text-sm font-semibold text-gray-900 mt-1">$51.48</div>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        </div>
      </main>

      <ChatWidget 
        onProductFilter={() => {}} 
        onClearChat={() => {}} 
        chatContext={{ type: 'product', product: product }}
      />
    </div>
  );
}
