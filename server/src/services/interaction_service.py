from sqlalchemy.orm import Session
from src.models.interaction import Interaction
from typing import List, Dict, Any, Optional


class InteractionService:
    def __init__(self):
        pass

    def log_interaction(self, db: Session, customer_key: int, event_type: str, 
                       item_id: Optional[int] = None, event_value: Optional[float] = None, 
                       product_metadata: Optional[dict] = None) -> Interaction:
        """Log a user interaction"""
        interaction = Interaction(
            customer_key=customer_key,
            event_type=event_type,
            item_id=item_id,
            event_value=event_value,
            product_metadata=product_metadata
        )
        
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        return interaction

    def get_interaction_history(self, db: Session, customer_key: int) -> List[Dict[str, Any]]:
        """Get all interaction history for a customer"""
        interactions = db.query(Interaction).filter(
            Interaction.customer_key == customer_key
        ).order_by(Interaction.timestamp.desc()).all()
        
        return [
            {
                "id": interaction.id,
                "customer_key": interaction.customer_key,
                "event_type": interaction.event_type,
                "item_id": interaction.item_id,
                "event_value": interaction.event_value,
                "product_metadata": interaction.product_metadata,
                "timestamp": interaction.timestamp.isoformat()
            }
            for interaction in interactions
        ]

    def get_purchase_count(self, db: Session, customer_key: int) -> int:
        """Get the count of all purchase events for a customer"""
        return db.query(Interaction).filter(
            Interaction.customer_key == customer_key,
            Interaction.event_type == "purchase"
        ).count()


# Create a singleton instance
interaction_svc = InteractionService()
