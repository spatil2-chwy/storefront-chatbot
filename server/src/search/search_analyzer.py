import re
import json
import os
import time
import logging
import chromadb
from typing import List, Dict, Set
from collections import Counter
from src.models.product import SearchMatch
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tag import pos_tag
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Set up logging
logger = logging.getLogger(__name__)

# # UNCOMMENT TO DOWNLOAD NLTK DATA
# # Download required NLTK data (run once)
# try:
#     # Splits text into words and punctuation
#     nltk.data.find('tokenizers/punkt')
# except LookupError:
#     nltk.download('punkt')

# try:
#     # Provides list of common words to filter out
#     nltk.data.find('corpora/stopwords')
# except LookupError:
#     nltk.download('stopwords')

# try:
#     # Provides synonyms, antonyms, and word relationships
#     nltk.data.find('corpora/wordnet')
# except LookupError:
#     nltk.download('wordnet')
# try:
#     # Provides part-of-speech tagging (noun, verb, adjective, etc.)
#     nltk.data.find('taggers/averaged_perceptron_tagger')
# except LookupError:
#     nltk.download('averaged_perceptron_tagger')
    
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
chromadb_path = os.path.join(project_root, "data", "databases", "chroma_db")
client = chromadb.PersistentClient(path=chromadb_path)
collection = client.get_collection(name="review_synthesis")

