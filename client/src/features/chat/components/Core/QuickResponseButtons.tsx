import React from 'react';
import { Button } from '../../../../ui/Buttons/Button';
import { ChevronRight } from 'lucide-react';

interface QuickResponseButtonsProps {
  tags: string[];
  onTagClick: (tag: string) => void;
}

export const QuickResponseButtons: React.FC<QuickResponseButtonsProps> = ({
  tags,
  onTagClick,
}) => {
  if (!tags || tags.length === 0) {
    return null;
  }

  return (
    <div className="mt-4 space-y-3">
      {/* Buttons - One per line */}
      <div className="space-y-2">
        {tags.map((tag, index) => (
          <Button
            key={index}
            variant="outline"
            size="default"
            onClick={() => onTagClick(tag)}
            className="group relative bg-white hover:bg-blue-50 border-gray-200 hover:border-blue-300 text-gray-700 hover:text-blue-700 px-4 py-2.5 text-sm font-medium rounded-md transition-all duration-200 shadow-sm hover:shadow-md transform hover:scale-105 w-full justify-between"
          >
            <span className="truncate">{tag}</span>
            <ChevronRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
          </Button>
        ))}
      </div>
    </div>
  );
};
