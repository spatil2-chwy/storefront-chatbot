<<<<<<< feature/authentication
from sqlalchemy import Column, Integer, Float, DateTime, String
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

class User(Base):
    __tablename__ = "customers_full"
    
    customer_key = Column(Integer, primary_key=True, index=True)
    customer_id  = Column(Integer, unique=True, index=True, nullable=False)
    password      = Column(String, nullable=False)
    name          = Column(String, nullable=False)
    email         = Column(String, unique=True, index=True, nullable=False)
    
    operating_revenue_trailing_365   = Column(Float)
    customer_order_first_placed_dttm = Column(SQLiteDateTime)
    customer_address_zip             = Column(String)
    customer_address_city            = Column(String)
    customer_address_state           = Column(String)
    
    pets = relationship(
        "PetProfile",
        back_populates="owner",
        foreign_keys="PetProfile.customer_id",
        primaryjoin="User.customer_id == PetProfile.customer_id",
        cascade="all, delete-orphan",
    )
=======
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    id: int
    email: EmailStr
    name: str

class UserCreate(BaseModel):
    email: EmailStr
    name: str
>>>>>>> dev
