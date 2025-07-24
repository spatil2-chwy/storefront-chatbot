from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator, String as SQLString
from src.database import Base

class SQLiteDate(TypeDecorator):
    """SQLite date type that handles string conversion"""
    impl = SQLString
    
    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, str):
            try:
                # Handle SQLite datetime format
                if ' ' in value:
                    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f").date()
                return datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                return None
        return value

class SQLiteDateTime(TypeDecorator):
    """SQLite datetime type that handles string conversion"""
    impl = SQLString
    
    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, str):
            try:
                # Try ISO format first
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                pass
            try:
                return datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                pass
            try:
                return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                pass
            return None
        return value

class PetProfile(Base):
    __tablename__ = "pet_profiles"
    
    pet_profile_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers_full.customer_id"), nullable=False)
    pet_name = Column(String)
    pet_type = Column(String)
    pet_breed = Column(String)
    pet_breed_size_type = Column(String, nullable=True)
    gender = Column(String)
    weight_type = Column(String, nullable=True)
    size_type = Column(String, nullable=True)
    birthday = Column(SQLiteDate)
    life_stage = Column(String)
    adopted = Column(Boolean)
    adoption_date = Column(SQLiteDate, nullable=True)
    status = Column(String)
    status_reason = Column(String, nullable=True)
    time_created = Column(SQLiteDateTime, default=datetime.now)
    time_updated = Column(SQLiteDateTime, nullable=True)
    weight = Column(Float)
    allergies = Column(String, nullable=True)  # Comma-separated allergy values
    # Note: allergy_count column still exists in database but is deprecated
    # It will be removed in a future migration
    photo_count = Column(Integer)
    pet_breed_id = Column(Integer)
    pet_type_id = Column(Integer)
    pet_new = Column(Boolean)
    first_birthday = Column(SQLiteDate, nullable=True)
    
    # Relationship back to User
    owner = relationship("User", back_populates="pets")
