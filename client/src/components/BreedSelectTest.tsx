import React, { useState, useEffect } from 'react';
import { breedService } from '../lib/api/breeds';
import { BreedSelect } from './BreedSelect';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Cards/Card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/Selects/Select';

export const BreedSelectTest: React.FC = () => {
  const [selectedSpecies, setSelectedSpecies] = useState('HORSE');
  const [selectedBreed, setSelectedBreed] = useState('');
  const [breeds, setBreeds] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [rawCsvData, setRawCsvData] = useState<string>('');

  const speciesOptions = [
    { value: 'DOG', label: 'Dog' },
    { value: 'CAT', label: 'Cat' },
    { value: 'HORSE', label: 'Horse' },
    { value: 'BIRD', label: 'Bird' },
    { value: 'FISH', label: 'Fish' },
    { value: 'FARM_ANIMAL', label: 'Farm Animal' },
    { value: 'SMALL_PET', label: 'Small Pet' }
  ];

  const loadBreeds = async (species: string) => {
    setLoading(true);
    setError(null);
    try {
      console.log(`Loading breeds for species: ${species}`);
      
      // Test direct fetch first
      const csvFileName = species.toLowerCase();
      const response = await fetch(`/pets/${csvFileName}.csv`);
      console.log(`Fetch response status: ${response.status}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch CSV file: ${response.status} ${response.statusText}`);
      }
      
      const csvText = await response.text();
      console.log(`Raw CSV data (first 200 chars):`, csvText.substring(0, 200));
      setRawCsvData(csvText.substring(0, 500));
      
      // Now test the breed service
      const breedData = await breedService.loadBreedsForSpecies(species);
      console.log(`Loaded ${breedData.length} breeds:`, breedData);
      setBreeds(breedData);
    } catch (err) {
      console.error('Error loading breeds:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBreeds(selectedSpecies);
  }, [selectedSpecies]);

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Breed Loading Test</h1>
      
      <Card>
        <CardHeader>
          <CardTitle>Test Breed Loading</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium">Select Species</label>
            <Select
              value={selectedSpecies}
              onValueChange={setSelectedSpecies}
            >
              <SelectTrigger className="mt-1">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {speciesOptions.map(species => (
                  <SelectItem key={species.value} value={species.value}>
                    {species.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {loading && (
            <div className="text-blue-600">Loading breeds...</div>
          )}

          {error && (
            <div className="text-red-600">Error: {error}</div>
          )}

          {rawCsvData && (
            <div>
              <h3 className="font-semibold mb-2">Raw CSV Data:</h3>
              <div className="max-h-40 overflow-y-auto border rounded p-2 bg-gray-50 text-xs">
                <pre>{rawCsvData}</pre>
              </div>
            </div>
          )}

          {!loading && !error && (
            <div>
              <h3 className="font-semibold mb-2">Loaded Breeds ({breeds.length}):</h3>
              <div className="max-h-60 overflow-y-auto border rounded p-2">
                {breeds.map((breed, index) => (
                  <div key={index} className="text-sm py-1">
                    {breed.label} ({breed.value})
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Test BreedSelect Component</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium">Species for BreedSelect</label>
            <Select
              value={selectedSpecies}
              onValueChange={setSelectedSpecies}
            >
              <SelectTrigger className="mt-1">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {speciesOptions.map(species => (
                  <SelectItem key={species.value} value={species.value}>
                    {species.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
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