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
          className="bg-white hover:bg-blue-50 border-blue-200 text-blue-700 hover:text-blue-800 hover:border-blue-300 px-3 py-1 text-xs font-medium rounded-full transition-colors"
        >
          {tag}
        </Button>
      ))}
    </div>
  );
};
