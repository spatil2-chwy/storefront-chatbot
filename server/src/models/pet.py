from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base

class PetProfile(Base):
    __tablename__ = "pet_profiles"
    
    pet_profile_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers_full.customer_key"), nullable=False)
    pet_name = Column(String)
    pet_type = Column(String)
    pet_breed = Column(String)
    gender = Column(String)
    birthday = Column(Date)
    life_stage = Column(String)
    adopted = Column(Boolean)
    adoption_date = Column(Date, nullable=True)
    status = Column(String)
    status_reason = Column(String, nullable=True)
    time_created = Column(DateTime)
    time_updated = Column(DateTime)
    weight = Column(Float)
    allergy_count = Column(Integer)
    photo_count = Column(Integer)
    pet_breed_id = Column(Integer)
    pet_type_id = Column(Integer)
    pet_new = Column(Boolean)
    first_birthday = Column(Date, nullable=True)
    
    # Relationship back to User
    owner = relationship("User", back_populates="pets")
