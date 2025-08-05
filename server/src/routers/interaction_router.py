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

def should_update_interaction_based_persona(interaction_history: List[Dict[str, Any]]) -> bool:
    """Check if we should trigger a persona update based on message count"""
    # count if 3 purchases have been made in the last 30 minutes
    purchase_count = sum(1 for interaction in interaction_history if interaction.get("event_type") == "purchase")
    return purchase_count >= 3


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
    
    # Get recent interaction history for this customer (last 30 minutes)
    raw_interaction_history = interaction_svc.get_interaction_history(db, request.customer_key, hours_back=0, minutes_back=30)
    
    # Check if we should trigger a persona update
    if should_update_interaction_based_persona(raw_interaction_history):
        print(f"Triggering persona update for customer {request.customer_key} - 3+ purchases detected")
        
        # Process interactions into structured format
        processed_interactions = interaction_processor.process_user_interactions(db, request.customer_key, hours_back=0, minutes_back=30)
        
        if processed_interactions:
            # Add background task to update persona with processed data
            background_tasks.add_task(
                update_interaction_based_persona_background_task,
                request.customer_key,
                [processed_interactions]  # Wrap in list to match expected format
            )
    
    return {"message": "Interaction logged successfully", "interaction_id": interaction.id}