from sqlalchemy.orm import Session
from src.models.chat import ChatMessage

class ChatService:
    """
    Service class for managing chat message operations in the database.
    Provides methods for creating and retrieving chat messages.
    """
    
    def get_message(self, db: Session, chat_id: str) -> ChatMessage | None:
        """
        Retrieve a chat message by its ID.
        
        Args:
            db (Session): Database session
            chat_id (str): ID of the chat message to retrieve
        
        Returns:
            ChatMessage | None: The chat message if found, None otherwise
        """
        return (
            db.query(ChatMessage)
              .filter(ChatMessage.id == chat_id)
              .one_or_none()
        )

    def create_message(self, db: Session, payload: ChatMessage) -> ChatMessage:
        """
        Create a new chat message in the database.
        
        Args:
            db (Session): Database session
            payload (ChatMessage): Chat message to create
        
        Returns:
            ChatMessage: The created chat message
        """
        db.add(payload)
        db.commit()
        db.refresh(payload)
        return payload