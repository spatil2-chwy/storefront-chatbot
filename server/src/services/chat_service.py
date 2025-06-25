from typing import List
from datetime import datetime
import uuid
from src.models.chat import ChatMessage, ChatMessageCreate
from src.models.constants import SenderType

class ChatService:
    def __init__(self):
        self.chat_messages: List[ChatMessage] = []
        self._initialize_dummy_data()

    def _initialize_dummy_data(self):
        self.chat_messages.append(ChatMessage(
            id=str(uuid.uuid4()),
            content="Hello! How can I help you find the perfect pet food today?",
            sender=SenderType.AI,
            timestamp=datetime.now()
        ))

    async def get_chat_messages(self) -> List[ChatMessage]:
        return self.chat_messages

    async def add_chat_message(self, message_data: ChatMessageCreate) -> ChatMessage:
        msg = ChatMessage(
            id=str(uuid.uuid4()),
            content=message_data.content,
            sender=message_data.sender,
            timestamp=datetime.now()
        )
        self.chat_messages.append(msg)
        return msg

    async def clear_chat_messages(self) -> None:
        self.chat_messages.clear()