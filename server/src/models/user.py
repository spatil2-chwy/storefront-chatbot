from sqlalchemy import Column, Integer, Float, DateTime, String
from sqlalchemy.orm import relationship
from src.database import Base

class User(Base):
    __tablename__ = "customers_full"
    
    customer_key = Column(Integer, primary_key=True, index=True)
    customer_id  = Column(Integer, unique=True, index=True, nullable=False)
    password      = Column(String, nullable=False)
    name          = Column(String, nullable=False)
    email         = Column(String, unique=True, index=True, nullable=False)
    
    operating_revenue_trailing_365   = Column(Float)
    customer_order_first_placed_dttm = Column(DateTime)
    customer_address_zip             = Column(String)
    customer_address_city            = Column(String)
    customer_address_state           = Column(String)
    
    pets = relationship(
        "PetProfile",
        back_populates="owner",
        cascade="all, delete-orphan",
    )
