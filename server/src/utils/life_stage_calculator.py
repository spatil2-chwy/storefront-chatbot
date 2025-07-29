from datetime import date, datetime
from typing import Optional

# Life stage thresholds for different pet types (in months)
LIFE_STAGE_THRESHOLDS = {
    'DOG': {
        'puppy': 12,    # 0-12 months
        'adult': 84,    # 1-7 years
        'senior': float('inf')  # 7+ years
    },
    'CAT': {
        'kitten': 12,   # 0-12 months
        'adult': 120,   # 1-10 years
        'senior': float('inf')  # 10+ years
    },
    'HORSE': {
        'foal': 36,     # 0-3 years
        'adult': 240,   # 3-20 years
        'senior': float('inf')  # 20+ years
    },
    'BIRD': {
        'chick': 12,    # 0-12 months
        'adult': 120,   # 1-10 years
        'senior': float('inf')  # 10+ years
    },
    'FISH': {
        'juvenile': 6,  # 0-6 months
        'adult': 60,    # 0.5-5 years
        'senior': float('inf')  # 5+ years
    },
    'FARM_ANIMAL': {
        'baby': 6,      # 0-6 months
        'adult': 60,    # 0.5-5 years
        'senior': float('inf')  # 5+ years
    },
    'SMALL_PET': {
        'baby': 2,      # 0-2 months
        'adult': 18,    # 2-18 months
        'senior': float('inf')  # 18+ months
    }
}

# Legacy stage codes mapping
LEGACY_STAGE_CODES = {
    'P': 'puppy',  # Puppy/Kitten
    'A': 'adult',  # Adult
    'S': 'senior'  # Senior
}

def calculate_pet_age(birthday: Optional[date]) -> Optional[dict]:
    """Calculate pet age from birthday"""
    if not birthday:
        return None
    
    today = date.today()
    age_delta = today - birthday
    
    age_days = age_delta.days
    age_months = int(age_days / 30.44)  # Average days per month
    age_years = int(age_days / 365.25)  # Account for leap years
    
    return {
        'years': age_years,
        'months': age_months,
        'days': age_days
    }

def calculate_life_stage(pet_type: str, birthday: Optional[date], legacy_stage: Optional[str] = None) -> str:
    """Calculate life stage based on pet type and birthday"""
    # Normalize pet type
    pet_type = pet_type.upper() if pet_type else 'OTHER'
    
    # If no birthday, try to use legacy stage code
    if not birthday and legacy_stage:
        stage_key = LEGACY_STAGE_CODES.get(legacy_stage.upper())
        if stage_key:
            return legacy_stage.upper()  # Return original legacy code
    
    # Calculate age
    age_info = calculate_pet_age(birthday)
    if not age_info:
        return 'UNKNOWN'
    
    # Get thresholds for this pet type
    thresholds = LIFE_STAGE_THRESHOLDS.get(pet_type, LIFE_STAGE_THRESHOLDS.get('DOG'))
    
    # Determine life stage based on age
    if age_info['months'] <= thresholds.get('puppy', thresholds.get('kitten', thresholds.get('foal', thresholds.get('chick', thresholds.get('juvenile', thresholds.get('baby', 12)))))):
        return 'P'  # Puppy/Kitten/Foal/etc.
    elif age_info['months'] <= thresholds.get('adult', 84):
        return 'A'  # Adult
    else:
        return 'S'  # Senior

def format_age_display(age_info: Optional[dict]) -> str:
    """Format age for display"""
    if not age_info:
        return "Age unknown"
    
    if age_info['years'] > 0:
        if age_info['years'] == 1:
            return f"{age_info['years']} year old"
        else:
            return f"{age_info['years']} years old"
    elif age_info['months'] > 0:
        if age_info['months'] == 1:
            return f"{age_info['months']} month old"
        else:
            return f"{age_info['months']} months old"
    else:
        return f"{age_info['days']} days old" 