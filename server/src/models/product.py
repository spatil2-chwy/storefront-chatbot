from pydantic import BaseModel
from typing import List, Optional

class Size(BaseModel):
    name: str
    price: float
    pricePerLb: str
    
class Product(BaseModel):
    id: int
    title: str
    brand: str
    price: float
    originalPrice: Optional[float] = None
    autoshipPrice: float
    rating: float
    reviewCount: int
    image: str
    images: List[str]
    deal: bool
    flavors: List[str]
    sizes: List[Size]
    description: str
    inStock: bool
    category: str
    keywords: List[str]
