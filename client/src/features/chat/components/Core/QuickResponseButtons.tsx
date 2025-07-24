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
  console.log('QuickResponseButtons: Rendering with tags:', tags, 'onTagClick:', !!onTagClick);
  
  if (!tags || tags.length === 0) {
    console.log('QuickResponseButtons: No tags provided');
    return null;
  }

  if (!onTagClick) {
    console.log('QuickResponseButtons: No onTagClick provided');
    return null;
  }

  const handleTagClick = (tag: string) => {
    console.log('QuickResponseButtons: Tag clicked:', tag);
    onTagClick(tag);
  };

  return (
    <div className="mt-4 space-y-3 relative z-10">
      {/* Buttons - One per line */}
      <div className="space-y-2">
        {tags.map((tag, index) => (
          <Button
            key={index}
            variant="outline"
            size="default"
            onClick={() => handleTagClick(tag)}
            className="w-full justify-between group relative z-10 pointer-events-auto"
            style={{ pointerEvents: 'auto' }}
          >
            <span className="truncate">{tag}</span>
            <ChevronRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
          </Button>
        ))}
      </div>
    </div>
  );
};
