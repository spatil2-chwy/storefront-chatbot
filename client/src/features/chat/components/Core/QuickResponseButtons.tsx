import React from 'react';
import { Button } from '../../../../ui/Buttons/Button';

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
    <div className="mt-3 flex flex-wrap gap-2">
      {tags.map((tag, index) => (
        <Button
          key={index}
          variant="outline"
          size="sm"
          onClick={() => onTagClick(tag)}
          className="bg-gradient-to-r from-blue-50 to-indigo-50 hover:from-blue-100 hover:to-indigo-100 border-blue-200 hover:border-blue-300 text-blue-700 hover:text-blue-800 px-4 py-2 text-sm font-medium rounded-full transition-all duration-200 shadow-sm hover:shadow-md transform hover:scale-105"
        >
          {tag}
        </Button>
      ))}
    </div>
  );
};
