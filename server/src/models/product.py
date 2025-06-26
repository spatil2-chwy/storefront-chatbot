from sqlalchemy import Column, Integer, String, Float, Boolean, JSON
from src.database import Base

<<<<<<< feature/authentication
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
=======
class Size(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    pricePerLb: Optional[str] = None
    
class Product(BaseModel):
    id: Optional[int] = None  # PRODUCT_ID
    title: Optional[str] = None  # CLEAN_NAME
    brand: Optional[str] = None  # PURCHASE_BRAND
    price: Optional[float] = None  # PRICE
    originalPrice: Optional[float] = None  # PRICE (for strikethrough/original price)
    autoshipPrice: Optional[float] = None  # AUTOSHIP_PRICE
    rating: Optional[float] = None  # RATING_AVG
    reviewCount: Optional[int] = None  # RATING_CNT
    image: Optional[str] = None  # THUMBNAIL
    images: Optional[List[str]] = None  # FULLIMAGE (array for gallery)
    deal: Optional[bool] = None  # Not available, can be False
    description: Optional[str] = None  # DESCRIPTION_LONG
    inStock: Optional[bool] = None  # Not available, can be True
    category: Optional[str] = None  # CATEGORY_LEVEL1
    keywords: Optional[List[str]] = None  # specialdiettag/ingredienttag
>>>>>>> dev
