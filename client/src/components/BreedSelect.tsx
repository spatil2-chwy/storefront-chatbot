import React from 'react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/Selects/Select';
import { MultiSelect, MultiSelectOption } from '../ui/Selects/MultiSelect';
import { useBreedSelection } from '../hooks/use-breed-selection';
import { Label } from '../ui/Input/Label';
import { Loader2 } from 'lucide-react';

interface BreedSelectProps {
  species: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  className?: string;
  label?: string;
  disabled?: boolean;
}

export const BreedSelect: React.FC<BreedSelectProps> = ({
  species,
  value,
  onChange,
  placeholder = "Select breed...",
  className = "",
  label,
  disabled = false
}) => {
  const {
    breedOptions,
    selectedBreeds,
    isLoading,
    error,
    handleBreedChange,
    isMultiSelect,
    maxSelections
  } = useBreedSelection({
    species,
    initialBreed: value
  });

  // Handle breed selection changes
  const handleSelectionChange = (selectedValues: string[]) => {
    // Limit selections for multi-select
    const limitedValues = isMultiSelect ? selectedValues.slice(0, maxSelections) : selectedValues;
    handleBreedChange(limitedValues);
    
    // Convert back to string format for the parent component
    const breedString = limitedValues.join(', ');
    onChange(breedString);
  };

  // Convert breed options to MultiSelectOption format
  const multiSelectOptions: MultiSelectOption[] = breedOptions.map(breed => ({
    value: breed.value,
    label: breed.label
  }));

  if (isLoading) {
    return (
      <div className={className}>
        {label && <Label className="text-sm font-medium">{label}</Label>}
        <div className="mt-1 flex items-center space-x-2 p-2 border border-gray-300 rounded-md bg-gray-50">
          <Loader2 className="h-4 w-4 animate-spin text-gray-500" />
          <span className="text-sm text-gray-500">Loading breeds...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={className}>
        {label && <Label className="text-sm font-medium">{label}</Label>}
        <div className="mt-1 p-2 border border-red-300 rounded-md bg-red-50">
          <span className="text-sm text-red-600">{error}</span>
        </div>
      </div>
    );
  }

  if (isMultiSelect) {
    return (
      <div className={className}>
        {label && <Label className="text-sm font-medium">{label}</Label>}
        <MultiSelect
          options={multiSelectOptions}
          selectedValues={selectedBreeds}
          onSelectionChange={handleSelectionChange}
          placeholder={placeholder}
          searchPlaceholder="Search breeds..."
          className="mt-1"
          disabled={disabled}
        />
        {isMultiSelect && (
          <p className="text-xs text-gray-500 mt-1">
            Select up to {maxSelections} breeds
          </p>
        )}
      </div>
    );
  }

  // Single select for other species
  return (
    <div className={className}>
      {label && <Label className="text-sm font-medium">{label}</Label>}
      <Select
        value={selectedBreeds[0] || ""}
        onValueChange={(selectedValue) => handleSelectionChange([selectedValue])}
        disabled={disabled}
      >
        <SelectTrigger className="mt-1">
          <SelectValue placeholder={placeholder} />
        </SelectTrigger>
        <SelectContent>
          {breedOptions.map((breed) => (
            <SelectItem key={breed.value} value={breed.value}>
              {breed.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}; 