import React, { useState } from 'react';
import { BreedSelect } from './BreedSelect';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Cards/Card';

export const BreedSelectTest: React.FC = () => {
  const [selectedSpecies, setSelectedSpecies] = useState('DOG');
  const [selectedBreed, setSelectedBreed] = useState('');

  const speciesOptions = [
    { value: 'DOG', label: 'Dog' },
    { value: 'CAT', label: 'Cat' },
    { value: 'HORSE', label: 'Horse' },
    { value: 'BIRD', label: 'Bird' },
    { value: 'FISH', label: 'Fish' },
    { value: 'RABBIT', label: 'Rabbit' },
    { value: 'HAMSTER', label: 'Hamster' },
    { value: 'OTHER', label: 'Other' }
  ];

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Breed Select Test</h1>
      
      <Card>
        <CardHeader>
          <CardTitle>Test Breed Selection</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Species</label>
            <select
              value={selectedSpecies}
              onChange={(e) => {
                setSelectedSpecies(e.target.value);
                setSelectedBreed(''); // Clear breed when species changes
              }}
              className="w-full p-2 border border-gray-300 rounded-md"
            >
              {speciesOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <BreedSelect
              species={selectedSpecies}
              value={selectedBreed}
              onChange={setSelectedBreed}
              label="Breed"
              placeholder="Select breed..."
            />
          </div>

          <div className="mt-4 p-4 bg-gray-100 rounded-md">
            <h3 className="font-semibold mb-2">Selected Values:</h3>
            <p><strong>Species:</strong> {selectedSpecies}</p>
            <p><strong>Breed:</strong> {selectedBreed || 'None selected'}</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}; 