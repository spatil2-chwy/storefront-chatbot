from fastapi import Depends
from sqlalchemy.orm import Session
from src.config.openai_loader import get_openai_client
from src.chat.prompts import persona_updater_system_prompt, interaction_based_persona_updater_system_prompt
from src.services.user_service import UserService
from src.database import get_db
from src.models.user import User
from typing import List, Dict, Any


client = get_openai_client()
MODEL = "gpt-4.1"

user_svc = UserService()

MSG_TO_CAPTURE = 7 # how many messages to capture for persona update

def update_persona(customer_key: int, history: list[dict], db: Session) -> bool:
    user_info = user_svc.get_user(db, customer_key).persona_summary
    print(user_info)

    response = client.responses.create(
        model = MODEL,
        input = [
            persona_updater_system_prompt, 
            {"role": "user", "content": "Chat History:\n" + str(history[1:][-MSG_TO_CAPTURE:]) + "\n\nPrevious persona summary: " + user_info}
        ],
    )

    content = response.output[0].content[0].text
    print(content)

    if content == "no_update":
        return False
    
    # Update the user's persona summary
    user_svc.update_user(
        db=db,
        customer_key=customer_key,
        user_data=User(persona_summary=content)
    )

    return True


def update_interaction_based_persona(customer_key: int, interaction_history: list[dict], db: Session) -> bool:
    user = user_svc.get_user(db, customer_key)
    if not user:
        print(f"User not found for customer_key: {customer_key}")
        return False
    
    user_info = user.persona_summary or ""
    print(user_info)

    response = client.chat.completions.create(
        model = MODEL,
        messages = [
            interaction_based_persona_updater_system_prompt, 
            {"role": "user", "content": "Interaction History:\n" + str(interaction_history) + "\n\nPrevious persona summary: " + user_info}
        ],
    )

    content = response.choices[0].message.content
    print(content)

    if content == "no_update":
        return False
    
    # Update the user's persona summary
    user_svc.update_user(
        db=db,
        customer_key=customer_key,
        user_data=User(persona_summary=content)
    )

    return True

# test
if __name__ == "__main__":
    test_history = [
        {"role": "system", "content": "You are a helpful assistant. (This message gets thrown away)"},
        # {"role": "user", "content": "Hi, im looking to purchase dog food from purina one"},
        # {"role": "assistant", "content": "Sure, here you go!"}
        {"role": "user", "content": "im so upset, my dog just keeps ruining all his toys. I will just buy cheap toys from now on"},
        {"role": "assistant", "content": "I'm sorry to hear that. It's tough when pets are destructive."},
    ]
    
    # Get a database session for testing
    db = next(get_db())
    try:
        update_persona(24612503152, test_history, db)
    finally:
        db.close()

    test_interaction_history = [
        {
            "user_id": 13094240.0,
            "summary": {
                "total_events": 16,
                "purchases": 4,
                "carts": 4,
                "clicks": 8,
                "conversion_rate": 0.25,
                "weighted_avg_price": 69.02,
                "avg_price_overall": 64.2,
                "price_stddev": 46.56,
                "price_bucket_counts": {
                    "low": 3,
                    "mid": 10,
                    "high": 3
                    }
                },
            "top_categories": 
            [
                {
                "category": "Beds, Crates & Gear",
                "purchase_ratio": 0.2,
                "avg_price": 116.66,
                "total_spend": 337.07,
                "total_events": 5
                },
                {
                "category": "Bowls & Feeders",
                "purchase_ratio": 0.4,
                "avg_price": 52.99,
                "total_spend": 197.46,
                "total_events": 5
            },
            {
                "category": "Food",
                "purchase_ratio": 0.2,
                "avg_price": 29.81,
                "total_spend": 79.11,
                "total_events": 5
            }
            ],
            "top_brands": [
            {
                "brand": "Frisco",
                "loyalty_score": 0.33,
                "total_purchases": 1,
                "total_spend": 306.0
            },
            {
                "brand": "Neater Pets",
                "loyalty_score": 0.4,
                "total_purchases": 2,
                "total_spend": 197.46
            },
            {
                "brand": "Purina ONE",
                "loyalty_score": 0.33,
                "total_purchases": 1,
                "total_spend": 69.04
            },
            {
                "brand": "FurHaven",
                "loyalty_score": 0.0,
                "total_purchases": 0,
                "total_spend": 31.07
            },
            {
                "brand": "Friskies",
                "loyalty_score": 0.0,
                "total_purchases": 0,
                "total_spend": 10.07
            }
            ],
            "recent_purchases": [
            {
                "name": "Neater Pets Neater Feeder Deluxe Elevated & Mess-Proof Dog Bowls, 1.5-cup & 2.2-cup, Red",
                "category": "Bowls & Feeders",
                "brand": "Neater Pets",
                "diet": None,
                "price": 38.99,
                "times_bought": 1
            },
            {
                "name": "Purina ONE Tender Selects Blend with Real Salmon Dry Cat Food, 16-lb bag",
                "category": "Food",
                "brand": "Purina ONE",
                "diet": "Indoor,High-Protein,Natural,With Grain",
                "price": 33.48,
                "times_bought": 1
            },
            ]
        }
        ]


    try:
        update_interaction_based_persona(24612503152, test_interaction_history, db)
    finally:
        db.close()



# This user demonstrates a balanced pet shopping behavior with a moderate 
# loyalty to brands, primarily purchasing bowls, feeders, and beds. They 
# have a preference for higher quality products, with an average purchase 
# price of $69.02 and a tendency to shop within the mid-price range. 
# Recent purchases indicate a focus on reliable and functional pet supplies, 
# specifically from Neater Pets and Purina ONE, suggesting an inclination 
# towards well-reviewed brands. Additionally, when it comes to dog toys, 
# they express a preference for luxury items, indicating a willingness to 
# invest in premium products for their pet's enjoyment.

# ->

# This user demonstrates a balanced pet shopping behavior with a moderate
#  loyalty to brands, primarily purchasing bowls, feeders, and beds. 
# They have a preference for higher quality products, with an average
#  purchase price of $69.02 and a tendency to shop within the mid-price
#  range. Recent purchases indicate a focus on reliable and functional
# pet supplies, specifically from Neater Pets and Purina ONE, suggesting
#  an inclination towards well-reviewed brands. However, when it comes 
# to dog toys, they now prefer to purchase cheap options due to durability 
# 'issues, moving away from a previous preference for luxury items.