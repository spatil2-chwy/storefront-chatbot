import React, { useState } from 'react';
import { Button } from '../../../../ui/Buttons/Button';
import { Input } from '../../../../ui/Input/Input';
import { Label } from '../../../../ui/Input/Label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../../../ui/Selects/Select';
import { PetProfileInfo } from '../../../../types';

interface PetProfileProps {
  petInfo: PetProfileInfo;
  onLooksGood: () => void;
  onEditInfo: () => void;
  onSave?: (updatedPet: PetProfileInfo) => void;
  onCancel?: () => void;
  isEditing?: boolean;
}

export const PetProfile: React.FC<PetProfileProps> = ({
  petInfo,
  onLooksGood,
  onEditInfo,
  onSave,
  onCancel,
  isEditing = false,
}) => {
  const [formData, setFormData] = useState<PetProfileInfo>(petInfo);
  const [isLoading, setIsLoading] = useState(false);

  // Update form data when petInfo changes
  React.useEffect(() => {
    setFormData(petInfo);
  }, [petInfo]);

  const handleInputChange = (field: keyof PetProfileInfo, value: string | number | boolean) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSave = async () => {
    if (!onSave) return;
    
    setIsLoading(true);
    try {
      await onSave(formData);
    } finally {
      setIsLoading(false);
    }
  };

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

  const renderField = (label: string, value: string | number, field?: keyof PetProfileInfo) => {
    if (isEditing && field) {
      if (field === 'gender') {
        return (
          <Select
            value={formData.gender}
            onValueChange={(value) => handleInputChange('gender', value)}
          >
            <SelectTrigger className="w-24">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="MALE">Male</SelectItem>
              <SelectItem value="FMLE">Female</SelectItem>
            </SelectContent>
          </Select>
        );
      } else if (field === 'type') {
        return (
          <Select
            value={formData.type}
            onValueChange={(value) => handleInputChange('type', value)}
          >
            <SelectTrigger className="w-24">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="DOG">Dog</SelectItem>
              <SelectItem value="CAT">Cat</SelectItem>
              <SelectItem value="BIRD">Bird</SelectItem>
              <SelectItem value="FISH">Fish</SelectItem>
              <SelectItem value="RABBIT">Rabbit</SelectItem>
              <SelectItem value="HAMSTER">Hamster</SelectItem>
              <SelectItem value="OTHER">Other</SelectItem>
            </SelectContent>
          </Select>
        );
      } else if (field === 'life_stage') {
        return (
          <Select
            value={formData.life_stage}
            onValueChange={(value) => handleInputChange('life_stage', value)}
          >
            <SelectTrigger className="w-28">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="P">Puppy/Kitten</SelectItem>
              <SelectItem value="A">Adult</SelectItem>
              <SelectItem value="S">Senior</SelectItem>
            </SelectContent>
          </Select>
        );
      } else if (field === 'weight') {
        return (
          <Input
            type="number"
            value={formData.weight}
            onChange={(e) => handleInputChange('weight', parseFloat(e.target.value) || 0)}
            className="w-20"
            placeholder="lbs"
          />
        );
      } else if (field === 'breed') {
        return (
          <Input
            value={formData.breed}
            onChange={(e) => handleInputChange('breed', e.target.value)}
            className="w-28"
            placeholder="Enter breed"
          />
        );
      } else if (field === 'name') {
        return (
          <Input
            value={formData.name}
            onChange={(e) => handleInputChange('name', e.target.value)}
            className="w-32"
            placeholder="Enter name"
          />
        );
      }
    }
    
    return <span className="text-gray-900">{value}</span>;
  };

  return (
    <div className="space-y-4">
      {/* Pet Information Header */}
      <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-4 border border-purple-200">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white text-xl font-medium">
            🐾
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="font-bold text-gray-900 text-xl">
              {isEditing ? (
                <Input
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  className="w-full"
                  placeholder="Enter pet name"
                />
              ) : (
                petInfo.name
              )}
            </h3>
            <p className="text-sm text-gray-600 font-medium">
              {isEditing ? (
                <div className="flex items-center space-x-2 mt-1">
                  <Input
                    value={formData.breed}
                    onChange={(e) => handleInputChange('breed', e.target.value)}
                    className="w-full"
                    placeholder="Breed"
                  />
                </div>
              ) : (
                petInfo.breed && petInfo.breed.toLowerCase() !== 'unknown' ? petInfo.breed : ''
              )}
            </p>
          </div>
        </div>

        {/* Pet Information Grid */}
        <div className="grid grid-cols-1 gap-3 text-sm">
          <div className="flex items-center justify-between py-2 border-b border-purple-100">
            <span className="font-semibold text-gray-700">Sex:</span>
            {renderField('Sex', formatGender(petInfo.gender), 'gender')}
          </div>
          <div className="flex items-center justify-between py-2 border-b border-purple-100">
            <span className="font-semibold text-gray-700">Type:</span>
            {renderField('Type', petInfo.type, 'type')}
          </div>
          {(petInfo.breed && petInfo.breed.toLowerCase() !== 'unknown') || isEditing ? (
            <div className="flex items-center justify-between py-2 border-b border-purple-100">
              <span className="font-semibold text-gray-700">Breed:</span>
              {renderField('Breed', petInfo.breed, 'breed')}
            </div>
          ) : null}
          {(petInfo.life_stage && petInfo.life_stage.toLowerCase() !== 'unknown') || isEditing ? (
            <div className="flex items-center justify-between py-2 border-b border-purple-100">
              <span className="font-semibold text-gray-700">Life Stage:</span>
              {renderField('Life Stage', formatLifeStage(petInfo.life_stage), 'life_stage')}
            </div>
          ) : null}
          <div className="flex items-center justify-between py-2 border-b border-purple-100">
            <span className="font-semibold text-gray-700">Born:</span>
            <span className="text-gray-900">{formatBirthday(petInfo.birthday)}</span>
          </div>
          <div className="flex items-center justify-between py-2 border-b border-purple-100">
            <span className="font-semibold text-gray-700">Weight:</span>
            {renderField('Weight', formatWeight(petInfo.weight), 'weight')}
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
        {isEditing ? (
          <div className="flex space-x-3">
            <Button
              onClick={handleSave}
              disabled={isLoading}
              className="flex-1 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white"
            >
              {isLoading ? 'Saving...' : 'Save Changes'}
            </Button>
            <Button
              variant="outline"
              onClick={onCancel}
              disabled={isLoading}
              className="flex-1"
            >
              Cancel
            </Button>
          </div>
        ) : (
          <>
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
          </>
        )}
      </div>
    </div>
  );
}; 