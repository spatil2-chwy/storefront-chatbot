import React from 'react';
import ProductCard from './ProductCard';
import { Product } from '../../../types';
import { Card, CardContent } from '@/ui/Cards/Card';
import { ChevronRight } from 'lucide-react';
import LandingCarousel from '@/components/LandingCarousel';

interface LandingCategory {
  name: string;
  description: string;
  search_query: string;
  products: Product[];
}

interface LandingProductsData {
  categories: {
    [key: string]: LandingCategory;
  };
  generated_at: string;
}

interface LandingProductsProps {
  data: LandingProductsData;
  onCategoryClick: (searchQuery: string) => void;
}

export default function LandingProducts({ data, onCategoryClick }: LandingProductsProps) {
  const categoryOrder = [
    'dog_food',
    'cat_food', 
    'dog_toys',
    'dog_beds',
    'dog_treats',
    'cat_litter',
    'dog_health',
    'cat_toys'
  ];

  return (
    <div className="space-y-12">
      {/* Hero Carousel */}
      <section>
        <LandingCarousel />
      </section>

      {/* Category Sections */}
      {categoryOrder.map((categoryKey) => {
        const category = data.categories[categoryKey];
        if (!category || !category.products || category.products.length === 0) {
          return null;
        }

        return (
          <section key={categoryKey}>
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{category.name}</h2>
                <p className="text-gray-600 mt-1">{category.description}</p>
              </div>
              <button
                onClick={() => onCategoryClick(category.search_query)}
                className="flex items-center space-x-1 text-chewy-blue hover:text-chewy-dark-blue font-medium transition-colors"
              >
                <span>View all {category.name}</span>
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {category.products.map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          </section>
        );
      })}
    </div>
  );
} 