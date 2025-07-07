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
    - Write a warm, friendly greeting (up to 3 sentences).
    - Mention all pets by name, optionally including breed or life stage if relevant.
    - If a pet's birthday is near (±7 days), give a gentle heads-up like "getting ready to celebrate?"
    - If they have multiple pets, mention all by name.
    - Keep tone friendly, playful, and warm.
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
        return random.choice(fallback_greetings)
    
    try:
        user_context = user_svc.get_user_context_for_chat(db, customer_key)
        if not user_context or not user_context.get("pets"):
            return random.choice(fallback_greetings)
        
        pets = user_context["pets"]
        customer_name = user_context.get("name", "").split()[0] if user_context.get("name") else ""
        
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
        pet_names_str = ", ".join(pet_names[:-1]) + f", and {pet_names[-1]}" if len(pet_names) > 2 else " and ".join(pet_names)
        
        # Priority 1: Upcoming birthday
        if upcoming_birthday_pets:
            pet, days_until = upcoming_birthday_pets[0]
            pet_name = pet.get("name", "your pet")
            birthday_greetings = []
            if days_until == 0:
                birthday_greetings = [
                    f"Hello{' ' + customer_name if customer_name else ''}! It's {pet_name}'s birthday today! Wishing {pet_name} a fantastic day filled with treats and cuddles. Let me know if you need help picking out something special to celebrate!",
                    f"Happy birthday to {pet_name}! {'Hope you and ' + customer_name + ' are celebrating big today.' if customer_name else 'Hope you are celebrating big today.'} If you need a last-minute gift or treat, I'm here to help!",
                    f"Hi{' ' + customer_name if customer_name else ''}! {pet_name} turns another year older today—how exciting! Let me know if you want to find something extra special for the celebration."
                ]
            elif days_until > 0:
                birthday_greetings = [
                    f"Hi{' ' + customer_name if customer_name else ''}! {pet_name}'s birthday is just around the corner. Are you getting ready to celebrate? If you need any ideas for a special treat or gift, I'm here to help!",
                    f"Hey{' ' + customer_name if customer_name else ''}! {pet_name}'s birthday is coming up soon—how fun! Let me know if you want suggestions for a birthday surprise.",
                    f"Hello{' ' + customer_name if customer_name else ''}! Looks like {pet_name}'s special day is almost here. Need help picking out a birthday treat?"
                ]
            else:
                birthday_greetings = [
                    f"Hey{' ' + customer_name if customer_name else ''}! I hope {pet_name} had a wonderful birthday recently. If you're looking to spoil them a little extra, just let me know—I'd love to help!",
                    f"Hi{' ' + customer_name if customer_name else ''}! Hope you and {pet_name} had a great birthday celebration. If you want to keep the party going with some treats or toys, I'm here!",
                    f"Hello{' ' + customer_name if customer_name else ''}! {pet_name}'s birthday just passed—hope it was a blast! Let me know if you need anything special for your furry friend."
                ]
            return random.choice(birthday_greetings)
        
        # Priority 2: New pet
        if new_pets and len(pets) > 1:
            new_pet_name = new_pets[0].get("name", "your new pet")
            other_pets = [pet["name"] for pet in pets if pet.get("name") and not pet.get("is_new", False)]
            other_pets_str = ", ".join(other_pets[:-1]) + f", and {other_pets[-1]}" if len(other_pets) > 2 else " and ".join(other_pets)
            new_pet_greetings = [
                f"Hi{' ' + customer_name if customer_name else ''}! It looks like {new_pet_name} just joined your family—how exciting! Are you shopping for {new_pet_name} along with {other_pets_str} today? Let me know if you need any recommendations for your newest family member!",
                f"Welcome{' ' + customer_name if customer_name else ''}! {new_pet_name} is the newest member of your furry crew. Shopping for both {new_pet_name} and {other_pets_str}? I'm happy to help with suggestions for everyone!",
                f"Hey{' ' + customer_name if customer_name else ''}! {new_pet_name} has joined {other_pets_str}—what a fun group! If you need ideas for your new arrival or the rest of the gang, just ask."
            ]
            return random.choice(new_pet_greetings)
        elif new_pets:
            new_pet_name = new_pets[0].get("name", "your new pet")
            new_pet_greetings = [
                f"Hi{' ' + customer_name if customer_name else ''}! Welcome {new_pet_name} to the family! If you need help finding the perfect essentials or treats, I'm here for you. Let me know what {new_pet_name} needs today!",
                f"Hello{' ' + customer_name if customer_name else ''}! {new_pet_name} is lucky to have you. If you want recommendations for your new companion, just let me know!",
                f"Hey{' ' + customer_name if customer_name else ''}! Excited to help you shop for {new_pet_name}. Let me know if you need any tips for your newest furry friend."
            ]
            return random.choice(new_pet_greetings)
        
        # Priority 3: Multiple pets - mention all by name
        if len(pet_names) > 1:
            multi_pet_greetings = [
                f"Hello{' ' + customer_name if customer_name else ''}! It's always a joy to see you shopping for {pet_names_str}. Your furry crew is lucky to have someone who cares so much! Let me know if you're looking for something special for any of them today.",
                f"Hi{' ' + customer_name if customer_name else ''}! Shopping for {pet_names_str} today? I'm here to help you find the best for your whole pack!",
                f"Hey{' ' + customer_name if customer_name else ''}! {pet_names_str} must keep you busy! Let me know if you need ideas for treats or toys for any of your pets."
            ]
            return random.choice(multi_pet_greetings)
        
        # Priority 4: Single pet with breed/life stage
        if len(pets) == 1:
            pet = pets[0]
            pet_name = pet.get("name", "your pet")
            breed = pet.get("breed", "")
            life_stage = pet.get("life_stage", "")
            details = ""
            if breed and breed.lower() != "unknown":
                details = f" the {breed}"
            elif life_stage and life_stage.lower() not in ["unknown", "adult"]:
                details = f" the {life_stage.lower()}"
            single_pet_greetings = [
                f"Hi{' ' + customer_name if customer_name else ''}! How are you and {pet_name}{details} doing today? I'm here to help you find the perfect goodies for {pet_name}. Let me know if you need any suggestions or just want to browse!",
                f"Hello{' ' + customer_name if customer_name else ''}! {pet_name}{details} is lucky to have you shopping for them. If you need ideas for treats or toys, just ask!",
                f"Hey{' ' + customer_name if customer_name else ''}! Always happy to help you and {pet_name}{details}. Let me know what you're looking for today!"
            ]
            return random.choice(single_pet_greetings)
        
        # Fallback with customer name if available
        if customer_name:
            fallback_named_greetings = [
                f"Hey {customer_name}! What can I help you find for your pets today? I'm here to make sure your furry friends get the best. Let me know how I can help!",
                f"Hi {customer_name}! Ready to shop for your pets? Let me know if you need any recommendations.",
                f"Hello {customer_name}! Excited to help you find something special for your pets today."
            ]
            return random.choice(fallback_named_greetings)
        
        return random.choice(fallback_greetings)
        
    except Exception as e:
        print(f"Error generating personalized greeting for customer {customer_key}: {e}")
        return random.choice(fallback_greetings)
