import React from 'react';
import { calculateLifeStage, calculatePetAge, formatAgeDisplay, getLifeStageColor, LifeStageInfo } from '../lib/utils/life-stage-calculator';
import { Badge } from '../ui/Display/Badge';
import { Info } from 'lucide-react';

interface LifeStageDisplayProps {
  petType: string;
  birthday: string | null;
  legacyStage?: string;
  showAge?: boolean;
  className?: string;
}

export const LifeStageDisplay: React.FC<LifeStageDisplayProps> = ({
  petType,
  birthday,
  legacyStage,
  showAge = true,
  className = ""
}) => {
  const lifeStage = calculateLifeStage(petType, birthday, legacyStage);
  const ageInfo = calculatePetAge(birthday);
  const colorClasses = getLifeStageColor(lifeStage.stage);

  if (!lifeStage || lifeStage.stage === 'unknown') {
    return (
      <div className={`flex items-center space-x-2 ${className}`}>
        <Badge variant="secondary" className="text-gray-600 bg-gray-100 border-gray-200">
          Unknown
        </Badge>
        {showAge && (
          <span className="text-sm text-gray-500">
            Age unknown
          </span>
        )}
      </div>
    );
  }

  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      <Badge variant="secondary" className={`border ${colorClasses}`}>
        {lifeStage.label}
        {lifeStage.isEstimated && (
          <Info className="h-3 w-3 ml-1" />
        )}
      </Badge>
      {showAge && ageInfo && (
        <span className="text-sm text-gray-600">
          {formatAgeDisplay(ageInfo)}
        </span>
      )}
    </div>
  );
}; 