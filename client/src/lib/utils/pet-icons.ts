export const getPetIcon = (petType: string): string => {
  const type = petType?.toUpperCase() || '';
  
  switch (type) {
    case 'DOG':
      return '🐕';
    case 'CAT':
      return '🐱';
    case 'BIRD':
      return '🐦';
    case 'FISH':
      return '🐠';
    case 'SMALL_PET':
    case 'RABBIT':
    case 'HAMSTER':
    case 'FERRET':
    case 'GUINEA_PIG':
    case 'CHINCHILLA':
    case 'GERBIL':
    case 'MOUSE':
    case 'RAT':
      return '🐭';
    case 'HORSE':
      return '🐎';
    case 'REPTILE':
      return '🦎';
    case 'FARM_ANIMAL':
    case 'PIG':
    case 'COW':
    case 'SHEEP':
    case 'GOAT':
    case 'CHICKEN':
    case 'DUCK':
    case 'TURKEY':
      return '🐷';
    case 'BROWSE':
      return '🛍️';
    default:
      return '🐾';
  }
}; 