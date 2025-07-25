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

def capitalize_field_value(value: str) -> str:
    """Capitalize the first letter of each word in a field value"""
    if not value:
        return value
    
    return ' '.join(word.capitalize() for word in value.split())

# Set up logging
logger = logging.getLogger(__name__)

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
        self.similarity_threshold = 1

        # Define fields that should preserve multi-word entities
        self.preserve_multiword_fields = {
            'Product Name', 'Clean Name', 'Brand', 'Special Diet',
            'What Customers Love', 'What to Watch Out For', 'Should You Buy It'
        }

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
    
    def extract_field_terms(self, field_value: str, field_name: str) -> List[str]:
        """
        Extract terms from field value, preserving multi-word entities for certain fields
        """
        if not field_value or not field_value.strip():
            return []
        
        field_terms = []
        
        # For fields that should preserve multi-word entities (especially Brand)
        if field_name in self.preserve_multiword_fields:
            # Split by common separators but preserve the whole phrases
            phrases = re.split(r'[,;|&]', field_value)
            complete_phrases_added = []
            
            for phrase in phrases:
                phrase = phrase.strip()
                if phrase and len(phrase) > 2:
                    phrase_lower = phrase.lower()
                    field_terms.append(phrase_lower)
                    complete_phrases_added.append(phrase_lower)
            
            # For Brand field, only add individual words if they're not part of a complete phrase
            # This prevents "purina" "pro" "plan" when "purina pro plan" exists
            if field_name == 'Brand':
                # Don't add individual words for brands - keep only complete brand names
                pass
            else:
                # For other preserve_multiword_fields, add individual words for partial matching
                tokens = word_tokenize(field_value.lower())
                for token in tokens:
                    cleaned_token = re.sub(r'[^\w\s]', '', token)
                    if (cleaned_token and cleaned_token not in self.stop_words and 
                        len(cleaned_token) > 2):
                        root_word = self.lemmatizer.lemmatize(cleaned_token)
                        # Only add if it's not already covered by a complete phrase
                        if not any(root_word in phrase for phrase in complete_phrases_added):
                            if root_word not in field_terms:
                                field_terms.append(root_word)
        
        else:
            # For other fields, use the original word-level splitting
            for term in re.split(r'[,;|&]', field_value):
                term = term.strip().lower()
                if term:
                    # Further tokenize each term to handle multi-word values
                    sub_terms = re.split(r'[\s\-_]', term)
                    for sub_term in sub_terms:
                        sub_term = sub_term.strip()
                        if sub_term and len(sub_term) > 2:
                            # Lemmatize to root word for consistent matching
                            root_word = self.lemmatizer.lemmatize(sub_term)
                            field_terms.append(root_word)
                    
                    # Also keep the original term for exact matches
                    original_root = self.lemmatizer.lemmatize(term)
                    if original_root not in field_terms:
                        field_terms.append(original_root)
        
        return field_terms    

    def phrase_match_terms(self, query_terms: List[str], product_terms: List[str]) -> List[tuple]:
        """
        Find matches between query terms and product terms, handling both phrases and individual words
        Returns list of (query_match, product_term, confidence_score)
        """
        
        if not query_terms or not product_terms:
            return []
        
        matches = []
        query_text = ' '.join(query_terms)
        
        # Check for phrase matches first (higher confidence)
        for product_term in product_terms:
            product_term_lower = product_term.lower()
            
            # Check if the entire product term appears in the query
            if len(product_term.split()) > 1:  # Multi-word term
                # Lemmatize the product term for comparison
                product_tokens = word_tokenize(product_term_lower)
                product_roots = []
                for token in product_tokens:
                    cleaned_token = re.sub(r'[^\w\s]', '', token)
                    if cleaned_token and len(cleaned_token) > 2:
                        root_word = self.lemmatizer.lemmatize(cleaned_token)
                        product_roots.append(root_word)
                
                # Check how many query terms match product term roots
                matching_count = sum(1 for root in product_roots if root in query_terms)
                if matching_count > 0:
                    confidence = matching_count / len(product_roots)
                    if confidence >= 0.5:  # At least half of the brand words match
                        matches.append((
                            ' '.join([term for term in query_terms if term in product_roots]),
                            product_term,  # Keep original formatting
                            min(confidence * 1.2, 1.0)  # Boost confidence for phrase matches
                        ))
                        continue
            
            # Individual word matching (lower confidence)
            product_root = self.lemmatizer.lemmatize(product_term_lower)
            for query_term in query_terms:
                if query_term == product_root:
                    matches.append((
                        query_term,
                        product_term,  # Keep original formatting
                        1.0 if len(product_term.split()) == 1 else 0.8  # Lower confidence for single word matches from multi-word terms
                    ))
        
        return matches
        
    def analyze_product_matches(self, metadata: dict, query: str, pet_profile: dict = None, user_context: dict = None, excluded_ingredients: list = None) -> List[SearchMatch]:
        """
        Semantic matching using comprehensive product metadata including pet profile and user query information
        """
        
        start_time = time.time()
        
        # Debug: Log the excluded ingredients
        logger.debug(f"🔍 SearchAnalyzer received excluded_ingredients: {excluded_ingredients}")
        
        # Extract meaningful terms from user's question
        query_terms = self.extract_query_terms(query)
        
        if not query_terms:
            return []
        
        matches = []
        
        # Store original query terms for category tag matching
        original_query_terms = query_terms.copy()
        
        # Dynamically select relevant fields based on query terms
        product_fields = self._get_relevant_fields_dynamic(metadata, query_terms, original_query_terms=original_query_terms, excluded_ingredients=excluded_ingredients)
        
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
            if pet_profile.get('allergies') and pet_profile.get('allergies').strip():
                # Split allergies by comma and add each allergy to search terms
                allergies = [allergy.strip() for allergy in pet_profile.get('allergies').split(',')]
                enhanced_query_terms.extend(allergies)
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
            
            # Special handling for excluded ingredients - always include them if they exist
            if field_name == 'Excluded Ingredients' and excluded_ingredients:
                # Create a match for each excluded ingredient
                for excluded_ingredient in excluded_ingredients:
                    capitalized_ingredient = capitalize_field_value(excluded_ingredient)
                    match = SearchMatch(
                        field=f"{field_name}: {capitalized_ingredient}",
                        matched_terms=[excluded_ingredient],
                        confidence=1.0,
                        field_value=capitalized_ingredient
                    )
                    matches.append(match)
                continue
            
            # Extract terms from field value, preserving multi-word entities for certain fields
            field_terms = self.extract_field_terms(field_value, field_name)
            
            if not field_terms:
                continue
            
            # Calculate matches between query terms and field terms
            phrase_matches = self.phrase_match_terms(unique_query_terms, field_terms)
            
            # Create SearchMatch for each match, but only keep high-confidence matches
            for query_match, product_term, confidence in phrase_matches:
                # Only include matches with confidence >= 0.8
                if confidence == 1:
                    # Capitalize the product term for better display
                    capitalized_product_term = capitalize_field_value(product_term)
                    match = SearchMatch(
                        field=f"{field_name}: {capitalized_product_term}",
                        matched_terms=[query_match] if isinstance(query_match, str) else query_match.split(),
                        confidence=float(confidence),
                        field_value=capitalized_product_term
                    )
                    matches.append(match)
        
        analysis_time = time.time() - start_time
        logger.debug(f"🔍 SearchAnalyzer analyzed {len(matches)} comprehensive matches in {analysis_time:.3f}s")
        
        return matches
    
    def _get_relevant_fields_dynamic(self, metadata, query_terms, original_query_terms=None, excluded_ingredients=None):
        """Dynamically select relevant fields based on query terms"""
        
        # Use original query terms for category tag matching if provided, otherwise use regular query terms
        category_matching_terms = original_query_terms if original_query_terms is not None else query_terms
        
        relevant_fields = {
            'Clean Name': metadata.get('CLEAN_NAME', ''),
            'Category Level 1': metadata.get('CATEGORY_LEVEL1', ''),
            'Category Level 2': metadata.get('CATEGORY_LEVEL2', ''),
            'Category Level 3': metadata.get('CATEGORY_LEVEL3', ''),
            'Product Type': metadata.get('PRODUCT_TYPE', ''),
        }
        
        # Add pet-specific fields (always relevant for pet queries)
        pet_fields = {
            'Pet Types': metadata.get('ATTR_PET_TYPE', ''),
            'Pet Types (Alt)': metadata.get('PET_TYPES', ''),
            'Life Stage': metadata.get('LIFE_STAGE', ''),
            'Life Stage (Alt)': metadata.get('LIFESTAGE', ''),
            'Breed Size': metadata.get('BREED_SIZE', ''),
        }
        relevant_fields.update(pet_fields)
        
        # Only add other fields if they contain query terms
        all_metadata_fields = {
            'Food Form': metadata.get('ATTR_FOOD_FORM', ''),
            'Special Diet': metadata.get('ATTR_SPECIAL_DIET', ''),
            'Ingredients': metadata.get('INGREDIENTS', ''),
            'Brand': metadata.get('PURCHASE_BRAND', ''),
        }
        
        # Check each field for query term presence
        for field_name, field_value in all_metadata_fields.items():
            if not field_value:
                continue
                
            field_lower = field_value.lower()
            
            # Only include fields that contain query terms
            if any(term in field_lower for term in query_terms):
                relevant_fields[field_name] = field_value
        
        # Add diet tags only if they contain query terms
        diet_tags = []
        for key in metadata:
            if key.startswith('specialdiettag:'):
                diet_tag = key.split(':', 1)[1]
                if any(term in diet_tag.lower() for term in query_terms):
                    diet_tags.append(capitalize_field_value(diet_tag))
        
        if diet_tags:
            relevant_fields['Diet Tags'] = ', '.join(diet_tags)
        
        # Add ingredient tags only if they contain query terms
        ingredient_tags = []
        for key in metadata:
            if key.startswith('ingredienttag:'):
                ingredient_tag = key.split(':', 1)[1]
                if any(term in ingredient_tag.lower() for term in query_terms):
                    ingredient_tags.append(capitalize_field_value(ingredient_tag))
        
        if ingredient_tags:
            relevant_fields['Ingredient Tags'] = ', '.join(ingredient_tags)
        
        # Add excluded ingredients as a special field for matching
        if excluded_ingredients:
            relevant_fields['Excluded Ingredients'] = ', '.join(excluded_ingredients)
        
        # Add category tags only if they contain ORIGINAL query terms (not enhanced)
        category_tags = []
        for key in metadata:
            if key.startswith('categorytag'):
                category_tag = key.split(':', 1)[1]
                if any(term in category_tag.lower() for term in category_matching_terms):
                    category_tags.append(capitalize_field_value(category_tag))
        
        if category_tags:
            relevant_fields['Category Tags'] = ', '.join(category_tags)
        
        return relevant_fields