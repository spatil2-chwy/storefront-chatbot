from sqlalchemy import Column, Integer, String, DateTime, Float, Text, JSON
from sqlalchemy.sql import func
from src.database import Base


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    customer_key = Column(Integer, nullable=False, index=True)
    event_type = Column(String(50), nullable=False)  # 'purchase', 'addToCart', 'productClick'
    item_id = Column(Integer, nullable=True)  # Product ID
    event_value = Column(Float, nullable=True)  # Price or other numeric value
    product_metadata = Column(JSON, nullable=True)  # Product details as JSON
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Interaction(id={self.id}, customer_key={self.customer_key}, event_type='{self.event_type}', item_id={self.item_id})>" 