from sqlalchemy import Column, Integer, String, Float, Boolean, JSON
from src.database import Base

class Product(Base):
    __tablename__ = "products"

    id             = Column(Integer, primary_key=True, index=True)
    title          = Column(String, nullable=False)
    brand          = Column(String, nullable=False)
    price          = Column(Float, nullable=False)
    originalPrice  = Column(Float, nullable=True)
    autoshipPrice  = Column(Float, nullable=False)
    rating         = Column(Float, nullable=False)
    reviewCount    = Column(Integer, nullable=False)
    image          = Column(String, nullable=False)
    images         = Column(JSON, nullable=False)
    deal           = Column(Boolean, default=False)
    flavors        = Column(JSON, nullable=False)
    sizes          = Column(JSON, nullable=False)
    description    = Column(String, nullable=False)
    inStock        = Column(Boolean, default=True)
    category       = Column(String, nullable=False)
    keywords       = Column(JSON, nullable=False)