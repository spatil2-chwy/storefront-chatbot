from typing import List, Optional
from src.models.product import Product
from src.services.chatbot_logic import chat

class ProductService:
    def __init__(self):
        import chromadb
        self.client = chromadb.PersistentClient(path="../scripts/chroma_db")
        self.collection = self.client.get_collection(name="products")
        self._search_analyzer = None  # Lazy loading for search matches
        print("✅ ProductService initialized successfully")
    
    @property
    def search_analyzer(self):
        """Lazy load the search analyzer only when needed"""
        if self._search_analyzer is None:
            from src.services.search_analyzer import SearchAnalyzer
            print("🔄 Initializing SearchAnalyzer...")
            self._search_analyzer = SearchAnalyzer()
        return self._search_analyzer

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
        if not link or not isinstance(link, str) or not link.strip():
            return "https://via.placeholder.com/400x300?text=Image+Not+Found"
        
        link = link.strip()
        
        # If it's already a valid HTTP URL, return as is
        if link.startswith("http"):
            return link
        
        # Handle Amazon-style URLs (base,timestamp format)
        if "," in link:
            link = link.lstrip("//")
            parts = link.split(",")
            if len(parts) == 2:
                base, timestamp = parts
                formatted = f"https://{base}._AC_SL600_V{timestamp}_.jpg"
                return formatted
        
        # If it starts with //, add https:
        if link.startswith("//"):
            formatted = f"https:{link}"
            return formatted
        
        # If it's a relative path or other format, try to make it absolute
        if not link.startswith("http"):
            formatted = f"https://{link}"
            return formatted
        
        return "https://via.placeholder.com/400x300?text=Image+Not+Found"

    def _metadata_to_product(self, metadata: dict, search_matches: Optional[List] = None) -> Product:
        # Images: use FULLIMAGE (as list) and THUMBNAIL
        images = []
        if metadata.get("FULLIMAGE"):
            # FULLIMAGE can be a single URL or a comma-separated string
            fullimage_val = metadata["FULLIMAGE"]
            
            if isinstance(fullimage_val, list):
                # If it's already a list, it might be malformed (base, timestamp)
                if len(fullimage_val) == 2:
                    # This looks like a base and timestamp that need to be combined
                    base = str(fullimage_val[0]).strip()
                    timestamp = str(fullimage_val[1]).strip()
                    if base and timestamp:
                        # Combine them into a proper URL
                        combined_url = f"{base}._AC_SL600_V{timestamp}_.jpg"
                        formatted_img = self.reformat_image_link(combined_url)
                        if formatted_img and formatted_img != "https://via.placeholder.com/400x300?text=Image+Not+Found":
                            images.append(formatted_img)
                else:
                    # Process each item normally
                    for img in fullimage_val:
                        if img and str(img).strip():
                            formatted_img = self.reformat_image_link(str(img))
                            if formatted_img and formatted_img != "https://via.placeholder.com/400x300?text=Image+Not+Found":
                                images.append(formatted_img)
            else:
                # If it's a string, split by comma and process
                img_list = self.safe_list(fullimage_val)
                if len(img_list) == 2:
                    # This looks like a base and timestamp that need to be combined
                    base = img_list[0].strip()
                    timestamp = img_list[1].strip()
                    if base and timestamp:
                        # Combine them into a proper URL
                        combined_url = f"{base}._AC_SL600_V{timestamp}_.jpg"
                        formatted_img = self.reformat_image_link(combined_url)
                        if formatted_img and formatted_img != "https://via.placeholder.com/400x300?text=Image+Not+Found":
                            images.append(formatted_img)
                else:
                    # Process each item normally
                    for img in img_list:
                        if img and str(img).strip():
                            formatted_img = self.reformat_image_link(str(img))
                            if formatted_img and formatted_img != "https://via.placeholder.com/400x300?text=Image+Not+Found":
                                images.append(formatted_img)
        
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
            search_matches=search_matches,  # Add search matches if provided
        )

    def _ranked_result_to_product(self, ranked_result, query: str = None) -> Product:
        """Convert a ranked result tuple (metadata, document, product_id, distance) to a Product object"""
        metadata, document, product_id, distance = ranked_result
        
        # Analyze search matches if query is provided
        search_matches = None
        if query:
            try:
                # Extract categorized search criteria
                categorized_criteria = self.search_analyzer.extract_search_criteria(query)
                
                # Analyze matches
                search_matches = self.search_analyzer.analyze_product_matches(
                    metadata, categorized_criteria, query
                )
            except Exception as e:
                print(f"⚠️ Error analyzing search matches: {e}")
                search_matches = None
        
        # Use the existing _metadata_to_product method
        return self._metadata_to_product(metadata, search_matches)

    async def search_products(self, query: str, limit: int = 10) -> List[Product]:
        """Search products using LLM agent to parse and filter the query, then semantic search"""
        try:
            # Use the LLM agent to parse the query and get filtered results
            # We pass an empty history since we're not in a chat context
            result = chat(query, [])
            
            # Extract products from the result
            ranked_products = result.get("products", [])
            
            if not ranked_products:
                print(f"No products found for query: '{query}'")
                return []
            
            # Convert ranked results to Product objects with search match analysis
            products = []
            for ranked_result in ranked_products[:limit]:  # Limit the results
                try:
                    product = self._ranked_result_to_product(ranked_result, query)
                    products.append(product)
                except Exception as e:
                    print(f"⚠️ Error converting ranked result to product: {e}")
                    continue
            
            print(f"Found {len(products)} products for query: '{query}' using LLM agent")
            return products
            
        except Exception as e:
            print(f"Error searching products with LLM agent: {e}")
            return []

    async def get_product(self, product_id: int) -> Optional[Product]:
        try:
            results = self.collection.get(where={"PRODUCT_ID": str(product_id)})
            
            if not results["metadatas"] or len(results["metadatas"]) == 0:
                return None
            
            # Get the first (and should be only) metadata
            metadata = results["metadatas"][0]
            
            if metadata is None:
                return None
                
            # Ensure metadata is a proper dictionary
            if isinstance(metadata, dict):
                meta_dict = metadata
            else:
                meta_dict = dict(metadata)
            
            product = self._metadata_to_product(meta_dict)
            return product
        except Exception as e:
            print(f"⚠️ Error fetching product {product_id}: {e}")
            return None


if __name__ == "__main__":
    product_service = ProductService()
    products = product_service.search_products("dry dog food")
    print(products)
