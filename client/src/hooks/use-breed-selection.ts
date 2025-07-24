import { useState, useEffect } from 'react';
import { breedService, BreedOption } from '../lib/api/breeds';

export interface UseBreedSelectionProps {
  species: string;
  initialBreed?: string;
  maxSelections?: number;
}

export interface UseBreedSelectionReturn {
  breedOptions: BreedOption[];
  selectedBreeds: string[];
  isLoading: boolean;
  error: string | null;
  handleBreedChange: (breeds: string[]) => void;
  isMultiSelect: boolean;
  maxSelections: number;
}

export const useBreedSelection = ({
  species,
  initialBreed = '',
  maxSelections = 2
}: UseBreedSelectionProps): UseBreedSelectionReturn => {
  const [breedOptions, setBreedOptions] = useState<BreedOption[]>([]);
  const [selectedBreeds, setSelectedBreeds] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Determine if this species should use multi-select
  const isMultiSelect = ['DOG', 'CAT', 'HORSE'].includes(species.toUpperCase());

  // Load breed options when species changes
  useEffect(() => {
    if (!species) {
      setBreedOptions([]);
      setSelectedBreeds([]);
      return;
    }

    const loadBreeds = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        const breeds = await breedService.loadBreedsForSpecies(species);
        setBreedOptions(breeds);
        
        // Initialize selected breeds from initialBreed
        if (initialBreed) {
          if (isMultiSelect) {
            // For multi-select, split by comma and trim
            const breeds = initialBreed.split(',').map(b => b.trim()).filter(b => b);
            setSelectedBreeds(breeds.slice(0, maxSelections));
          } else {
            // For single-select, just use the initial breed
            setSelectedBreeds([initialBreed]);
          }
        } else {
          setSelectedBreeds([]);
        }
      } catch (err) {
        setError(`Failed to load breeds for ${species}`);
        console.error('Error loading breeds:', err);
      } finally {
        setIsLoading(false);
      }
    };

    loadBreeds();
  }, [species, initialBreed, isMultiSelect, maxSelections]);

  const handleBreedChange = (breeds: string[]) => {
    if (isMultiSelect) {
      // For multi-select, limit to maxSelections
      setSelectedBreeds(breeds.slice(0, maxSelections));
    } else {
      // For single-select, take only the first selection
      setSelectedBreeds(breeds.slice(0, 1));
    }
  };

  return {
    breedOptions,
    selectedBreeds,
    isLoading,
    error,
    handleBreedChange,
    isMultiSelect,
    maxSelections
  };
}; 