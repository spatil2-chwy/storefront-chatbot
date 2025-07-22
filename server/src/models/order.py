from sqlalchemy import Column, Integer, Float, DateTime, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator, String as SQLString
from datetime import datetime
from src.database import Base

class SQLiteDateTime(TypeDecorator):
    """SQLite datetime type that handles string conversion"""
    impl = SQLString
    
    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, str):
            try:
                return datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                return None
        return value

class Order(Base):
    __tablename__ = "orders"
    
    # Order identification
    order_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, nullable=False)
    order_date = Column(SQLiteDateTime, nullable=False, default=datetime.utcnow)
    
    # Order status
    status = Column(String, nullable=False, default="processing")  # processing, shipped, delivered, cancelled
    
    # Pricing
    subtotal = Column(Float, nullable=False)
    shipping_cost = Column(Float, nullable=False, default=0.0)
    tax_amount = Column(Float, nullable=False, default=0.0)
    total_amount = Column(Float, nullable=False)
    
    # Shipping Information
    shipping_first_name = Column(String, nullable=False)
    shipping_last_name = Column(String, nullable=False)
    shipping_email = Column(String, nullable=False)
    shipping_phone = Column(String)
    shipping_address = Column(String, nullable=False)
    shipping_city = Column(String, nullable=False)
    shipping_state = Column(String, nullable=False)
    shipping_zip_code = Column(String, nullable=False)
    
    # Payment Information (stored securely/masked)
    payment_method = Column(String, nullable=False, default="credit_card")
    card_last_four = Column(String)  # Only store last 4 digits
    cardholder_name = Column(String)
    
    # Billing Address (optional if same as shipping)
    billing_address = Column(String)
    billing_city = Column(String)
    billing_state = Column(String)
    billing_zip_code = Column(String)
    
    # Metadata
    created_at = Column(SQLiteDateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(SQLiteDateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to order items
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"
    
    # Item identification
    item_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=False)
    
    # Product information (snapshot at time of order)
    product_id = Column(Integer, nullable=False)
    product_title = Column(String, nullable=False)
    product_brand = Column(String)
    product_image = Column(String)
    
    # Purchase details
    quantity = Column(Integer, nullable=False)
    purchase_option = Column(String, nullable=False, default="buyonce")  # buyonce or autoship
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    # Relationship back to order
    order = relationship("Order", back_populates="items")
