from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from src.database import Base

class PetProfile(Base):
    __tablename__ = "pet_profiles"

    pet_profile_id      = Column(Integer, primary_key=True, index=True)
    customer_id         = Column(Integer, ForeignKey("customers_full.customer_id"), nullable=False)
    pet_name            = Column(String, nullable=True)
    pet_type            = Column(String, nullable=True)
    pet_breed           = Column(String, nullable=True)
    pet_breed_size_type = Column(String, nullable=True)
    gender              = Column(String, nullable=True)
    weight_type         = Column(String, nullable=True)
    size_type           = Column(String, nullable=True)
    birthday            = Column(Date, nullable=True)
    life_stage          = Column(String, nullable=True)
    adopted             = Column(Boolean, default=False)
    adoption_date       = Column(Date, nullable=True)
    status              = Column(String, nullable=False)
    status_reason       = Column(String, nullable=True)
    time_created        = Column(DateTime, nullable=False)
    time_updated        = Column(DateTime, nullable=True)
    weight              = Column(Integer, nullable=True)
    allergy_count       = Column(Integer, nullable=True)
    photo_count         = Column(Integer, nullable=True)
    pet_breed_id        = Column(Integer, nullable=True)
    pet_type_id         = Column(Integer, nullable=True)
    pet_new             = Column(Boolean, default=False)
    first_birthday      = Column(Date, nullable=True)

    # Relationship back to user
    owner = relationship("User", back_populates="pets")