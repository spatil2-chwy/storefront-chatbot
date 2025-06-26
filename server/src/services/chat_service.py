from sqlalchemy.orm import Session
from src.models.chat import ChatMessage

class ChatService:
    def get_message(self, db: Session, chat_id: str) -> ChatMessage | None:
        return (
            db.query(ChatMessage)
              .filter(ChatMessage.id == chat_id)
              .one_or_none()
        )

    def create_message(self, db: Session, payload: ChatMessage) -> ChatMessage:
        db.add(payload)
        db.commit()
        db.refresh(payload)
        return payload