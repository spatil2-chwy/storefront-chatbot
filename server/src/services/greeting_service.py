from datetime import date, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from src.services.user_service import UserService
import random

user_svc = UserService()

def generate_personalized_greeting(db: Session, customer_key: Optional[int] = None) -> str:
    """
    Generate a personalized greeting for a customer based on their profile and pets.
    
    Instructions based on prompt:
    - Write a short, warm greeting (max 2 short sentences).
    - Mention pets by name, optionally including breed or life stage if relevant.
    - If a pet's birthday is near (±7 days), give a gentle heads-up like "getting ready to celebrate?"
    - If this is their first time logging in after a new pet was added, mention that
    - If they have multiple pets, you can say "shopping for [pet1 or pet2] today?"
    - Keep tone friendly, a little playful, and not too robotic.
    """
    
    # Fallback greeting if no customer key or user not found
    fallback_greetings = [
        "Hey there! What can I help you find for your furry friends today?",
        "Hi! Ready to spoil some pets today?",
        "Welcome! What's on the pet shopping list today?",
        "Hey! Looking for something special for your pet today?"
    ]
    
    if not customer_key:
        return random.choice(fallback_greetings)
    
    try:
        # Get user context
        user_context = user_svc.get_user_context_for_chat(db, customer_key)
        if not user_context or not user_context.get("pets"):
            return random.choice(fallback_greetings)
        
        pets = user_context["pets"]
        customer_name = user_context.get("name", "").split()[0] if user_context.get("name") else ""
        
        # Check for upcoming birthdays (±7 days)
        today = date.today()
        upcoming_birthday_pets = []
        
        for pet in pets:
            if pet.get("birthday"):
                # Calculate next birthday (this year or next year)
                birthday = pet["birthday"]
                this_year_birthday = birthday.replace(year=today.year)
                
                # If birthday this year has passed, check next year
                if this_year_birthday < today:
                    next_birthday = birthday.replace(year=today.year + 1)
                else:
                    next_birthday = this_year_birthday
                
                days_until = (next_birthday - today).days
                if -7 <= days_until <= 7:
                    upcoming_birthday_pets.append((pet, days_until))
        
        # Check for new pets (added recently or marked as new)
        new_pets = [pet for pet in pets if pet.get("is_new", False)]
        
        # Generate greeting based on context
        pet_names = [pet["name"] for pet in pets if pet.get("name")]
        
        # Priority 1: Upcoming birthday
        if upcoming_birthday_pets:
            pet, days_until = upcoming_birthday_pets[0]
            pet_name = pet.get("name", "your pet")
            if days_until == 0:
                return f"Hey! It's {pet_name}'s birthday today! Need help planning something special?"
            elif days_until > 0:
                return f"Hey — {pet_name}'s birthday is coming up! Getting ready to celebrate?"
            else:
                return f"Hey! Hope {pet_name} had a great birthday recently. Shopping for something special today?"
        
        # Priority 2: New pet
        if new_pets and len(pets) > 1:
            new_pet_name = new_pets[0].get("name", "your new pet")
            other_pets = [pet["name"] for pet in pets if pet.get("name") and not pet.get("is_new", False)]
            if other_pets:
                return f"Hi! Looks like {new_pet_name} just joined your family 💙 Shopping for everyone today?"
            else:
                return f"Hi! Welcome {new_pet_name} to the family! What do they need today?"
        
        # Priority 3: Multiple pets - ask which one
        if len(pet_names) > 1:
            if len(pet_names) == 2:
                return f"Hey there! Shopping for {pet_names[0]} or {pet_names[1]} today?"
            else:
                # Pick 2 random pets to mention
                selected_pets = random.sample(pet_names, 2)
                return f"Hey there! Is {selected_pets[0]} or {selected_pets[1]} getting spoiled today?"
        
        # Priority 4: Single pet with breed/life stage
        if len(pets) == 1:
            pet = pets[0]
            pet_name = pet.get("name", "your pet")
            breed = pet.get("breed", "")
            life_stage = pet.get("life_stage", "")
            
            # Add some variety to single pet greetings
            greetings = [
                f"Hey! What's {pet_name} getting today?",
                f"Hi there! Shopping for {pet_name} today?",
                f"Welcome back! What does {pet_name} need today?"
            ]
            
            # Add breed or life stage context sometimes
            if breed and breed.lower() != "unknown" and random.choice([True, False]):
                greetings.append(f"Hey! Looking for something special for {pet_name} the {breed}?")
            elif life_stage and life_stage.lower() not in ["unknown", "adult"] and random.choice([True, False]):
                greetings.append(f"Hi! What does {life_stage.lower()} {pet_name} need today?")
            
            return random.choice(greetings)
        
        # Fallback with customer name if available
        if customer_name:
            return f"Hey {customer_name}! What can I help you find for your pets today?"
        
        return random.choice(fallback_greetings)
        
    except Exception as e:
        print(f"Error generating personalized greeting for customer {customer_key}: {e}")
        return random.choice(fallback_greetings)
