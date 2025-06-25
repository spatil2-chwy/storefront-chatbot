from fastapi import APIRouter
from typing import List
from ..models.chat import ChatMessage, ChatMessageCreate
from src.services import user_service

router = APIRouter()

@router.get("/chat/messages", response_model=List[ChatMessage])
async def get_chat_messages():
    return await user_service.get_chat_messages()

@router.post("/chat/messages", response_model=ChatMessage)
async def add_chat_message(message_data: ChatMessageCreate):
    return await user_service.add_chat_message(message_data)

@router.delete("/chat/messages")
async def clear_chat_messages():
    await user_service.clear_chat_messages()
    return {"message": "Chat messages cleared"}
