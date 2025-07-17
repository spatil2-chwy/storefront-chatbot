import React, { useState } from 'react';
import { Button } from '../../../../ui/Buttons/Button';
import { Input } from '../../../../ui/Input/Input';
import { Label } from '../../../../ui/Input/Label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../../../ui/Selects/Select';
import { PetProfileInfo } from '../../../../types';

interface PetEditProps {
  petInfo: PetProfileInfo;
  onSave: (updatedPet: PetProfileInfo) => void;
  onCancel: () => void;
}

export const PetEdit: React.FC<PetEditProps> = ({
  petInfo,
  onSave,
  onCancel,
}) => {
  const [formData, setFormData] = useState<PetProfileInfo>(petInfo);
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (field: keyof PetProfileInfo, value: string | number | boolean) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSave = async () => {
    setIsLoading(true);
    try {
      await onSave(formData);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="text-sm text-gray-600 mb-4">
        Let's update {petInfo.name}'s information. You can skip any field you don't want to fill out.
      </div>

      <div className="space-y-4">
        {/* Pet Name */}
        <div className="space-y-2">
          <Label htmlFor="pet-name">Pet Name</Label>
          <Input
            id="pet-name"
            value={formData.name}
            onChange={(e) => handleInputChange('name', e.target.value)}
            placeholder="Enter pet name"
          />
        </div>

        {/* Pet Type */}
        <div className="space-y-2">
          <Label htmlFor="pet-type">Pet Type</Label>
          <Select
            value={formData.type}
            onValueChange={(value) => handleInputChange('type', value)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select pet type" />
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
        </div>

        {/* Breed */}
        <div className="space-y-2">
          <Label htmlFor="pet-breed">Breed</Label>
          <Input
            id="pet-breed"
            value={formData.breed}
            onChange={(e) => handleInputChange('breed', e.target.value)}
            placeholder="Enter breed"
          />
        </div>

        {/* Gender */}
        <div className="space-y-2">
          <Label htmlFor="pet-gender">Gender</Label>
          <Select
            value={formData.gender}
            onValueChange={(value) => handleInputChange('gender', value)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select gender" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="MALE">Male</SelectItem>
              <SelectItem value="FMLE">Female</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Life Stage */}
        <div className="space-y-2">
          <Label htmlFor="pet-life-stage">Life Stage</Label>
          <Select
            value={formData.life_stage}
            onValueChange={(value) => handleInputChange('life_stage', value)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select life stage" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="P">Puppy/Kitten</SelectItem>
              <SelectItem value="A">Adult</SelectItem>
              <SelectItem value="S">Senior</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Weight */}
        <div className="space-y-2">
          <Label htmlFor="pet-weight">Weight (lbs)</Label>
          <Input
            id="pet-weight"
            type="number"
            value={formData.weight}
            onChange={(e) => handleInputChange('weight', parseFloat(e.target.value) || 0)}
            placeholder="Enter weight"
          />
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex space-x-3 pt-4">
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
    </div>
  );
}; 