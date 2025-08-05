# log interactions
# EVENT_TYPE --> ('purchase', 'addToCart', 'productClick')
# persona update background task

from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from src.database import get_db
from src.schemas import InteractionRequest
from src.services.persona_updater import update_interaction_based_persona
from src.services.interaction_service import interaction_svc
from src.services.interaction_processor import interaction_processor

router = APIRouter(prefix="/interactions", tags=["interactions"])

# Session-based purchase tracking - resets on server restart
session_purchase_counts = {}  # {customer_key: purchase_count}

def update_interaction_based_persona_background_task(customer_key: int, interaction_history: List[Dict[str, Any]]):
    """Background task to update user persona based on interaction history"""
    # Get a new database session for the background task
    db = next(get_db())
    try:
        print(f"Starting persona update background task for customer {customer_key}")
        success = update_interaction_based_persona(customer_key, interaction_history, db)
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

def should_update_interaction_based_persona(customer_key: int) -> bool:
    """Check if we should trigger a persona update based on session purchase count"""
    # Get current session purchase count for this customer
    current_purchase_count = session_purchase_counts.get(customer_key, 0)
    
    # Trigger update if 3 or more purchases in this session
    should_update = current_purchase_count >= 3
    
    print(f"Session purchase check for customer {customer_key}: count={current_purchase_count}, should_update={should_update}")
    
    return should_update

def increment_session_purchase_count(customer_key: int):
    """Increment the session purchase count for a customer"""
    if customer_key not in session_purchase_counts:
        session_purchase_counts[customer_key] = 0
    session_purchase_counts[customer_key] += 1
    print(f"Incremented session purchase count for customer {customer_key}: {session_purchase_counts[customer_key]}")

@router.get("/session_purchase_counts")
async def get_session_purchase_counts():
    """Debug endpoint to check current session purchase counts"""
    return {"session_purchase_counts": session_purchase_counts}

@router.post("/log_interaction")
async def log_interaction(request: InteractionRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Log an interaction and trigger persona update if needed"""
    # Log the interaction
    interaction = interaction_svc.log_interaction(
        db, 
        request.customer_key, 
        request.event_type, 
        request.item_id, 
        request.event_value, 
        request.product_metadata
    )
    
    # If this is a purchase, increment session counter
    if request.event_type == "purchase":
        increment_session_purchase_count(request.customer_key)
    
    # Check if we should trigger a persona update (session-based)
    if should_update_interaction_based_persona(request.customer_key):
        print(f"Triggering persona update for customer {request.customer_key} - 3+ purchases in session")
        
        # Get all interactions for this customer (no time limit - just session data)
        # Since we're session-aware, we'll get all interactions logged in this session
        raw_interaction_history = interaction_svc.get_interaction_history(db, request.customer_key)
        
        if raw_interaction_history:
            # Process interactions into structured format
            processed_interactions = interaction_processor.process_user_interactions_from_list(raw_interaction_history)
            
            if processed_interactions:
                # Add background task to update persona with processed data
                background_tasks.add_task(
                    update_interaction_based_persona_background_task,
                    request.customer_key,
                    [processed_interactions]  # Wrap in list to match expected format
                )
    
    return {"message": "Interaction logged successfully", "interaction_id": interaction.id}