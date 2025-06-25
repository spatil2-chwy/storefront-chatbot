from typing import List, Optional
from sqlalchemy.orm import Session
from src.models.product import Product

class ProductService:
    def list_products(
        self,
        db: Session,
        category: Optional[str] = None,
        keywords: Optional[List[str]] = None,
    ) -> List[Product]:
        query = db.query(Product)
        if category:
            query = query.filter(Product.category == category)
        if keywords:
            query = query.filter(Product.keywords.contains(keywords))
        return query.all()

    def get_product(self, db: Session, product_id: int) -> Product | None:
        return (
            db.query(Product)
              .filter(Product.id == product_id)
              .one_or_none()
        )

    def create_product(self, db: Session, prod_data: Product) -> Product:
        db.add(prod_data)
        db.commit()
        db.refresh(prod_data)
        return prod_data