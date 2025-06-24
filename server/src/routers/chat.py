from fastapi import APIRouter
from typing import List
from ..models.chat import ChatMessage, ChatMessageCreate
from storage import storage

router = APIRouter()

@router.get("/chat/messages", response_model=List[ChatMessage])
async def get_chat_messages():
    return await storage.get_chat_messages()

@router.post("/chat/messages", response_model=ChatMessage)
async def add_chat_message(message_data: ChatMessageCreate):
    return await storage.add_chat_message(message_data)

@router.delete("/chat/messages")
async def clear_chat_messages():
    await storage.clear_chat_messages()
    return {"message": "Chat messages cleared"}
