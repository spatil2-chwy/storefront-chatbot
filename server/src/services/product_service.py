from typing import List, Optional
from src.models.product import Product
from src.services.chatbot_logic import chat
import time

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

        # Parse review synthesis from JSON
        review_synthesis = self.safe_json(metadata.get("review_synthesis", "{}"), {})
        what_customers_love = ""
        what_to_watch_out_for = ""
        should_you_buy_it = ""
        
        if review_synthesis and isinstance(review_synthesis, dict):
            # Extract what_customers_love (it's stored as a list, so join it)
            customers_love_list = review_synthesis.get("what_customers_love", [])
            if isinstance(customers_love_list, list):
                what_customers_love = " ".join(customers_love_list)
            else:
                what_customers_love = str(customers_love_list)
            
            # Extract what_to_watch_out_for (it's stored as a list, so join it)
            watch_out_list = review_synthesis.get("what_to_watch_out_for", [])
            if isinstance(watch_out_list, list):
                what_to_watch_out_for = " ".join(watch_out_list)
            else:
                what_to_watch_out_for = str(watch_out_list)
            
            # Extract should_you_buy_it (it's stored as a string)
            should_you_buy_it = review_synthesis.get("should_you_buy_it", "")

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
            what_customers_love=what_customers_love,
            what_to_watch_out_for=what_to_watch_out_for,
            should_you_buy_it=should_you_buy_it,
            unanswered_faqs=self.safe_str(metadata.get("unanswered_faqs", "")) or None,
            answered_faqs=self.safe_str(metadata.get("answered_faqs", "")) or None,
        )

    def _ranked_result_to_product(self, ranked_result, query: str = None) -> Product:
        """Convert a ranked result tuple (metadata, document, product_id, distance) to a Product object"""
        metadata, document, product_id, distance = ranked_result
        
        # Analyze search matches if query is provided
        search_matches = None
        if query:
            try:
                analysis_start = time.time()
                # Extract categorized search criteria
                categorized_criteria = self.search_analyzer.extract_search_criteria(query)
                criteria_time = time.time() - analysis_start
                
                # Analyze matches
                match_start = time.time()
                search_matches = self.search_analyzer.analyze_product_matches(
                    metadata, categorized_criteria, query
                )
                match_time = time.time() - match_start
                
                print(f"    🔍 Search match analysis: criteria={criteria_time:.3f}s, matches={match_time:.3f}s")
            except Exception as e:
                print(f"⚠️ Error analyzing search matches: {e}")
                search_matches = None
        
        # Use the existing _metadata_to_product method
        return self._metadata_to_product(metadata, search_matches)

    async def search_products(self, query: str, limit: int = 10) -> dict:
        """Search products using direct semantic search without LLM agent"""
        try:
            total_start = time.time()
            print(f"🔍 Starting direct search for: '{query}'")
            
            # Use direct semantic search instead of going through the chat function
            from src.services.searchengine import query_products, rank_products
            
            search_start = time.time()
            results = query_products(query, (), (), ())  # No filters for direct search
            search_time = time.time() - search_start
            print(f"  🔍 Database search took: {search_time:.3f}s")
            
            ranking_start = time.time()
            ranked_products = rank_products(results)
            ranking_time = time.time() - ranking_start
            print(f"  📊 Ranking took: {ranking_time:.3f}s")
            
            if not ranked_products:
                print(f"❌ No products found for query: '{query}'")
                return {
                    "products": [],
                    "reply": f"No products found for '{query}'"
                }
            
            # Convert ranked results to Product objects with search match analysis
            conversion_start = time.time()
            products = []
            for i, ranked_result in enumerate(ranked_products[:limit]):  # Limit the results
                try:
                    product_start = time.time()
                    product = self._ranked_result_to_product(ranked_result, query)
                    product_time = time.time() - product_start
                    if i < 3:  # Only log first 3 products to avoid spam
                        print(f"    📦 Product {i+1} conversion: {product_time:.3f}s")
                    products.append(product)
                except Exception as e:
                    print(f"⚠️ Error converting ranked result to product: {e}")
                    continue
            
            conversion_time = time.time() - conversion_start
            total_time = time.time() - total_start
            
            print(f"  🔄 Product conversion took: {conversion_time:.3f}s ({len(products)} products)")
            print(f"  ✅ Total search time: {total_time:.3f}s")
            
            return {
                "products": products,
                "reply": f"Found {len(products)} products for '{query}'"
            }
            
        except Exception as e:
            print(f"❌ Error searching products: {e}")
            return {
                "products": [],
                "reply": f"Search failed: {str(e)}"
            }

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
