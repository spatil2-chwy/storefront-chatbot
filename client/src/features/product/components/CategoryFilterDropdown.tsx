import React, { useState, useMemo, useRef, useEffect } from 'react';
import { ChevronDown, X } from 'lucide-react';
import { Button } from '@/ui/Buttons/Button';
import { Checkbox } from '@/ui/Checkboxes/Checkbox';
import { Label } from '@/ui/Input/Label';
import { Badge } from '@/ui/Display/Badge';
import { Product } from '../../../types';

interface CategoryFilterDropdownProps {
  products: Product[];
  selectedCategories: string[];
  onCategoryChange: (categories: string[]) => void;
  className?: string;
}

export default function CategoryFilterDropdown({
  products,
  selectedCategories,
  onCategoryChange,
  className = ""
}: CategoryFilterDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [showAllSelected, setShowAllSelected] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setShowAllSelected(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Extract all unique matched values from search matches
  const availableCategories = useMemo(() => {
    const categories = new Set<string>();
    
    products.forEach(product => {
      if (product.search_matches) {
        product.search_matches.forEach(match => {
          if (match.field.includes(':')) {
            const [category, value] = match.field.split(':', 2);
            if (value && value.trim()) {
              // Special handling for excluded ingredients - show as "no X" format
              if (category.trim() === 'Excluded Ingredients') {
                categories.add(`${value.trim()}-Free`);
              } else {
                categories.add(value.trim());
              }
            }
          }
        });
      }
    });
    
    return Array.from(categories).sort();
  }, [products]);

  const handleCategoryToggle = (category: string, checked: boolean) => {
    const newCategories = checked
      ? [...selectedCategories, category]
      : selectedCategories.filter(c => c !== category);
    onCategoryChange(newCategories);
  };

  const handleToggleAll = (checked: boolean) => {
    if (checked) {
      onCategoryChange(availableCategories);
    } else {
      onCategoryChange([]);
    }
  };

  const allSelected = availableCategories.length > 0 && selectedCategories.length === availableCategories.length;
  const someSelected = selectedCategories.length > 0 && selectedCategories.length < availableCategories.length;

  // Use the category name directly from search matches
  const getCategoryDisplayName = (category: string): string => {
    return category;
  };

  const displayText = selectedCategories.length === 0 
    ? "Filter by matches" 
    : selectedCategories.length === 1
    ? getCategoryDisplayName(selectedCategories[0])
    : `${selectedCategories.length} selected`;

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      <Button
        variant="outline"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full justify-between h-9 px-3 text-sm"
      >
        <span className="truncate">{displayText}</span>
        <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </Button>

      {isOpen && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-md shadow-lg z-50 min-w-[200px] max-h-80 overflow-hidden">
          {/* Header */}
          <div className="p-3 border-b border-gray-100 bg-gray-50">
            <div className="flex items-center space-x-3">
              <Checkbox
                id="select-all"
                checked={allSelected}
                ref={(el) => {
                  if (el) {
                    (el as HTMLInputElement).indeterminate = someSelected;
                  }
                }}
                onCheckedChange={handleToggleAll}
                className="flex-shrink-0"
              />
              <Label
                htmlFor="select-all"
                className="text-sm font-medium text-gray-700 cursor-pointer flex-1"
              >
                Search Matches
              </Label>
            </div>
            
            {/* Selected items display */}
            {selectedCategories.length > 0 && (
              <div className="mt-2">
                <div className="flex flex-wrap gap-1">
                  {(showAllSelected ? selectedCategories : selectedCategories.slice(0, 3)).map((category) => (
                    <Badge
                      key={category}
                      variant="secondary"
                      className="text-xs px-2 py-0.5 bg-blue-100 text-blue-800"
                    >
                      {getCategoryDisplayName(category)}
                    </Badge>
                  ))}
                  {!showAllSelected && selectedCategories.length > 3 && (
                    <button
                      onClick={() => setShowAllSelected(true)}
                      className="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 hover:bg-gray-200 rounded-md transition-colors"
                    >
                      +{selectedCategories.length - 3} more
                    </button>
                  )}
                  {showAllSelected && selectedCategories.length > 3 && (
                    <button
                      onClick={() => setShowAllSelected(false)}
                      className="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 hover:bg-gray-200 rounded-md transition-colors"
                    >
                      Show less
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>
          
          {/* Categories list */}
          <div className="max-h-60 overflow-y-auto">
            {availableCategories.length === 0 ? (
              <div className="text-sm text-gray-500 py-4 text-center">
                No matches found
              </div>
            ) : (
              <div className="py-1">
                {availableCategories.map((category) => (
                  <div 
                    key={category} 
                    className="flex items-center space-x-3 px-3 py-2 hover:bg-gray-50 cursor-pointer"
                    onClick={() => handleCategoryToggle(category, !selectedCategories.includes(category))}
                  >
                    <Checkbox
                      id={category}
                      checked={selectedCategories.includes(category)}
                      onCheckedChange={(checked) => handleCategoryToggle(category, checked as boolean)}
                      className="flex-shrink-0"
                    />
                    <Label
                      htmlFor={category}
                      className="text-sm text-gray-700 cursor-pointer flex-1 truncate"
                    >
                      {getCategoryDisplayName(category)}
                    </Label>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
} 