export interface BreedOption {
  value: string;
  label: string;
}

export interface BreedData {
  [species: string]: BreedOption[];
}

class BreedService {
  private breedData: BreedData = {};
  private loadedSpecies = new Set<string>();

  async loadBreedsForSpecies(species: string): Promise<BreedOption[]> {
    // Normalize species name to match CSV file names
    const speciesMap: { [key: string]: string } = {
      'DOG': 'dog',
      'CAT': 'cat',
      'HORSE': 'horse',
      'BIRD': 'bird',
      'FISH': 'fish',
      'RABBIT': 'small_pet', // Rabbits are in small_pet.csv
      'HAMSTER': 'small_pet', // Hamsters are in small_pet.csv
      'OTHER': 'small_pet' // Other pets are in small_pet.csv
    };

    const csvFileName = speciesMap[species.toUpperCase()];
    if (!csvFileName) {
      console.warn(`No breed data available for species: ${species}`);
      return [];
    }

    // Return cached data if already loaded
    if (this.breedData[csvFileName]) {
      return this.breedData[csvFileName];
    }

    try {
      // Load breed data from CSV file
      const response = await fetch(`/data/backend/pets/${csvFileName}.csv`);
      if (!response.ok) {
        throw new Error(`Failed to load breed data for ${species}`);
      }

      const csvText = await response.text();
      const breeds = this.parseCSV(csvText);
      
      // Cache the data
      this.breedData[csvFileName] = breeds;
      this.loadedSpecies.add(species);
      
      return breeds;
    } catch (error) {
      console.error(`Error loading breeds for ${species}:`, error);
      return [];
    }
  }

  private parseCSV(csvText: string): BreedOption[] {
    const lines = csvText.trim().split('\n');
    const breeds: BreedOption[] = [];
    
    // Skip header row and process each line
    for (let i = 1; i < lines.length; i++) {
      const line = lines[i].trim();
      if (line) {
        // Handle CSV format - some files use "PET_BREED_NM" header, others use "Fish Species"
        const breedName = line.replace(/^["']|["']$/g, ''); // Remove quotes if present
        breeds.push({
          value: breedName,
          label: breedName
        });
      }
    }
    
    return breeds.sort((a, b) => a.label.localeCompare(b.label));
  }

  // Get breeds for a specific species (cached if available)
  getBreedsForSpecies(species: string): BreedOption[] {
    const speciesMap: { [key: string]: string } = {
      'DOG': 'dog',
      'CAT': 'cat',
      'HORSE': 'horse',
      'BIRD': 'bird',
      'FISH': 'fish',
      'RABBIT': 'small_pet',
      'HAMSTER': 'small_pet',
      'OTHER': 'small_pet'
    };

    const csvFileName = speciesMap[species.toUpperCase()];
    return this.breedData[csvFileName] || [];
  }

  // Check if breeds are loaded for a species
  isBreedsLoaded(species: string): boolean {
    return this.loadedSpecies.has(species.toUpperCase());
  }

  // Clear cache (useful for testing or memory management)
  clearCache(): void {
    this.breedData = {};
    this.loadedSpecies.clear();
  }
}

export const breedService = new BreedService(); 