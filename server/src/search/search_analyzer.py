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
            'Product Name', 'Clean Name', 'Brand', 'Special Diet', 'Diet Tags',
            'What Customers Love', 'What to Watch Out For', 'Should You Buy It'
        }

        SearchAnalyzer._initialized = True
    
    def extract_query_terms(self, query: str) -> List[str]:
        """
        Extract meaningful terms from user query and lemmatize them to root words
        """
        
        # First, look for compound terms (words with hyphens or common compound phrases)
        compound_terms = []
        
        # Common compound terms in pet food context
        common_compounds = [
            'grain-free', 'grain free', 'salmon-free', 'salmon free', 'chicken-free', 'chicken free',
            'beef-free', 'beef free', 'dairy-free', 'dairy free', 'soy-free', 'soy free',
            'corn-free', 'corn free', 'wheat-free', 'wheat free', 'limited ingredient',
            'single protein', 'multi-protein', 'multi protein', 'raw food', 'raw-food',
            'wet food', 'wet-food', 'dry food', 'dry-food', 'puppy food', 'puppy-food',
            'senior food', 'senior-food', 'adult food', 'adult-food'
        ]
        
        query_lower = query.lower()
        for compound in common_compounds:
            if compound in query_lower:
                compound_terms.append(compound)
        
        # Tokenize the query
        tokens = word_tokenize(query.lower())
        
        # Remove stop words and lemmatize
        meaningful_terms = []
        
        # Add compound terms first
        meaningful_terms.extend(compound_terms)
        
        for token in tokens:
            # Remove punctuation and clean
            cleaned_token = re.sub(r'[^\w\s]', '', token)
            if cleaned_token and cleaned_token not in self.stop_words and len(cleaned_token) > 2:
                # Lemmatize to root word
                root_word = self.lemmatizer.lemmatize(cleaned_token)
                # Only add if not already covered by a compound term
                if not any(root_word in compound for compound in compound_terms):
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
            # For other fields, preserve compound terms while still allowing individual word matching
            for term in re.split(r'[,;|&]', field_value):
                term = term.strip().lower()
                if term:
                    # First, add the complete term for exact phrase matching
                    field_terms.append(term)
                    
                    # Then, split by spaces only (not hyphens) to preserve compound terms like "grain-free"
                    space_split_terms = re.split(r'\s+', term)
                    for space_term in space_split_terms:
                        space_term = space_term.strip()
                        if space_term and len(space_term) > 2:
                            # For compound terms like "grain-free", keep them as-is
                            if '-' in space_term or '_' in space_term:
                                field_terms.append(space_term)
                            else:
                                # For single words, lemmatize for consistent matching
                                root_word = self.lemmatizer.lemmatize(space_term)
                                if root_word not in field_terms:
                                    field_terms.append(root_word)
        
        return field_terms    

    def phrase_match_terms(self, query_terms: List[str], product_terms: List[str]) -> List[tuple]:
        """
        Find matches between query terms and product terms, handling both phrases and individual words
        Returns list of (query_match, product_term, confidence_score)
        """
        
        if not query_terms or not product_terms:
            return []
        
        matches = []
        
        # Check for exact phrase matches first (highest confidence)
        for product_term in product_terms:
            product_term_lower = product_term.lower()
            
            # Normalize product term (replace hyphens with spaces for comparison)
            normalized_product = product_term_lower.replace('-', ' ')
            
            for query_term in query_terms:
                # Normalize query term (replace hyphens with spaces for comparison)
                normalized_query = query_term.replace('-', ' ')
                
                # Check for exact match (after normalization)
                if normalized_query == normalized_product:
                    matches.append((
                        query_term,
                        product_term,  # Keep original formatting
                        1.0  # Highest confidence for exact matches
                    ))
                    continue
                
                # Check if query term contains product term or vice versa
                if normalized_query in normalized_product or normalized_product in normalized_query:
                    # Calculate confidence based on overlap
                    if len(normalized_query) >= len(normalized_product):
                        confidence = len(normalized_product) / len(normalized_query)
                    else:
                        confidence = len(normalized_query) / len(normalized_product)
                    
                    if confidence >= 0.7:  # At least 70% overlap
                        matches.append((
                            query_term,
                            product_term,  # Keep original formatting
                            confidence
                        ))
                        continue
        
        # Check for individual word matches (lower confidence)
        for product_term in product_terms:
            product_term_lower = product_term.lower()
            
            # Split product term into individual words
            product_words = re.split(r'[\s\-_]', product_term_lower)
            
            for query_term in query_terms:
                # Split query term into individual words
                query_words = re.split(r'[\s\-_]', query_term)
                
                # Check for word-level matches
                for query_word in query_words:
                    if query_word and len(query_word) > 2:
                        query_root = self.lemmatizer.lemmatize(query_word)
                        
                        for product_word in product_words:
                            if product_word and len(product_word) > 2:
                                product_root = self.lemmatizer.lemmatize(product_word)
                                
                                if query_root == product_root:
                                    matches.append((
                                        query_word,
                                        product_term,  # Keep original formatting
                                        0.8  # Lower confidence for word-level matches
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
            
            # Use original query terms for most field matching to avoid irrelevant matches
            # Only use enhanced terms for pet-specific fields
            pet_specific_fields = {'Pet Types', 'Pet Types (Alt)', 'Life Stage', 'Life Stage (Alt)', 'Breed Size'}
            matching_terms = unique_query_terms if field_name in pet_specific_fields else original_query_terms
            
            # Calculate matches between query terms and field terms
            phrase_matches = self.phrase_match_terms(matching_terms, field_terms)
            
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