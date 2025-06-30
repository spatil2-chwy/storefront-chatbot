import React from 'react';
import { SearchMatch } from '../types';
import { Badge } from '@/components/ui/badge';
import { Target, CheckCircle, Heart, Dog, Baby, Scale, Package, Shield, Pill, Utensils, Award } from 'lucide-react';

interface SearchMatchesProps {
  matches?: SearchMatch[];
  className?: string;
  showTitle?: boolean;
  maxMatches?: number;
}

export default function SearchMatches({ 
  matches, 
  className = "", 
  showTitle = true,
  maxMatches = 50
}: SearchMatchesProps) {
  if (!matches || matches.length === 0) {
    return null;
  }

  const formatMatchDisplay = (match: SearchMatch) => {
    // If the field contains a category (e.g., "Pet Type: Dog"), extract both parts
    if (match.field.includes(':')) {
      const [category, value] = match.field.split(':', 2);
      const cleanCategory = category.trim();
      const cleanValue = value.trim();
      
      // Map categories to more user-friendly labels
      const categoryLabels: { [key: string]: string } = {
        // New metadata-driven categories
        'Brands': 'Brand',
        'Categories': 'Category',
        'Ingredients': 'Ingredient',
        'Diet & Health': 'Diet',
        'Pet Types': 'Pet Type',
        'Product Forms': 'Form',
        'Life Stages': 'Life Stage',
        'Size/Weight': 'Size',
        };
      
      const displayCategory = categoryLabels[cleanCategory] || cleanCategory;
      
      return {
        category: cleanCategory,
        value: cleanValue,
        displayText: `${displayCategory}: ${cleanValue}`
      };
    }
    
    // Fallback for old format
    return {
      category: match.field,
      value: match.matched_terms.join(', '),
      displayText: match.matched_terms.join(', ')
    };
  };

  // Sort matches by confidence (highest first) - show all matches
  const sortedMatches = matches
    .sort((a, b) => b.confidence - a.confidence);

  // Group matches by category
  const groupedMatches = sortedMatches.reduce((acc, match) => {
    const { category, value, displayText } = formatMatchDisplay(match);
    const categoryKey = category;
    
    if (!acc[categoryKey]) {
      acc[categoryKey] = {
        category: categoryKey,
        values: [],
        confidence: match.confidence,
        field: match.field
      };
    }
    
    // Only add if not already present (avoid duplicates)
    if (!acc[categoryKey].values.includes(value)) {
      acc[categoryKey].values.push(value);
      // Keep the highest confidence for this category
      acc[categoryKey].confidence = Math.max(acc[categoryKey].confidence, match.confidence);
    }
    
    return acc;
  }, {} as Record<string, { category: string; values: string[]; confidence: number; field: string }>);

  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 0.8) return 'bg-green-100 text-green-800 border-green-200';
    if (confidence >= 0.6) return 'bg-blue-100 text-blue-800 border-blue-200';
    return 'bg-gray-100 text-gray-700 border-gray-200';
  };

  const getConfidenceIcon = (confidence: number) => {
    if (confidence >= 0.8) {
      return <CheckCircle className="w-3 h-3 fill-current" />;
    }
    return <Target className="w-3 h-3" />;
  };

  const getCategoryIcon = (field: string) => {
    // New metadata-driven categories
    if (field.includes('Brands')) return <Award className="w-3 h-3" />;
    if (field.includes('Categories')) return <Package className="w-3 h-3" />;
    if (field.includes('Ingredients')) return <Utensils className="w-3 h-3" />;
    if (field.includes('Diet & Health')) return <Shield className="w-3 h-3" />;
    if (field.includes('Pet Types')) return <Dog className="w-3 h-3" />;
    if (field.includes('Product Forms')) return <Pill className="w-3 h-3" />;
    if (field.includes('Life Stages')) return <Baby className="w-3 h-3" />;
    if (field.includes('Size/Weight')) return <Scale className="w-3 h-3" />;
    
    // Legacy categories (for backward compatibility)
    if (field.includes('Pet Type')) return <Dog className="w-3 h-3" />;
    if (field.includes('Life Stage')) return <Baby className="w-3 h-3" />;
    if (field.includes('Brand')) return <Award className="w-3 h-3" />;
    if (field.includes('Product Type')) return <Package className="w-3 h-3" />;
    if (field.includes('Health Concern')) return <Heart className="w-3 h-3" />;
    if (field.includes('Form')) return <Pill className="w-3 h-3" />;
    if (field.includes('Diet/Special Needs')) return <Shield className="w-3 h-3" />;
    if (field.includes('Flavor')) return <Utensils className="w-3 h-3" />;
    
    return <Target className="w-3 h-3" />;
  };

  return (
    <div className={`space-y-2 ${className}`}>
      {showTitle && (
        <div className="flex items-center space-x-1 text-xs text-gray-600">
          <Target className="w-3 h-3" />
          <span>Matches your search for:</span>
        </div>
      )}
      
      <div className="space-y-1">
        {Object.values(groupedMatches).map((group, index) => {
          // Map categories to more user-friendly labels
          const categoryLabels: { [key: string]: string } = {
            // New metadata-driven categories
            'Brands': 'Brand',
            'Categories': 'Category',
            'Ingredients': 'Ingredient',
            'Diet & Health': 'Diet',
            'Pet Types': 'Pet Type',
            'Product Forms': 'Form',
            'Life Stages': 'Life Stage',
            'Size/Weight': 'Size',
            
            // Legacy categories (for backward compatibility)
            'Pet Type': 'Pet Type',
            'Life Stage': 'Life Stage',
            'Brand': 'Brand',
            'Product Type': 'Item',
            'Health Concern': 'Health',
            'Form': 'Form',
            'Diet/Special Needs': 'Diet',
            'Flavor': 'Flavor'
          };
          
          const displayCategory = categoryLabels[group.category] || group.category;
          const displayText = `${displayCategory}: ${group.values.join(', ')}`;
          
          return (
            <div key={index} className="flex items-center">
              <Badge
                variant="outline"
                className={`text-xs px-2 py-0.5 ${getConfidenceColor(group.confidence)} font-normal`}
                title={`${displayCategory}: ${group.values.join(', ')} (${Math.round(group.confidence * 100)}% confidence)`}
              >
                <div className="flex items-center space-x-1">
                  {getCategoryIcon(group.field)}
                  <span className="text-xs">
                    {displayText}
                  </span>
                </div>
              </Badge>
            </div>
          );
        })}
      </div>
    </div>
  );
} 