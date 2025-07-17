import React from 'react';
import { Button } from '../../../../ui/Buttons/Button';
import { PetProfileInfo } from '../../../../types';

interface PetProfileProps {
  petInfo: PetProfileInfo;
  onLooksGood: () => void;
  onEditInfo: () => void;
}

export const PetProfile: React.FC<PetProfileProps> = ({
  petInfo,
  onLooksGood,
  onEditInfo,
}) => {
  const formatGender = (gender: string) => {
    if (gender === 'MALE') return 'Male';
    if (gender === 'FMLE') return 'Female';
    return gender;
  };

  const formatLifeStage = (lifeStage: string) => {
    if (lifeStage === 'P') return 'Puppy/Kitten';
    if (lifeStage === 'A') return 'Adult';
    if (lifeStage === 'S') return 'Senior';
    return lifeStage;
  };

  const formatBirthday = (birthday: string | null) => {
    if (!birthday) return 'Unknown';
    try {
      const date = new Date(birthday);
      return date.toLocaleDateString('en-US', {
        month: '2-digit',
        day: '2-digit',
        year: 'numeric'
      });
    } catch {
      return 'Unknown';
    }
  };

  const formatWeight = (weight: number) => {
    if (!weight || weight <= 0) return 'Unknown';
    return `${weight} lbs`;
  };

  return (
    <div className="space-y-4">
      {/* Pet Information Header */}
      <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-4 border border-purple-200">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white text-xl font-medium">
            🐾
          </div>
          <div>
            <h3 className="font-bold text-gray-900 text-xl">
              {petInfo.name}
            </h3>
            <p className="text-sm text-gray-600 font-medium">
              {petInfo.breed && petInfo.breed.toLowerCase() !== 'unknown' ? petInfo.breed : ''} {petInfo.type}
            </p>
          </div>
        </div>

        {/* Pet Information Grid */}
        <div className="grid grid-cols-1 gap-3 text-sm">
          <div className="flex items-center justify-between py-2 border-b border-purple-100">
            <span className="font-semibold text-gray-700">Sex:</span>
            <span className="text-gray-900">{formatGender(petInfo.gender)}</span>
          </div>
          <div className="flex items-center justify-between py-2 border-b border-purple-100">
            <span className="font-semibold text-gray-700">Type:</span>
            <span className="text-gray-900">{petInfo.type}</span>
          </div>
          {petInfo.breed && petInfo.breed.toLowerCase() !== 'unknown' && (
            <div className="flex items-center justify-between py-2 border-b border-purple-100">
              <span className="font-semibold text-gray-700">Breed:</span>
              <span className="text-gray-900">{petInfo.breed}</span>
            </div>
          )}
          {petInfo.life_stage && petInfo.life_stage.toLowerCase() !== 'unknown' && (
            <div className="flex items-center justify-between py-2 border-b border-purple-100">
              <span className="font-semibold text-gray-700">Life Stage:</span>
              <span className="text-gray-900">{formatLifeStage(petInfo.life_stage)}</span>
            </div>
          )}
          <div className="flex items-center justify-between py-2 border-b border-purple-100">
            <span className="font-semibold text-gray-700">Born:</span>
            <span className="text-gray-900">{formatBirthday(petInfo.birthday)}</span>
          </div>
          <div className="flex items-center justify-between py-2 border-b border-purple-100">
            <span className="font-semibold text-gray-700">Weight:</span>
            <span className="text-gray-900">{formatWeight(petInfo.weight)}</span>
          </div>
          <div className="flex items-center justify-between py-2">
            <span className="font-semibold text-gray-700">Allergies:</span>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
              petInfo.allergies 
                ? 'bg-red-100 text-red-800' 
                : 'bg-green-100 text-green-800'
            }`}>
              {petInfo.allergies ? 'Yes' : 'None'}
            </span>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col space-y-3">
        <Button
          onClick={onLooksGood}
          className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white"
        >
          Looks good! Let's find something for {petInfo.name}
        </Button>
        <Button
          variant="outline"
          onClick={onEditInfo}
          className="w-full"
        >
          Edit information
        </Button>
      </div>
    </div>
  );
}; 