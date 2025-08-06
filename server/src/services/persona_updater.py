from fastapi import Depends
from sqlalchemy.orm import Session
from src.config.openai_loader import get_openai_client
from src.chat.prompts import persona_updater_system_prompt, interaction_based_persona_updater_system_prompt
from src.services.user_service import UserService
from src.database import get_db
from src.models.user import User
from typing import List, Dict, Any
import json


client = get_openai_client()
MODEL = "gpt-4.1"

user_svc = UserService()

MSG_TO_CAPTURE = 4 # how many USER messages to capture for persona update

def clean_message_content(content):
    """Remove image data from message content, keeping only text"""
    if isinstance(content, list):
        # Handle multi-modal content (text + image)
        text_parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "input_text":
                text_parts.append(item.get("text", ""))
        return " ".join(text_parts) if text_parts else ""
    elif isinstance(content, str):
        # Handle plain text content
        return content
    else:
        return str(content) if content else ""

def update_persona(customer_key: int, history: list[dict], db: Session) -> bool:
    user_info = user_svc.get_user(db, customer_key).persona_summary
    print(user_info)

    # Extract only user messages from history and clean them
    user_messages = []
    for msg in history:
        if msg.get("role") == "user":
            # Create a clean copy of the message without image data
            clean_msg = {
                "role": msg["role"],
                "content": clean_message_content(msg.get("content", ""))
            }
            user_messages.append(clean_msg)
    
    # Take the last MSG_TO_CAPTURE user messages
    recent_user_messages = user_messages[-MSG_TO_CAPTURE:] if len(user_messages) >= MSG_TO_CAPTURE else user_messages

    print(user_messages)
    
    print(f"Capturing {len(recent_user_messages)} user messages for persona update: {recent_user_messages}")

    response = client.chat.completions.create(
        model = MODEL,
        messages = [
            {"role": "system", "content": persona_updater_system_prompt},
            {"role": "user", "content": "Recent User Messages:\n" + str(recent_user_messages) + "\n\nPrevious persona summary: " + user_info}
        ],
        response_format={"type": "json_object"}
    )


    content = response.choices[0].message.content
    print(content)

    response_json = json.loads(content)
    if response_json.get("update_needed"):
        result = response_json.get("persona_summary")
    else:
        result = user_info

    
    # Update the user's persona summary
    user_svc.update_user(
        db=db,
        customer_key=customer_key,
        user_data=User(persona_summary=result)
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
            {"role": "system", "content": interaction_based_persona_updater_system_prompt},
            {"role": "user", "content": "Interaction History:\n" + str(interaction_history) + "\n\nPrevious persona summary: " + user_info}
        ],
        response_format={
            "type": "json_object"
        }
    )

    content = response.choices[0].message.content
    print(content)

    response_json = json.loads(content)
    if response_json.get("update_needed"):
        result = response_json.get("persona_summary")
    else:
        result = user_info
    
    # Update the user's persona summary
    user_svc.update_user(
        db=db,
        customer_key=customer_key,
        user_data=User(persona_summary=result)
    )

    return True

# test
if __name__ == "__main__":
    print("Testing persona updater...")
    
    # Test 1: Chat-based persona update with mixed message types
    test_history = [
        {"role": "system", "content": "You are a helpful assistant. (This message gets thrown away)"},
        {"role": "user", "content": "I need help finding dog food"},
        {"role": "assistant", "content": "I'd be happy to help! What type of dog do you have?"},
        {"role": "user", "content": "I have a golden retriever"},
        {"role": "assistant", "content": "Great! Golden retrievers are wonderful dogs."},
        {"role": "user", "content": "He's very active and energetic"},
        {"role": "assistant", "content": "Active dogs need high-quality nutrition."},
        {"role": "user", "content": "What about grain-free options?"},
        {"role": "assistant", "content": "Grain-free can be good for some dogs."},
        {"role": "user", "content": "I'm so upset, my dog just keeps ruining all his toys. I will just buy cheap toys from now on"},
        {"role": "assistant", "content": "I'm sorry to hear that. It's tough when pets are destructive."},
    ]
    
    # Test the user message extraction logic
    user_messages = [msg for msg in test_history if msg.get("role") == "user"]
    recent_user_messages = user_messages[-MSG_TO_CAPTURE:] if len(user_messages) >= MSG_TO_CAPTURE else user_messages
    
    print(f"Total messages in history: {len(test_history)}")
    print(f"User messages found: {len(user_messages)}")
    print(f"Messages to capture (MSG_TO_CAPTURE={MSG_TO_CAPTURE}): {len(recent_user_messages)}")
    print(f"Recent user messages: {recent_user_messages}")
    
    # Get a database session for testing
    db = next(get_db())
    try:
        print("Testing chat-based persona update...")
        result = update_persona(24612503152, test_history, db)
        print(f"Chat-based update result: {result}")
    except Exception as e:
        print(f"Chat-based update error: {e}")
    finally:
        db.close()

    # Test 2: Interaction-based persona update
    test_interaction_history = [
        {
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
            "top_categories": [
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
                }
            ],
            "recent_purchases": [
                {
                    "name": "Neater Pets Neater Feeder Deluxe Elevated & Mess-Proof Dog Bowls",
                    "category": "Bowls & Feeders",
                    "brand": "Neater Pets",
                    "diet": None,
                    "price": 38.99,
                    "times_bought": 1
                },
                {
                    "name": "Purina ONE Tender Selects Blend with Real Salmon Dry Cat Food",
                    "category": "Food",
                    "brand": "Purina ONE",
                    "diet": "Indoor,High-Protein,Natural,With Grain",
                    "price": 33.48,
                    "times_bought": 1
                }
            ]
        }
    ]

    db = next(get_db())
    try:
        print("Testing interaction-based persona update...")
        result = update_interaction_based_persona(24612503152, test_interaction_history, db)
        print(f"Interaction-based update result: {result}")
    except Exception as e:
        print(f"Interaction-based update error: {e}")
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