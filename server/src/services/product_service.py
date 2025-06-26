import chromadb
from typing import List, Optional
from src.models.product import Product
from sentence_transformers import SentenceTransformer
import numpy as np

class ProductService:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="../scripts/chroma_db")
        self.collection = self.client.get_collection(name="products")
        # Initialize the same embedding model used in productdbbuilder
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        print("✅ ProductService initialized successfully")

    @staticmethod
    def safe_float(val, default=0.0):
        try:
            return float(val)
        except Exception:
            return default

    @staticmethod
    def safe_int(val, default=0):
        try:
            return int(val)
        except Exception:
            return default

    @staticmethod
    def safe_list(val, sep=",", default=None):
        if not val:
            return default or []
        if isinstance(val, list):
            return val
        return [v.strip() for v in str(val).split(sep) if v.strip()]

    @staticmethod
    def safe_json(val, default=None):
        import json
        try:
            return json.loads(val)
        except Exception:
            return default or []

    @staticmethod
    def safe_str(val, default=""):
        if val is None:
            return default
        return str(val)

    @staticmethod
    def reformat_image_link(link):
        """
        Reformatting image links to be displayable on web
        """
        if isinstance(link, str) and link.strip():
            link = link.lstrip("//")
            parts = link.split(",")
            if len(parts) == 2:
                base, timestamp = parts
                return f"https://{base}._AC_SL600_V{timestamp}_.jpg"
            elif link.startswith("http"):
                return link
        return "https://via.placeholder.com/400x300?text=Image+Not+Found"

    def _metadata_to_product(self, metadata: dict) -> Product:
        # Images: use FULLIMAGE (as list) and THUMBNAIL
        images = []
        if metadata.get("FULLIMAGE"):
            # FULLIMAGE can be a single URL or a comma-separated string
            fullimage_val = metadata["FULLIMAGE"]
            if isinstance(fullimage_val, list):
                images = [self.reformat_image_link(img) for img in fullimage_val]
            else:
                images = [self.reformat_image_link(img) for img in self.safe_list(fullimage_val)]
        
        # Format thumbnail image
        thumbnail = metadata.get("THUMBNAIL", "")
        image = self.reformat_image_link(thumbnail) if thumbnail else (images[0] if images else self.reformat_image_link(""))

        # Keywords: use specialdiettag/ingredienttag keys
        keywords = []
        for k in metadata:
            if k.startswith("specialdiettag:") or k.startswith("ingredienttag:"):
                keywords.append(k.split(":", 1)[1])

        return Product(
            id=self.safe_int(metadata.get("PRODUCT_ID", 0)),
            title=self.safe_str(metadata.get("CLEAN_NAME", "Unnamed Product")),
            brand=self.safe_str(metadata.get("PURCHASE_BRAND", "Unknown Brand")),
            price=round(self.safe_float(metadata.get("PRICE", 0.0)), 1),
            originalPrice=None,  # No separate original price field in database
            autoshipPrice=round(self.safe_float(metadata.get("AUTOSHIP_PRICE", 0.0)), 1),
            rating=self.safe_float(metadata.get("RATING_AVG", 0.0)),
            reviewCount=self.safe_int(metadata.get("RATING_CNT", 0)),
            image=image,
            images=images,
            deal=False,
            description=self.safe_str(metadata.get("DESCRIPTION_LONG", "")),
            inStock=True,
            category=self.safe_str(metadata.get("CATEGORY_LEVEL1", "")),
            keywords=keywords,
        )

    async def search_products(self, query: str, limit: int = 10) -> List[Product]:
        """Search products using semantic search with embeddings and cosine similarity"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=limit,
                include=["distances", "metadatas", "documents"]
            )
            metadatas = results["metadatas"]
            if metadatas is None or len(metadatas) == 0:
                return []
            
            products = []
            # metadatas is a list of lists, where each inner list contains metadata for one result
            # The first (and only) inner list contains all the metadata for the search results
            metadata_list = metadatas[0] if metadatas else []
            
            for meta in metadata_list:
                if meta is not None:
                    try:
                        # Ensure meta is a proper dictionary
                        if isinstance(meta, dict):
                            meta_dict = meta
                        else:
                            meta_dict = dict(meta)
                        products.append(self._metadata_to_product(meta_dict))
                    except Exception as meta_error:
                        print(f"⚠️ Error converting metadata: {meta_error}")
                        continue
            
            print(f"✅ Found {len(products)} products for query: '{query}'")
            return products
        except Exception as e:
            print(f"⚠️ Error searching products: {e}")
            return []

    async def get_product(self, product_id: int) -> Optional[Product]:
        results = self.collection.get(where={"PRODUCT_ID": str(product_id)})
        if not results["metadatas"]:
            return None
        return self._metadata_to_product(dict(results["metadatas"][0]))


if __name__ == "__main__":
    product_service = ProductService()
    products = product_service.search_products("dry dog food")
    print(products)