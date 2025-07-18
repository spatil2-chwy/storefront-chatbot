from datetime import date, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from src.services.user_service import UserService
import random

user_svc = UserService()

def generate_personalized_greeting(db: Session, customer_key: Optional[int] = None) -> Dict[str, Any]:
    """
    Generate a personalized greeting for a customer based on their profile and pets.
    Returns a dictionary with greeting text and pet selection options if applicable.
    """
    
    fallback_greetings = [
        "Hey there! What can I help you find for your furry friends today?",
        "Hi! Ready to spoil some pets today?",
        "Welcome! What's on the pet shopping list today?",
        "Hey! Looking for something special for your pet today?",
        "Hello! How can I help you and your pets today?",
        "Hi there! Excited to help you find something for your pets.",
        "Welcome back! What treats or toys are you looking for today?",
        "Hey! Always happy to help with your pet shopping needs."
    ]
    
    if not customer_key:
        return {
            "greeting": random.choice(fallback_greetings),
            "has_pets": False,
            "pet_options": []
        }
    
    try:
        user_context = user_svc.get_user_context_for_chat(db, customer_key)
        if not user_context:
            return {
                "greeting": random.choice(fallback_greetings),
                "has_pets": False,
                "pet_options": []
            }
        
        pets = user_context.get("pets", [])
        customer_name = user_context.get("name", "").split()[0] if user_context.get("name") else ""
        possible_next_buys = user_context.get("possible_next_buys", "")
        
        # If user has no pets, return simple greeting
        if not pets:
            return {
                "greeting": random.choice(fallback_greetings),
                "has_pets": False,
                "pet_options": []
            }
        
        today = date.today()
        upcoming_birthday_pets = []
        
        for pet in pets:
            if pet.get("birthday"):
                birthday = pet["birthday"]
                this_year_birthday = birthday.replace(year=today.year)
                if this_year_birthday < today:
                    next_birthday = birthday.replace(year=today.year + 1)
                else:
                    next_birthday = this_year_birthday
                days_until = (next_birthday - today).days
                if -7 <= days_until <= 7:
                    upcoming_birthday_pets.append((pet, days_until))
        
        new_pets = [pet for pet in pets if pet.get("is_new", False)]
        pet_names = [pet["name"] for pet in pets if pet.get("name")]
        
        # Create pet options for selection
        pet_options = []
        for pet in pets:
            if pet.get("name"):
                pet_options.append({
                    "id": pet.get("pet_profile_id"),
                    "name": pet["name"],
                    "type": pet.get("type", ""),
                    "breed": pet.get("breed", "")
                })
        
        # Add browse option
        pet_options.append({
            "id": "browse",
            "name": "Just browse",
            "type": "browse",
            "breed": ""
        })
        
        # Generate greeting text based on number of pets
        greeting_text = ""
        
        # Single pet - ask if shopping for the pet or just browsing
        if len(pets) == 1:
            pet = pets[0]
            pet_name = pet.get("name", "your pet")
            breed = pet.get("breed", "")
            details = ""
            if breed and breed.lower() != "unknown":
                details = f" the {breed}"
            
            single_pet_greetings = [
                f"Hi{' ' + customer_name if customer_name else ''}! Are you shopping for {pet_name}{details} today, or just browsing?",
                f"Hello{' ' + customer_name if customer_name else ''}! Looking for something special for {pet_name}{details}, or want to explore?",
                f"Hey{' ' + customer_name if customer_name else ''}! Shopping for {pet_name}{details} or just browsing today?"
            ]
            greeting_text = random.choice(single_pet_greetings)
        
        # Multiple pets - ask which pet they're shopping for
        else:
            pet_names_str = ", ".join(pet_names[:-1]) + f", and {pet_names[-1]}" if len(pet_names) > 2 else " and ".join(pet_names)
            
            # Priority 1: Upcoming birthday
            if upcoming_birthday_pets:
                pet, days_until = upcoming_birthday_pets[0]
                pet_name = pet.get("name", "your pet")
                birthday_greetings = [
                    f"Hello{' ' + customer_name if customer_name else ''}! It's {pet_name}'s birthday today! Wishing {pet_name} a fantastic day filled with treats and cuddles. Which pack member are you shopping for today?",
                    f"Happy birthday to {pet_name}! {'Hope you and ' + customer_name + ' are celebrating big today.' if customer_name else 'Hope you are celebrating big today.'} Which pack member are you shopping for today?",
                    f"Hi{' ' + customer_name if customer_name else ''}! {pet_name} turns another year older today—how exciting! Which pack member are you shopping for today?"
                ]
                greeting_text = random.choice(birthday_greetings)
            
            # Priority 2: New pet
            elif new_pets and len(pets) > 1:
                new_pet_name = new_pets[0].get("name", "your new pet")
                other_pets = [pet["name"] for pet in pets if pet.get("name") and not pet.get("is_new", False)]
                other_pets_str = ", ".join(other_pets[:-1]) + f", and {other_pets[-1]}" if len(other_pets) > 2 else " and ".join(other_pets)
                new_pet_greetings = [
                    f"Hi{' ' + customer_name if customer_name else ''}! It looks like {new_pet_name} just joined your family—how exciting! Which pack member are you shopping for today?",
                    f"Welcome{' ' + customer_name if customer_name else ''}! {new_pet_name} is the newest member of your furry crew. Which pack member are you shopping for today?",
                    f"Hey{' ' + customer_name if customer_name else ''}! {new_pet_name} has joined {other_pets_str}—what a fun group! Which pack member are you shopping for today?"
                ]
                greeting_text = random.choice(new_pet_greetings)
            
            # Priority 3: Multiple pets - mention all by name
            else:
                multi_pet_greetings = [
                    f"Hello{' ' + customer_name if customer_name else ''}! It's always a joy to see you shopping for {pet_names_str}. Which pack member are you shopping for today?",
                    f"Hi{' ' + customer_name if customer_name else ''}! Shopping for {pet_names_str} today? Which pack member are you shopping for today?",
                    f"Hey{' ' + customer_name if customer_name else ''}! {pet_names_str} must keep you busy! Which pack member are you shopping for today?"
                ]
                greeting_text = random.choice(multi_pet_greetings)
        
        return {
            "greeting": greeting_text,
            "has_pets": True,
            "pet_options": pet_options
        }
        
    except Exception as e:
        print(f"Error generating personalized greeting for customer {customer_key}: {e}")
        return {
            "greeting": random.choice(fallback_greetings),
            "has_pets": False,
            "pet_options": []
        }