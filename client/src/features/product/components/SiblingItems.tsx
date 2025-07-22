import React from 'react';
import { SiblingItem } from '../../../types';
import { Button } from '@/ui/Buttons/Button';
import { Badge } from '@/ui/Display/Badge';

interface SiblingItemsProps {
  siblingItems: SiblingItem[];
  currentVariant?: string;
  onVariantSelect: (siblingItem: SiblingItem) => void;
}

export default function SiblingItems({ siblingItems, currentVariant, onVariantSelect }: SiblingItemsProps) {
  if (!siblingItems || siblingItems.length === 0) {
    return null;
  }

  return (
    <div className="flex flex-wrap gap-2">
      {siblingItems.map((item) => {
        const isSelected = item.variant === currentVariant;
        const pricePerUnit = item.variant?.includes('lb') 
          ? `$${(item.price / parseFloat(item.variant.match(/(\d+(?:\.\d+)?)/)?.[1] || '1')).toFixed(2)}/lb`
          : item.variant?.includes('count')
          ? `$${(item.price / parseInt(item.variant.match(/(\d+)/)?.[1] || '1')).toFixed(2)}/count`
          : null;

        return (
          <Button
            key={item.id}
            variant={isSelected ? "default" : "outline"}
            size="sm"
            onClick={() => onVariantSelect(item)}
            className={`min-w-[120px] h-auto p-3 flex flex-col items-start space-y-1 ${
              isSelected 
                ? 'border-chewy-blue bg-chewy-blue text-white' 
                : 'border-gray-300 hover:border-chewy-blue hover:bg-gray-50'
            }`}
          >
            <div className="text-sm font-medium">{item.variant}</div>
            <div className="text-xs text-gray-600">
              ${item.price.toFixed(2)}
            </div>
            {pricePerUnit && (
              <div className="text-xs text-gray-500">
                {pricePerUnit}
              </div>
            )}
            {isSelected && (
              <Badge className="mt-1 text-xs bg-white text-chewy-blue">
                Selected
              </Badge>
            )}
          </Button>
        );
      })}
    </div>
  );
} 