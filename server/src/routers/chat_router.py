# Chat router - handles all chat-related endpoints including chatbot, product comparison, and streaming
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from src.database import get_db
from src.schemas import ChatMessage as ChatSchema
from src.models.chat import ChatMessage
from src.services.chat_service import ChatService
from src.services.user_service import UserService
from src.services.pet_service import PetService
from src.chat.chatbot_engine import chat_stream_with_products
from src.chat.chat_modes import compare_products, ask_about_product
from src.services.persona_updater import update_persona
import json

router = APIRouter(prefix="/chats", tags=["chats"])
chat_svc = ChatService()
user_svc = UserService()
pet_svc = PetService()

# Message counter for persona updates - tracks messages per customer
PERSONA_UPDATE_INTERVAL = 8  # Update persona every N messages (default: 5)

def update_persona_background_task(customer_key: int, history: List[Dict[str, Any]]):
    """Background task to update user persona based on chat history"""
    # Get a new database session for the background task
    db = next(get_db())
    try:
        print(f"Starting persona update background task for customer {customer_key}")
        success = update_persona(customer_key, history, db)
        if success:
            print(f"Persona updated successfully for customer {customer_key}")
        else:
            print(f"No persona update needed for customer {customer_key}")
    except Exception as e:
        print(f"Error updating persona for customer {customer_key}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def should_update_persona(history: List[Dict[str, Any]]) -> bool:
    """Check if we should trigger a persona update based on message count"""
    # Count user messages in history (exclude system messages)
    user_message_count = len([msg for msg in history if msg.get("role") == "user"])
    
    # Trigger update if user message count is a multiple of the interval and > 0
    should_update = user_message_count > 0 and user_message_count % PERSONA_UPDATE_INTERVAL == 0
    
    # Add detailed logging
    print(f"Persona update check: user_message_count={user_message_count}, PERSONA_UPDATE_INTERVAL={PERSONA_UPDATE_INTERVAL}, should_update={should_update}")
    
    return should_update

@router.get("/{chat_id}", response_model=ChatSchema)
def get_chat_message(chat_id: str, db: Session = Depends(get_db)):
    # Get a specific chat message by ID
    msg = chat_svc.get_message(db, chat_id)
    if not msg:
        raise HTTPException(status_code=404, detail="Chat message not found")
    return msg

class ChatRequest(BaseModel):
    message: str
    history: list
    customer_key: Optional[int] = None
    image: Optional[str] = None  # Base64 encoded image
    selected_pet: Optional[dict] = None  # Selected pet context

class ComparisonRequest(BaseModel):
    message: str
    products: List[dict]
    history: List[Dict[str, Any]] = []  # Add conversation history
    customer_key: Optional[int] = None  # Add customer_key for persona updates
    image: Optional[str] = None  # Base64 encoded image

class AskAboutProductRequest(BaseModel):
    message: str
    product: dict
    history: List[Dict[str, Any]] = []  # Add conversation history
    customer_key: Optional[int] = None  # Add customer_key for persona updates
    image: Optional[str] = None  # Base64 encoded image

class PersonalizedGreetingRequest(BaseModel):
    customer_key: Optional[int] = None

class PetSelectionRequest(BaseModel):
    customer_key: int
    pet_id: str  # Can be pet_profile_id or "browse"

class PetProfileRequest(BaseModel):
    pet_profile_id: int
class ManualPersonaUpdateRequest(BaseModel):
    customer_key: int
    history: List[Dict[str, Any]]

@router.post("/compare")
async def compare_products_endpoint(request: ComparisonRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Compare multiple products based on user question
    try:
        response = compare_products(request.message, request.products, request.history)
        
        # Trigger persona update background task if conditions are met
        updated_history = request.history + [{"role": "user", "content": request.message}]

        print(f"Number of messages in updated history: {len(updated_history)}")
        if request.customer_key and should_update_persona(updated_history):
            print(f"Triggering persona update background task for customer {request.customer_key} (compare endpoint)")
            background_tasks.add_task(
                update_persona_background_task,
                request.customer_key,
                updated_history
            )
        
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


@router.post("/ask_about_product")
async def ask_about_product_endpoint(request: AskAboutProductRequest, background_tasks: BackgroundTasks):
    # Ask specific questions about a single product
    try:
        response = ask_about_product(request.message, request.product, request.history)
        
        # Trigger persona update background task if conditions are met
        updated_history = request.history + [{"role": "user", "content": request.message}]
        if request.customer_key and should_update_persona(updated_history):
            print(f"Triggering persona update background task for customer {request.customer_key} (ask_about_product endpoint)")
            background_tasks.add_task(
                update_persona_background_task,
                request.customer_key,
                updated_history
            )
        
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Product question failed: {str(e)}")

@router.post("/", response_model=ChatSchema)
def create_chat_message(payload: ChatSchema, db: Session = Depends(get_db)):
    # Create a new chat message
    return chat_svc.create_message(db, ChatMessage(**payload.dict()))

@router.post("/personalized_greeting")
async def personalized_greeting(request: PersonalizedGreetingRequest, db: Session = Depends(get_db)):
    # Generate personalized greeting based on user's pets and profile
    try:
        from src.chat.greeting_generator import generate_personalized_greeting
        
        greeting_data = generate_personalized_greeting(db, request.customer_key)
        return {"response": greeting_data}
    except Exception as e:
        print(f"Error generating personalized greeting: {e}")
        # Fallback greeting
        fallback_greeting = {
            "greeting": "Hey there! What can I help you find for your furry friends today?",
            "has_pets": False,
            "pet_options": []
        }
        return {"response": fallback_greeting}

@router.post("/select_pet")
async def select_pet(request: PetSelectionRequest, db: Session = Depends(get_db)):
    # Handle pet selection - returns pet profile or browse message
    try:
        if request.pet_id == "browse":
            return {
                "response": {
                    "type": "browse",
                    "message": "Sounds good! What are you looking for today?",
                    "pet_context": None
                }
            }
        
        # Get pet profile
        pet_profile_id = int(request.pet_id)
        pet = pet_svc.get_pet_profile(db, pet_profile_id)
        
        if not pet:
            raise HTTPException(status_code=404, detail="Pet not found")
        
        # Format pet information for display
        pet_info = {
            "id": pet.pet_profile_id,
            "name": pet.pet_name,
            "type": pet.pet_type,
            "breed": pet.pet_breed,
            "gender": pet.gender,
            "weight": pet.weight,
            "life_stage": pet.life_stage,
            "birthday": pet.birthday.isoformat() if pet.birthday else None,
            "allergies": pet.allergies or "",
            "is_new": pet.pet_new
        }
        
        # Create pet context for chat
        pet_context = f"Pet: {pet.pet_name} ({pet.pet_type})"
        if pet.pet_breed and pet.pet_breed.lower() != "unknown":
            pet_context += f", {pet.pet_breed}"
        if pet.weight:
            pet_context += f", {pet.weight}lbs"
        if pet.life_stage and pet.life_stage.lower() != "unknown":
            pet_context += f", {pet.life_stage}"
        
        return {
            "response": {
                "type": "pet_profile",
                "pet_info": pet_info,
                "pet_context": pet_context
            }
        }
        
    except Exception as e:
        print(f"Error selecting pet: {e}")
        raise HTTPException(status_code=500, detail=f"Pet selection failed: {str(e)}")

@router.get("/pet_profile/{pet_profile_id}")
async def get_pet_profile(pet_profile_id: int, db: Session = Depends(get_db)):
    # Get detailed pet profile information
    try:
        pet = pet_svc.get_pet_profile(db, pet_profile_id)
        
        if not pet:
            raise HTTPException(status_code=404, detail="Pet not found")
        
        # Format pet information for editing
        pet_info = {
            "id": pet.pet_profile_id,
            "name": pet.pet_name or "",
            "type": pet.pet_type or "",
            "breed": pet.pet_breed or "",
            "gender": pet.gender or "",
            "weight": pet.weight or 0,
            "life_stage": pet.life_stage or "",
            "birthday": pet.birthday.isoformat() if pet.birthday else None,
            "allergies": pet.allergies or "",
            "is_new": pet.pet_new or False
        }
        
        return {"response": {"pet_info": pet_info}}
        
    except Exception as e:
        print(f"Error getting pet profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get pet profile: {str(e)}")

@router.put("/pet_profile/{pet_profile_id}")
async def update_pet_profile(pet_profile_id: int, pet_data: Dict[str, Any], db: Session = Depends(get_db)):
    # Update pet profile information
    try:
        from src.models.pet import PetProfile
        from src.utils.life_stage_calculator import calculate_life_stage
        
        # Get existing pet
        existing_pet = pet_svc.get_pet_profile(db, pet_profile_id)
        if not existing_pet:
            raise HTTPException(status_code=404, detail="Pet not found")
        
        # Update pet fields
        if "name" in pet_data:
            existing_pet.pet_name = pet_data["name"]
        if "type" in pet_data:
            existing_pet.pet_type = pet_data["type"]
        if "breed" in pet_data:
            existing_pet.pet_breed = pet_data["breed"]
        if "gender" in pet_data:
            existing_pet.gender = pet_data["gender"]
        if "weight" in pet_data:
            existing_pet.weight = pet_data["weight"]
        if "birthday" in pet_data:
            if pet_data["birthday"]:
                from datetime import datetime
                existing_pet.birthday = datetime.fromisoformat(pet_data["birthday"]).date()
            else:
                existing_pet.birthday = None
        if "allergies" in pet_data:
            # Store allergies as comma-separated string
            existing_pet.allergies = pet_data["allergies"]
        
        # Automatically calculate and update life stage based on birthday and pet type
        existing_pet.life_stage = calculate_life_stage(
            existing_pet.pet_type, 
            existing_pet.birthday, 
            existing_pet.life_stage
        )
        
        # Save changes
        updated_pet = pet_svc.update_pet(db, pet_profile_id, existing_pet)
        
        if not updated_pet:
            raise HTTPException(status_code=500, detail="Failed to update pet profile")
        
        # Format updated pet information
        pet_info = {
            "id": updated_pet.pet_profile_id,
            "name": updated_pet.pet_name,
            "type": updated_pet.pet_type,
            "breed": updated_pet.pet_breed,
            "gender": updated_pet.gender,
            "weight": updated_pet.weight,
            "life_stage": updated_pet.life_stage,
            "birthday": updated_pet.birthday.isoformat() if updated_pet.birthday else None,
            "allergies": updated_pet.allergies or "",
            "is_new": updated_pet.pet_new
        }
        
        # Create updated pet context
        pet_context = f"Pet: {updated_pet.pet_name} ({updated_pet.pet_type})"
        if updated_pet.pet_breed and updated_pet.pet_breed.lower() != "unknown":
            pet_context += f", {updated_pet.pet_breed}"
        if updated_pet.weight:
            pet_context += f", {updated_pet.weight}lbs"
        if updated_pet.life_stage and updated_pet.life_stage.lower() != "unknown":
            pet_context += f", {updated_pet.life_stage}"
        
        return {
            "response": {
                "type": "pet_updated",
                "pet_info": pet_info,
                "pet_context": pet_context
            }
        }
        
    except Exception as e:
        print(f"Error updating pet profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update pet profile: {str(e)}")

# @router.post("/update_persona_manual")
# async def manual_persona_update(request: ManualPersonaUpdateRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
#     """Manual endpoint to trigger persona update for testing purposes"""
#     try:
#         print(f"Manual persona update triggered for customer {request.customer_key}")
#         background_tasks.add_task(
#             update_persona_background_task,
#             request.customer_key,
#             request.history
#         )
#         return {"message": f"Persona update triggered for customer {request.customer_key}"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Manual persona update failed: {str(e)}")

@router.post("/chatbot/stream")
async def chatbot_stream(request: ChatRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Streaming chatbot endpoint - returns Server-Sent Events with real-time responses
    user_context = ""
    pet_profile = None
    user_context_data = None
    
    # Get user context if customer_key is provided
    if request.customer_key:
        try:
            user_context_data = user_svc.get_user_context_for_chat(db, request.customer_key)
            if user_context_data:
                user_context = user_svc.format_pet_context_for_ai(user_context_data)
        except Exception as e:
            print(f"Error getting user context for customer {request.customer_key}: {e}")
    
    # Add selected pet context if provided
    if request.selected_pet:
        pet_profile = request.selected_pet  # Use the selected pet as pet profile
        pet_context = f"Selected Pet: {request.selected_pet.get('name', 'Unknown')} ({request.selected_pet.get('type', 'Unknown')})"
        if request.selected_pet.get('breed') and request.selected_pet.get('breed').lower() != 'unknown':
            pet_context += f", {request.selected_pet.get('breed')}"
        if request.selected_pet.get('weight'):
            pet_context += f", {request.selected_pet.get('weight')}lbs"
        if request.selected_pet.get('life_stage') and request.selected_pet.get('life_stage').lower() != 'unknown':
            pet_context += f", {request.selected_pet.get('life_stage')}"
        
        if user_context:
            user_context += f"\n{pet_context}"
        else:
            user_context = pet_context
    
    def generate_stream():
        try:
            # Get the generator, products, and buttons from chat_stream_with_products
            stream_generator, products, buttons = chat_stream_with_products(
                user_input=request.message,
                history=request.history,
                user_context=user_context,
                image_base64=request.image,
                pet_profile=pet_profile,
                user_context_data=user_context_data
            )
            
            print(f"Streaming response for: {request.message}")
            print(f"Products found: {len(products) if products else 0}")
            print(f"Buttons found: {buttons if buttons else 'None'}")
            
            # Send products first if there are any
            if products:
                print(f"Sending products before streaming text: {len(products)} products")
                # Convert Product objects to dictionaries for JSON serialization
                products_dict = []
                for product in products:
                    try:
                        # Product is a Pydantic model, use dict() method
                        product_dict = product.dict()
                        
                        # Clean string values to prevent JSON serialization issues
                        for key, value in product_dict.items():
                            if isinstance(value, str):
                                # Clean any problematic string values
                                product_dict[key] = value.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
                            elif isinstance(value, list):
                                # Handle lists that might contain objects
                                cleaned_list = []
                                for item in value:
                                    if isinstance(item, str):
                                        cleaned_list.append(item.replace('\n', ' ').replace('\r', ' ').replace('\t', ' '))
                                    elif hasattr(item, 'dict'):
                                        cleaned_list.append(item.dict())
                                    else:
                                        cleaned_list.append(item)
                                product_dict[key] = cleaned_list
                        
                        products_dict.append(product_dict)
                    except Exception as e:
                        print(f"Error serializing product: {e}")
                        import traceback
                        traceback.print_exc()
                        continue
                
                try:
                    # Send products event
                    products_data = {'products': products_dict}
                    products_json = json.dumps(products_data, ensure_ascii=False)
                    print(f"Products JSON length: {len(products_json)}")
                    print(f"Products count: {len(products_dict)}")
                    print(f"Sending products event before text")
                    yield f"data: {products_json}\n\n"
                except Exception as e:
                    print(f"Error serializing products data: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Stream the text chunks
            for chunk in stream_generator:
                # print(f"Streaming chunk: {chunk[:10]}...")
                # Format as Server-Sent Event
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
            # Send buttons if available
            if buttons:
                try:
                    buttons_data = {'buttons': buttons}
                    buttons_json = json.dumps(buttons_data, ensure_ascii=False)
                    print(f"Sending buttons: {buttons}")
                    yield f"data: {buttons_json}\n\n"
                except Exception as e:
                    print(f"Error serializing buttons data: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Send end signal
            # print(f"Sending end signal")
            try:
                # Send end signal
                end_signal = {'end': True}
                end_json = json.dumps(end_signal, ensure_ascii=False)
                # print(f"Sending end signal")
                yield f"data: {end_json}\n\n"
                
            except Exception as e:
                print(f"Error serializing end data: {e}")
                import traceback
                traceback.print_exc()
                # Send end signal without products if serialization fails
                yield f"data: {json.dumps({'end': True})}\n\n"
        except Exception as e:
            print(f"Error in streaming: {e}")
            import traceback
            traceback.print_exc()
            # Send error signal
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    # Trigger persona update background task if conditions are met
    if request.customer_key:
        # Create new history including the current message
        updated_history = request.history + [{"role": "user", "content": request.message}]
        if should_update_persona(updated_history):
            print(f"Triggering persona update background task for customer {request.customer_key}")
            background_tasks.add_task(
                update_persona_background_task,
                request.customer_key,
                updated_history
            )
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )