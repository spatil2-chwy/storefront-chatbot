from typing import Dict, List, Optional
from src.models.product import Size, Product

class ProductService:
    def __init__(self):
        self.products: Dict[int, Product] = {}
        self._initialize_dummy_data()

    def _initialize_dummy_data(self):
        # dummy product entry
        self.products[1] = Product(
            id=1,
            title="Purina Pro Plan Adult Dog Food",
            brand="Purina",
            price=49.99,
            originalPrice=59.99,
            autoshipPrice=44.99,
            rating=4.5,
            reviewCount=1250,
            image="/images/dog-food-1.jpg",
            images=["/images/dog-food-1.jpg", "/images/dog-food-1-2.jpg"],
            deal=True,
            flavors=["Chicken & Rice", "Beef & Rice"],
            sizes=[
                Size(name="30 lb", price=49.99, pricePerLb="$1.67/lb"),
                Size(name="47 lb", price=69.99, pricePerLb="$1.49/lb")
            ],
            description="High-quality adult dog food with real chicken as the first ingredient.",
            inStock=True,
            category="Dog Food",
            keywords=["dog", "food", "adult", "chicken", "protein"]
        )

    async def get_products(self, category: Optional[str] = None, keywords: Optional[List[str]] = None) -> List[Product]:
        products = list(self.products.values())
        if category:
            products = [p for p in products if p.category.lower() == category.lower()]
        if keywords:
            filtered = []
            for p in products:
                text = f"{p.title} {p.brand} {p.description}".lower()
                if any(k.lower() in text for k in keywords):
                    filtered.append(p)
            products = filtered
        return products

    async def get_product(self, product_id: int) -> Optional[Product]:
        return self.products.get(product_id)