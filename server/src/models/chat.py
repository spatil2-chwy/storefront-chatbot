from sqlalchemy import Column, String, Text, DateTime, Enum
from src.models.constants import SenderType as DbSenderType
from src.database import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id        = Column(String, primary_key=True, index=True)
    content   = Column(Text, nullable=False)
    sender    = Column(Enum(DbSenderType), nullable=False)
    timestamp = Column(DateTime, nullable=False)