class SearchAnalyzer:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SearchAnalyzer, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Only initialize once
        if SearchAnalyzer._initialized:
            return
            
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Initialize Semantic Model - this is the expensive operation
        self.semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.similarity_threshold = 0.8

        SearchAnalyzer._initialized = True
    
    def extract_query_terms(self, query: str) -> List[str]:
        """
        Extract meaningful terms from user query and lemmatize them to root words
        """
        
        # Tokenize the query
        tokens = word_tokenize(query.lower())
        
        # Remove stop words and lemmatize
        meaningful_terms = []
        for token in tokens:
            # Remove punctuation and clean
            cleaned_token = re.sub(r'[^\w\s]', '', token)
            if cleaned_token and cleaned_token not in self.stop_words and len(cleaned_token) > 2:
                # Lemmatize to root word
                root_word = self.lemmatizer.lemmatize(cleaned_token)
                meaningful_terms.append(root_word)

        return meaningful_terms
        
    def exact_match_terms(self, query_terms: List[str], product_terms: List[str]) -> List[tuple]:
        """
        Find exact matches between query terms and product terms using root words
        Returns list of (query_term, product_term, confidence_score)
        """
        
        if not query_terms or not product_terms:
            return []
        
        matches = []
        
        # Lemmatize product terms to root words
        product_root_terms = []
        for term in product_terms:
            root_word = self.lemmatizer.lemmatize(term.lower())
            product_root_terms.append(root_word)
        
        # Find exact matches
        for query_term in query_terms:
            for i, product_root_term in enumerate(product_root_terms):
                if query_term == product_root_term:
                    # Exact match gets high confidence
                    matches.append((
                        query_term,
                        product_terms[i],  # Original product term
                        1.0  # Full confidence for exact match
                    ))
        
        return matches
        
    def analyze_product_matches(self, metadata: dict, query: str, pet_profile: dict = None, user_context: dict = None) -> List[SearchMatch]:
        """
        Semantic matching using comprehensive product metadata including pet profile and user query information
        """
        
        start_time = time.time()
        
        # Extract meaningful terms from user's question
        query_terms = self.extract_query_terms(query)
        
        if not query_terms:
            return []
        
        matches = []
        
        # Use comprehensive product metadata fields for matching
        product_fields = {
            # Core product information
            'Product Name': metadata.get('NAME', ''),
            'Clean Name': metadata.get('CLEAN_NAME', ''),
            
            # Categorization
            'Category Level 1': metadata.get('CATEGORY_LEVEL1', ''),
            'Category Level 2': metadata.get('CATEGORY_LEVEL2', ''),
            'Category Level 3': metadata.get('CATEGORY_LEVEL3', ''),
            'Product Type': metadata.get('PRODUCT_TYPE', ''),
            
            # Pet-specific attributes
            'Pet Types': metadata.get('ATTR_PET_TYPE', ''),
            'Pet Types (Alt)': metadata.get('PET_TYPES', ''),
            'Life Stage': metadata.get('LIFE_STAGE', ''),
            'Life Stage (Alt)': metadata.get('LIFESTAGE', ''),
            'Breed Size': metadata.get('BREED_SIZE', ''),
            
            # Food and diet attributes
            'Food Form': metadata.get('ATTR_FOOD_FORM', ''),
            'Special Diet': metadata.get('ATTR_SPECIAL_DIET', ''),
            'Ingredients': metadata.get('INGREDIENTS', ''),
            
            # Merchandising classifications
            'Merch Classification 1': metadata.get('MERCH_CLASSIFICATION1', ''),
            'Merch Classification 2': metadata.get('MERCH_CLASSIFICATION2', ''),
            'Merch Classification 3': metadata.get('MERCH_CLASSIFICATION3', ''),
            'Merch Classification 4': metadata.get('MERCH_CLASSIFICATION4', ''),
            
            # Brand information
            'Brand': metadata.get('PURCHASE_BRAND', ''),
        }
        
        # Add diet tags from metadata keys (relevant for pet allergies and health)
        diet_tags = []
        for key in metadata:
            if key.startswith('specialdiettag:'):
                diet_tag = key.split(':', 1)[1]
                diet_tags.append(diet_tag)
        product_fields['Diet Tags'] = ', '.join(diet_tags)
        
        # Add ingredient tags from metadata keys
        ingredient_tags = []
        for key in metadata:
            if key.startswith('ingredienttag:'):
                ingredient_tag = key.split(':', 1)[1]
                ingredient_tags.append(ingredient_tag)
        product_fields['Ingredient Tags'] = ', '.join(ingredient_tags)
        
        # Add category tags from metadata keys
        category_tags = []
        for key in metadata:
            if key.startswith('categorytag'):
                category_tag = key.split(':', 1)[1]
                category_tags.append(category_tag)
        product_fields['Category Tags'] = ', '.join(category_tags)
        
        # Add review synthesis content for better matching
        review_synthesis = metadata.get("review_synthesis", "{}")
        if review_synthesis and isinstance(review_synthesis, str):
            try:
                import json
                review_data = json.loads(review_synthesis)
                if isinstance(review_data, dict):
                    # What customers love
                    customers_love_list = review_data.get("what_customers_love", [])
                    if customers_love_list:
                        if isinstance(customers_love_list, list):
                            product_fields['What Customers Love'] = ' '.join(customers_love_list)
                        else:
                            product_fields['What Customers Love'] = str(customers_love_list)
                    
                    # What to watch out for
                    watch_out_list = review_data.get("what_to_watch_out_for", [])
                    if watch_out_list:
                        if isinstance(watch_out_list, list):
                            product_fields['What to Watch Out For'] = ' '.join(watch_out_list)
                        else:
                            product_fields['What to Watch Out For'] = str(watch_out_list)
                    
                    # Should you buy it
                    should_you_buy_it = review_data.get("should_you_buy_it", "")
                    if should_you_buy_it:
                        product_fields['Should You Buy It'] = str(should_you_buy_it)
            except (json.JSONDecodeError, TypeError):
                # If review synthesis is not valid JSON, skip it
                pass
        

        
        # If pet profile is provided, enhance the query with pet-specific terms
        enhanced_query_terms = query_terms.copy()
        if pet_profile:
            # Add pet type to search terms
            if pet_profile.get('type'):
                pet_type_terms = self.extract_query_terms(pet_profile['type'])
                enhanced_query_terms.extend(pet_type_terms)
            
            # Add breed to search terms
            if pet_profile.get('breed'):
                breed_terms = self.extract_query_terms(pet_profile['breed'])
                enhanced_query_terms.extend(breed_terms)
            
            # Add life stage to search terms
            if pet_profile.get('life_stage'):
                life_stage_terms = self.extract_query_terms(pet_profile['life_stage'])
                enhanced_query_terms.extend(life_stage_terms)
            
            # Add size/weight to search terms
            if pet_profile.get('size'):
                size_terms = self.extract_query_terms(pet_profile['size'])
                enhanced_query_terms.extend(size_terms)
            
            # Add allergy information to search terms
            if pet_profile.get('allergies'):
                enhanced_query_terms.extend(['allergy', 'hypoallergenic', 'sensitive'])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_query_terms = []
        for term in enhanced_query_terms:
            if term not in seen:
                seen.add(term)
                unique_query_terms.append(term)
        
        # Match query terms against comprehensive product metadata fields
        for field_name, field_value in product_fields.items():
            if not field_value or not field_value.strip():
                continue
            
            # Split field value into individual terms for better matching
            field_terms = []
            if field_value:
                # Split by common separators and clean
                for term in re.split(r'[,;|&]', field_value):
                    term = term.strip().lower()
                    if term:
                        # Further tokenize each term to handle multi-word values
                        # This allows "senior" to match "Adult;Puppy;Senior" 
                        # and "bone" to match "Bone Treats;Chew Toys"
                        sub_terms = re.split(r'[\s\-_]', term)
                        for sub_term in sub_terms:
                            sub_term = sub_term.strip()
                            if sub_term and len(sub_term) > 2:  # Skip very short terms
                                # Lemmatize to root word for consistent matching
                                root_word = self.lemmatizer.lemmatize(sub_term)
                                field_terms.append(root_word)
                        
                        # Also keep the original term for exact matches
                        original_root = self.lemmatizer.lemmatize(term)
                        if original_root not in field_terms:
                            field_terms.append(original_root)
            
            if not field_terms:
                continue
            
            # Calculate semantic similarity between query terms and field terms
            semantic_matches = self.exact_match_terms(unique_query_terms, field_terms)
            
            # Create SearchMatch for each semantic match
            for query_term, product_term, confidence in semantic_matches:
                match = SearchMatch(
                    field=f"{field_name}: {product_term}",
                    matched_terms=[query_term],
                    confidence=float(confidence),  # Use similarity as confidence
                    field_value=product_term
                )
                matches.append(match)
        
        analysis_time = time.time() - start_time
        logger.debug(f"🔍 SearchAnalyzer analyzed {len(matches)} comprehensive matches in {analysis_time:.3f}s")
        
        return matches