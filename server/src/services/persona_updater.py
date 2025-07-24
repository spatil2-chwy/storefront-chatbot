from fastapi import Depends
from sqlalchemy.orm import Session
from src.config.openai_loader import get_openai_client
from src.chat.prompts import persona_updater_system_prompt
from src.services.user_service import UserService
from src.database import get_db
from src.models.user import User


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