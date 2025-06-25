from pydantic import BaseModel
from datetime import datetime
from .constants import SenderType

class ChatMessage(BaseModel):
    id: str                  
    content: str              
    sender: SenderType        
    timestamp: datetime       

class ChatMessageCreate(BaseModel):
    content: str              
    sender: SenderType      
