export interface LifeStageInfo {
  stage: string;
  label: string;
  ageInYears: number;
  ageInMonths: number;
  isEstimated: boolean;
}

export interface PetAgeInfo {
  years: number;
  months: number;
  days: number;
}

// Life stage thresholds for different pet types (in months)
const LIFE_STAGE_THRESHOLDS = {
  DOG: {
    puppy: 12,    // 0-12 months
    adult: 84,    // 1-7 years
    senior: Infinity // 7+ years
  },
  CAT: {
    kitten: 12,   // 0-12 months
    adult: 120,   // 1-10 years
    senior: Infinity // 10+ years
  },
  HORSE: {
    foal: 36,     // 0-3 years
    adult: 240,   // 3-20 years
    senior: Infinity // 20+ years
  },
  BIRD: {
    chick: 12,    // 0-12 months
    adult: 120,   // 1-10 years
    senior: Infinity // 10+ years
  },
  FISH: {
    juvenile: 6,  // 0-6 months
    adult: 60,    // 0.5-5 years
    senior: Infinity // 5+ years
  },
  FARM_ANIMAL: {
    baby: 6,      // 0-6 months
    adult: 60,    // 0.5-5 years
    senior: Infinity // 5+ years
  },
  SMALL_PET: {
    baby: 2,      // 0-2 months
    adult: 18,    // 2-18 months
    senior: Infinity // 18+ months
  }
};

// Life stage labels for different pet types
const LIFE_STAGE_LABELS = {
  DOG: {
    puppy: 'Puppy',
    adult: 'Adult',
    senior: 'Senior'
  },
  CAT: {
    kitten: 'Kitten',
    adult: 'Adult',
    senior: 'Senior'
  },
  HORSE: {
    foal: 'Foal',
    adult: 'Adult',
    senior: 'Senior'
  },
  BIRD: {
    chick: 'Chick',
    adult: 'Adult',
    senior: 'Senior'
  },
  FISH: {
    juvenile: 'Juvenile',
    adult: 'Adult',
    senior: 'Senior'
  },
  FARM_ANIMAL: {
    baby: 'Baby',
    adult: 'Adult',
    senior: 'Senior'
  },
  SMALL_PET: {
    baby: 'Baby',
    adult: 'Adult',
    senior: 'Senior'
  }
};

// Legacy stage codes mapping
const LEGACY_STAGE_CODES = {
  P: 'puppy', // Puppy/Kitten
  A: 'adult', // Adult
  S: 'senior' // Senior
};

export function calculatePetAge(birthday: string | null): PetAgeInfo | null {
  if (!birthday) {
    return null;
  }

  try {
    const birthDate = new Date(birthday);
    const today = new Date();
    
    if (isNaN(birthDate.getTime())) {
      return null;
    }

    // Calculate age difference
    const ageInMs = today.getTime() - birthDate.getTime();
    const ageInDays = Math.floor(ageInMs / (1000 * 60 * 60 * 24));
    const ageInMonths = Math.floor(ageInDays / 30.44); // Average days per month
    const ageInYears = Math.floor(ageInDays / 365.25); // Account for leap years

    return {
      years: ageInYears,
      months: ageInMonths,
      days: ageInDays
    };
  } catch (error) {
    console.error('Error calculating pet age:', error);
    return null;
  }
}

export function calculateLifeStage(
  petType: string,
  birthday: string | null,
  legacyStage?: string
): LifeStageInfo {
  // If no birthday, try to use legacy stage code
  if (!birthday && legacyStage) {
    const stageKey = LEGACY_STAGE_CODES[legacyStage as keyof typeof LEGACY_STAGE_CODES];
    if (stageKey) {
      const typeLabels = LIFE_STAGE_LABELS[petType as keyof typeof LIFE_STAGE_LABELS] || LIFE_STAGE_LABELS.DOG;
      return {
        stage: stageKey,
        label: typeLabels[stageKey as keyof typeof typeLabels] || 'Unknown',
        ageInYears: 0,
        ageInMonths: 0,
        isEstimated: true
      };
    }
  }

  const ageInfo = calculatePetAge(birthday);
  if (!ageInfo) {
    return {
      stage: 'unknown',
      label: 'Unknown',
      ageInYears: 0,
      ageInMonths: 0,
      isEstimated: true
    };
  }

  const thresholds = LIFE_STAGE_THRESHOLDS[petType as keyof typeof LIFE_STAGE_THRESHOLDS] || LIFE_STAGE_THRESHOLDS.DOG;
  const labels = LIFE_STAGE_LABELS[petType as keyof typeof LIFE_STAGE_LABELS] || LIFE_STAGE_LABELS.DOG;

  let stage: string;
  let label: string;

  // Get the first stage threshold (puppy/kitten/foal/etc.)
  const firstStageKey = Object.keys(thresholds)[0];
  const firstStageThreshold = thresholds[firstStageKey as keyof typeof thresholds];
  
  if (ageInfo.months <= firstStageThreshold) {
    stage = firstStageKey;
    label = labels[stage as keyof typeof labels];
  } else if (ageInfo.months <= thresholds.adult) {
    stage = 'adult';
    label = labels.adult;
  } else {
    stage = 'senior';
    label = labels.senior;
  }

  return {
    stage,
    label,
    ageInYears: ageInfo.years,
    ageInMonths: ageInfo.months,
    isEstimated: false
  };
}

export function formatAgeDisplay(ageInfo: PetAgeInfo | null): string {
  if (!ageInfo) {
    return 'Age unknown';
  }

  if (ageInfo.years > 0) {
    if (ageInfo.years === 1) {
      return `${ageInfo.years} year old`;
    } else {
      return `${ageInfo.years} years old`;
    }
  } else if (ageInfo.months > 0) {
    if (ageInfo.months === 1) {
      return `${ageInfo.months} month old`;
    } else {
      return `${ageInfo.months} months old`;
    }
  } else {
    return `${ageInfo.days} days old`;
  }
}

export function getLifeStageColor(stage: string): string {
  switch (stage) {
    case 'puppy':
    case 'kitten':
    case 'foal':
    case 'chick':
    case 'juvenile':
    case 'baby':
    case 'young':
      return 'text-blue-600 bg-blue-100 border-blue-200';
    case 'adult':
      return 'text-green-600 bg-green-100 border-green-200';
    case 'senior':
      return 'text-orange-600 bg-orange-100 border-orange-200';
    default:
      return 'text-gray-600 bg-gray-100 border-gray-200';
  }
} 