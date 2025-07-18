import React from 'react';
import { Button } from '../../../../ui/Buttons/Button';
import { PetOption } from '../../../../types';

interface PetSelectionProps {
  petOptions: PetOption[];
  onPetSelect: (petId: string) => void;
}

export const PetSelection: React.FC<PetSelectionProps> = ({
  petOptions,
  onPetSelect,
}) => {
  return (
    <div className="space-y-3">
      <div className="text-sm text-gray-600 mb-3">
        Choose a pack member to shop for:
      </div>
      <div className="grid grid-cols-1 gap-2">
        {petOptions.map((pet) => (
          <Button
            key={pet.id}
            variant="outline"
            className="justify-start text-left h-auto py-3 px-4"
            onClick={() => onPetSelect(pet.id.toString())}
          >
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white text-sm font-medium">
                {pet.type === 'browse' ? '🛍️' : '🐾'}
              </div>
              <div className="flex-1">
                <div className="font-medium text-gray-900">
                  {pet.name}
                </div>
                {pet.type !== 'browse' && pet.breed && (
                  <div className="text-sm text-gray-500">
                    {pet.breed}
                  </div>
                )}
              </div>
            </div>
          </Button>
        ))}
      </div>
    </div>
  );
}; 