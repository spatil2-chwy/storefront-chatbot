<<<<<<< HEAD
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from ..models.chat import ChatMessage, ChatMessageCreate
from src.services import user_service
from src.services.chatbot_logic import chat
=======
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.schemas import ChatMessage as ChatSchema
from src.services.chat_service import ChatService
>>>>>>> origin/dev

router = APIRouter(prefix="/chats", tags=["chats"])
chat_svc = ChatService()

@router.get("/{chat_id}", response_model=ChatSchema)
def get_chat_message(chat_id: str, db: Session = Depends(get_db)):
    msg = chat_svc.get_message(db, chat_id)
    if not msg:
        raise HTTPException(status_code=404, detail="Chat message not found")
    return msg

<<<<<<< HEAD
@router.post("/chat/messages", response_model=ChatMessage)
async def add_chat_message(message_data: ChatMessageCreate):
    return await user_service.add_chat_message(message_data)

@router.delete("/chat/messages")
async def clear_chat_messages():
    await user_service.clear_chat_messages()
    return {"message": "Chat messages cleared"}

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    history: list

@router.post("/chatbot")
async def chatbot(request: ChatRequest):
    reply = chat(
        user_input=request.message,
        history=request.history,
    )

    return {"response": reply}
=======
@router.post("/", response_model=ChatSchema)
def create_chat_message(payload: ChatSchema, db: Session = Depends(get_db)):
    return chat_svc.create_message(db, ChatMessage(**payload.dict()))
>>>>>>> origin/dev
