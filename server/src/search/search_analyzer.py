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

# Download required NLTK data (run once)
try:
    # Splits text into words and punctuation
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    # Provides list of common words to filter out
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    # Provides synonyms, antonyms, and word relationships
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

try:
    # Provides part-of-speech tagging (noun, verb, adjective, etc.)
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')
    
client = chromadb.PersistentClient(path="./../scripts/chroma_db")
collection = client.get_collection(name="products")

class SearchAnalyzer:
    def __init__(self):
        self.metadata_filters = self.build_metadata_filters()
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Initialize Semantic Model
        logger.info("Loading semantic model...")
        self.semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.similarity_threshold = 0.7

        logger.info(f"Search Analyzer initialized with {sum(len(v) for v in self.metadata_filters.values())} discoverable criteria")

    def extract_query_terms(self, query: str) -> List[str]:
            """
            Use NLTK to break down user question and extract search criteria
            """
            
            # Tokenize and clean the query
            tokens = word_tokenize(query.lower())
            
            # Remove stop words and lemmatize
            meaningful_terms = []
            for token in tokens:
                if token.isalnum() and token not in self.stop_words:
                    lemmatized = self.lemmatizer.lemmatize(token)
                    meaningful_terms.append(lemmatized)

           return meaningful_terms
            
    def semantic_similarity(self, query_terms: List[str], product_terms: List[str]) -> List[tuple]:
        """
        Calculate semantic similarity between query terms and product terms
        Returns list of (query_term, product_term, similarity_score)
        """
        
        if not query_terms or not product_terms:
            return []
        
        try: 
            # Get embeddings for query terms
            query_embeddings = self.semantic_model.encode(query_terms)
            
            # Get embeddings for product terms
            product_embeddings = self.semantic_model.encode(product_terms)
            
            # Calculate cosine similarity
            similarities = cosine_similarity(query_embeddings, product_embeddings)
            
            # Find matches above threshold using NumPy operations
            matches_mask = similarities >= self.similarity_threshold
            
            # Create matches list
            matches = []
            for i, j in zip(query_indices, product_indices):
                matches.append((
                    query_terms[i], 
                    product_terms[j], 
                    float(similarities[i, j])
                ))

            return matches
        
        except Exception as e:
            logger.error(f"Error calculating semantic similarity: {e}")
            
        def analyze_product_matches(self, metadata: dict, query: str) -> List[SearchMatch]:
            """
            Semantic matching - if something from user's question is very similar to product metadata, show it
            """
            
            # Extract meaningful terms from user's question
            query_terms = self.extract_query_terms(query)
            
            if not query_terms:
                return []
            
            matches = []
            
            # Get all product metadata values for matching
            product_fields = {
                'brand': metadata.get('PURCHASE_BRAND', ''),
                'category_level_1': metadata.get('CATEGORY_LEVEL1', ''),
                'category_level_2': metadata.get('CATEGORY_LEVEL2', ''),
                'category_level_3': metadata.get('CATEGORY_LEVEL3', ''),
                'ingredients': metadata.get('INGREDIENTS', ''),
                'pet_type': metadata.get('ATTR_PET_TYPE', ''),
                'life_stage': metadata.get('LIFE_STAGE', ''),
                'breed_size': metadata.get('BREED_SIZE', ''),
                'product_type': metadata.get('PRODUCT_TYPE', ''),
                'food_form': metadata.get('ATTR_FOOD_FORM', ''),
                'parent_company': metadata.get('PARENT_COMPANY', ''),
                'merch_classification1': metadata.get('MERCH_CLASSIFICATION1', ''),
                'merch_classification2': metadata.get('MERCH_CLASSIFICATION2', ''),
                'merch_classification3': metadata.get('MERCH_CLASSIFICATION3', ''),
                'merch_classification4': metadata.get('MERCH_CLASSIFICATION4', ''),
            }
            
            # Add diet tags from metadata keys
            diet_tags = []
            for key in metadata:
                if key.startswith('specialdiettag:'):
                    diet_tag = key.split(':', 1)[1]
                    diet_tags.append(diet_tag)
            product_fields['diet_tags'] = ', '.join(diet_tags)
            
            # Match query terms against all product fields
            for field_name, field_value in product_fields.items():
                if not field_value or not field_value.strip():
                    continue
            
            # Calculate semantic similarity between query terms and this field
            semantic_matches = self.semantic_similarity(query_terms, [field_value])
            
            # Create SearchMatch for each semantic match
            for query_term, product_term, similarity in semantic_matches:
                match = SearchMatch(
                    field=field_name,
                    matched_terms=[query_term],
                    confidence=float(similarity),  # Use similarity as confidence
                    field_value=product_term
                )
                matches.append(match)
        
            return matches