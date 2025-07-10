from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from src.database import get_db
from src.schemas import ChatMessage as ChatSchema
from src.models.chat import ChatMessage
from src.services.chat_service import ChatService
from src.services.user_service import UserService
from src.services.chatbot_logic import chat, chat_stream_with_products
from src.services.chatmodes_service import compare_products, ask_about_product
import json

router = APIRouter(prefix="/chats", tags=["chats"])
chat_svc = ChatService()
user_svc = UserService()

@router.get("/{chat_id}", response_model=ChatSchema)
def get_chat_message(chat_id: str, db: Session = Depends(get_db)):
    msg = chat_svc.get_message(db, chat_id)
    if not msg:
        raise HTTPException(status_code=404, detail="Chat message not found")
    return msg

class ChatRequest(BaseModel):
    message: str
    history: list
    customer_key: Optional[int] = None

class ComparisonRequest(BaseModel):
    message: str
    products: List[dict]
    history: Optional[list] = []  # Add conversation history

class AskAboutProductRequest(BaseModel):
    message: str
    product: dict
    history: Optional[list] = []  # Add conversation history

class PersonalizedGreetingRequest(BaseModel):
    customer_key: Optional[int] = None

@router.post("/chatbot")
async def chatbot(request: ChatRequest, db: Session = Depends(get_db)):
    user_context = ""
    
    # Get user context if customer_key is provided
    if request.customer_key:
        try:
            user_context_data = user_svc.get_user_context_for_chat(db, request.customer_key)
            if user_context_data:
                user_context = user_svc.format_pet_context_for_ai(user_context_data)
                # print(f"User context for customer {request.customer_key}:\n{user_context}")
        except Exception as e:
            print(f"Error getting user context for customer {request.customer_key}: {e}")
    
    reply = chat(
        user_input=request.message,
        history=request.history,
        user_context=user_context
    )

    return {"response": reply}

@router.post("/compare")
async def compare_products_endpoint(request: ComparisonRequest):
    """
    Handle product comparison requests.
    """
    try:
        response = compare_products(request.message, request.products, request.history)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


@router.post("/ask_about_product")
async def ask_about_product_endpoint(request: AskAboutProductRequest):
    """
    Handle product question requests
    """
    try:
        response = ask_about_product(request.message, request.product, request.history)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Product question failed: {str(e)}")

@router.post("/", response_model=ChatSchema)
def create_chat_message(payload: ChatSchema, db: Session = Depends(get_db)):
    return chat_svc.create_message(db, ChatMessage(**payload.dict()))

@router.post("/personalized_greeting")
async def personalized_greeting(request: PersonalizedGreetingRequest, db: Session = Depends(get_db)):
    """
    Generate a personalized greeting for a customer based on their profile and pets.
    """
    try:
        from src.services.greeting_service import generate_personalized_greeting
        
        greeting = generate_personalized_greeting(db, request.customer_key)
        return {"response": {"greeting": greeting}}
    except Exception as e:
        print(f"Error generating personalized greeting: {e}")
        # Fallback greeting
        greeting = "Hey there! What can I help you find for your furry friends today?"
        return {"response": {"greeting": greeting}}

@router.post("/chatbot/stream")
async def chatbot_stream(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Streaming version of the chatbot endpoint that returns Server-Sent Events.
    """
    user_context = ""
    
    # Get user context if customer_key is provided
    if request.customer_key:
        try:
            user_context_data = user_svc.get_user_context_for_chat(db, request.customer_key)
            if user_context_data:
                user_context = user_svc.format_pet_context_for_ai(user_context_data)
        except Exception as e:
            print(f"Error getting user context for customer {request.customer_key}: {e}")
    
    def generate_stream():
        try:
            # Get the generator and products from chat_stream_with_products
            stream_generator, products = chat_stream_with_products(
                user_input=request.message,
                history=request.history,
                user_context=user_context
            )
            
            print(f"Streaming response for: {request.message}")
            print(f"Products found: {len(products) if products else 0}")
            
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
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )