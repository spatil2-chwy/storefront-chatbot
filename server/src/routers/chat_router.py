from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.schemas import ChatMessage as ChatSchema
from src.services.chat_service import ChatService

router = APIRouter(prefix="/chats", tags=["chats"])
chat_svc = ChatService()

@router.get("/{chat_id}", response_model=ChatSchema)
def get_chat_message(chat_id: str, db: Session = Depends(get_db)):
    msg = chat_svc.get_message(db, chat_id)
    if not msg:
        raise HTTPException(status_code=404, detail="Chat message not found")
    return msg

@router.post("/", response_model=ChatSchema)
def create_chat_message(payload: ChatSchema, db: Session = Depends(get_db)):
    return chat_svc.create_message(db, ChatMessage(**payload.dict()))
