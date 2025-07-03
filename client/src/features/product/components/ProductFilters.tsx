import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/Cards/Card';
import { Checkbox } from '@/components/Checkboxes/Checkbox';
import { Label } from '@/components/Input/label';
import { Slider } from '@/components/Input/slider';
import { Badge } from '@/components/Display/Badge';

interface ProductFiltersProps {
  onFilterChange: (filters: any) => void;
}

export default function ProductFilters({ onFilterChange }: ProductFiltersProps) {
  const [selectedBrands, setSelectedBrands] = useState<string[]>(['By Chewy']);
  const [selectedBreedSizes, setSelectedBreedSizes] = useState<string[]>([]);
  const [priceRange, setPriceRange] = useState([5, 50]);

  const brands = [
    { name: 'By Chewy', count: null },
    { name: '360 Pet Nutrition', count: null },
    { name: 'ACANA', deal: true },
    { name: 'Addiction', count: null },
    { name: 'Against the Grain', count: null },
  ];

  const breedSizes = [
    'Extra Small Breeds',
    'Small Breeds',
    'Medium Breeds',
    'Large Breeds',
    'Giant Breeds',
    'All Breeds',
  ];

  const handleBrandChange = (brand: string, checked: boolean) => {
    const newBrands = checked
      ? [...selectedBrands, brand]
      : selectedBrands.filter(b => b !== brand);
    
    setSelectedBrands(newBrands);
    onFilterChange({ brands: newBrands, breedSizes: selectedBreedSizes, priceRange });
  };

  const handleBreedSizeChange = (breedSize: string, checked: boolean) => {
    const newBreedSizes = checked
      ? [...selectedBreedSizes, breedSize]
      : selectedBreedSizes.filter(bs => bs !== breedSize);
    
    setSelectedBreedSizes(newBreedSizes);
    onFilterChange({ brands: selectedBrands, breedSizes: newBreedSizes, priceRange });
  };

  const handlePriceRangeChange = (newRange: number[]) => {
    setPriceRange(newRange);
    onFilterChange({ brands: selectedBrands, breedSizes: selectedBreedSizes, priceRange: newRange });
  };

  return (
    <aside className="w-64 flex-shrink-0 space-y-6">
      {/* Brand Filter */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Brand</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {brands.map((brand) => (
            <div key={brand.name} className="flex items-center space-x-2">
              <Checkbox
                id={brand.name}
                checked={selectedBrands.includes(brand.name)}
                onCheckedChange={(checked) => handleBrandChange(brand.name, checked as boolean)}
              />
              <Label
                htmlFor={brand.name}
                className="text-sm text-gray-700 flex items-center space-x-2"
              >
                <span>{brand.name}</span>
                {brand.deal && (
                  <Badge className="bg-red-500 text-white text-xs">Deal</Badge>
                )}
              </Label>
            </div>
          ))}
          <button className="text-chewy-blue text-sm hover:underline">+ 300 more</button>
        </CardContent>
      </Card>

      {/* Breed Size Filter */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Breed Size</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {breedSizes.map((breedSize) => (
            <div key={breedSize} className="flex items-center space-x-2">
              <Checkbox
                id={breedSize}
                checked={selectedBreedSizes.includes(breedSize)}
                onCheckedChange={(checked) => handleBreedSizeChange(breedSize, checked as boolean)}
              />
              <Label htmlFor={breedSize} className="text-sm text-gray-700">
                {breedSize}
              </Label>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Product Weight Filter */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Product Weight</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between text-sm text-gray-600">
              <span>{priceRange[0]} lbs</span>
              <span>{priceRange[1]} lbs</span>
            </div>
            <Slider
              value={priceRange}
              onValueChange={handlePriceRangeChange}
              max={100}
              min={1}
              step={1}
              className="w-full"
            />
          </div>
        </CardContent>
      </Card>
    </aside>
  );
}
