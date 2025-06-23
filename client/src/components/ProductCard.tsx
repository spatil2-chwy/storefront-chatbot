import { Link } from 'wouter';
import { Heart, RotateCcw } from 'lucide-react';
import { Product } from '@shared/schema';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface ProductCardProps {
  product: Product;
}

export default function ProductCard({ product }: ProductCardProps) {
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

  return (
    <Link href={`/product/${product.id}`}>
      <Card className="bg-white rounded-xl shadow-sm hover:shadow-lg transition-shadow duration-300 overflow-hidden cursor-pointer">
        <div className="relative">
          <img 
            src={product.image} 
            alt={product.title}
            className="w-full h-48 object-cover"
          />
          {product.deal && (
            <div className="absolute top-2 left-2">
              <Badge className="bg-red-500 text-white text-xs font-medium">Deal</Badge>
            </div>
          )}
          <button className="absolute top-2 right-2 p-2 rounded-full bg-white shadow-md hover:bg-gray-50">
            <Heart className="w-4 h-4 text-gray-400" />
          </button>
        </div>
        
        <CardContent className="p-4">
          <h3 className="font-medium text-gray-900 mb-2 line-clamp-2 text-sm">
            {product.title}
          </h3>
          
          <div className="flex items-center mb-2">
            <div className="flex items-center">
              <div className="flex text-sm">
                {renderStars(product.rating)}
              </div>
              <span className="text-sm text-gray-600 ml-2">{product.rating}</span>
              <span className="text-xs text-gray-500 ml-1">
                ({product.reviewCount > 1000 ? `${(product.reviewCount / 1000).toFixed(1)}K` : product.reviewCount})
              </span>
            </div>
          </div>
          
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <span className="text-lg font-semibold text-gray-900">${product.price}</span>
              {product.originalPrice && (
                <span className="text-sm text-gray-500 line-through">${product.originalPrice}</span>
              )}
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-chewy-blue font-medium">${product.autoshipPrice}</span>
              <div className="flex items-center space-x-1">
                <RotateCcw className="w-3 h-3 text-chewy-blue" />
                <span className="text-xs text-chewy-blue font-medium">Autoship</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
