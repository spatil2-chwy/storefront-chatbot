import re
import json
import os
import time
import logging
from typing import List, Dict, Set
from collections import Counter
from src.models.product import SearchMatch

logger = logging.getLogger(__name__)

import chromadb
client = chromadb.PersistentClient(path="../scripts/chroma_db")
collection = client.get_collection(name="review_synthesis")

class SearchAnalyzer:
    def __init__(self):
        self.metadata_filters = self._build_metadata_filters()
        logger.info(f"Search Analyzer initialized with {sum(len(v) for v in self.metadata_filters.values())} discoverable criteria")
    
    def _build_metadata_filters(self) -> Dict[str, Dict[str, Set[str]]]:
        """Build search filters from actual product metadata"""
        cache_file = "data/chromadb/metadata_filters_cache.json"
        
        # Try to load from cache first
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                    # Convert lists back to sets for faster lookups
                    return {
                        category: {key: set(values) for key, values in filters.items()}
                        for category, filters in cached_data.items()
                    }
            except:
                pass
        
        # Discover from database
        filters = self._discover_from_database()
        
        # Cache the results
        try:
            # Convert sets to lists for JSON serialization
            cache_data = {
                category: {key: list(values) for key, values in filters.items()}
                for category, filters in filters.items()
            }
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except:
            pass
        
        return filters
    
    def _discover_from_database(self) -> Dict[str, Dict[str, Set[str]]]:
        """Discover all searchable criteria from product metadata"""
        try:
            # import chromadb
            # client = chromadb.PersistentClient(path="../scripts/chroma_db")
            # collection = client.get_collection(name="products")
            
            # Sample products for analysis
            results = collection.get(limit=10000)
            print(f"Analyzing {len(results['metadatas'])} products for metadata filters...")
            
            filters = {
                'brands': {},
                'categories': {},
                'ingredients': {},
                'diet_tags': {},
                'pet_attributes': {},
                'price_ranges': {},
                'ratings': {}
            }
            
            # Collect all unique values from metadata
            all_brands = []
            all_categories = []
            all_ingredients = []
            all_diet_tags = []
            all_pet_types = []
            all_food_forms = []
            prices = []
            ratings = []
            
            for metadata in results['metadatas']:
                if not metadata:
                    continue
                
                # Extract brands - handle multi-value fields separated by ||
                brand_field = metadata.get('PURCHASE_BRAND', '').strip()
                if brand_field:
                    # Split on || and clean each brand
                    brand_parts = [part.strip() for part in brand_field.split('||')]
                    for brand in brand_parts:
                        if brand and len(brand) > 1:
                            all_brands.append(brand)
                
                # Extract categories from all levels
                for level in ['CATEGORY_LEVEL1', 'CATEGORY_LEVEL2', 'CATEGORY_LEVEL3']:
                    category = metadata.get(level, '').strip()
                    if category:
                        all_categories.append(category)
                
                # Extract pet attributes
                pet_type = metadata.get('ATTR_PET_TYPE', '').strip()
                if pet_type:
                    all_pet_types.append(pet_type)
                
                food_form = metadata.get('ATTR_FOOD_FORM', '').strip()
                if food_form:
                    all_food_forms.append(food_form)
                
                # Extract tags from metadata keys
                for key in metadata:
                    if key.startswith('ingredienttag:'):
                        ingredient = key.split(':', 1)[1].strip()
                        if ingredient:
                            all_ingredients.append(ingredient)
                    elif key.startswith('specialdiettag:'):
                        diet_tag = key.split(':', 1)[1].strip()
                        if diet_tag:
                            all_diet_tags.append(diet_tag)
                
                # Collect numeric data
                price = metadata.get('PRICE', 0)
                if price and price > 0:
                    prices.append(float(price))
                
                rating = metadata.get('RATING_AVG', 0)
                if rating and rating > 0:
                    ratings.append(float(rating))
            
            # Build brand filters (keep most common brands)
            brand_counts = Counter(all_brands)
            filters['brands']['all'] = set([brand for brand, count in brand_counts.most_common(200)])
            
            # Build category filters
            category_counts = Counter(all_categories)
            filters['categories']['all'] = set([cat for cat, count in category_counts.most_common(100)])
            
            # Build ingredient filters (keep most common ingredients)
            ingredient_counts = Counter(all_ingredients)
            filters['ingredients']['all'] = set([ing for ing, count in ingredient_counts.most_common(300)])
            
            # Build diet tag filters
            diet_counts = Counter(all_diet_tags)
            filters['diet_tags']['all'] = set([diet for diet, count in diet_counts.most_common(50)])
            
            # Build pet attribute filters
            pet_type_counts = Counter(all_pet_types)
            filters['pet_attributes']['types'] = set([pet for pet, count in pet_type_counts.most_common(20)])
            
            food_form_counts = Counter(all_food_forms)
            filters['pet_attributes']['food_forms'] = set([form for form, count in food_form_counts.most_common(20)])
            
            # Build price range filters
            if prices:
                prices.sort()
                filters['price_ranges']['low'] = set([f"Under ${int(p)}" for p in [10, 25, 50]])
                filters['price_ranges']['high'] = set([f"Over ${int(p)}" for p in [50, 100, 200]])
            
            # Build rating filters
            if ratings:
                filters['ratings']['all'] = set(["4+ Stars", "3+ Stars", "5 Stars"])
            
            print(f"Discovered metadata filters:")
            print(f"  • {len(filters['brands']['all'])} brands")
            print(f"  • {len(filters['categories']['all'])} categories")
            print(f"  • {len(filters['ingredients']['all'])} ingredients")
            print(f"  • {len(filters['diet_tags']['all'])} diet tags")
            print(f"  • {len(filters['pet_attributes']['types'])} pet types")
            
            return filters
            
        except Exception as e:
            print(f"⚠️ Error discovering metadata filters: {e}")
            return self._get_fallback_filters()
    
    def _get_fallback_filters(self) -> Dict[str, Dict[str, Set[str]]]:
        """Fallback filters if database discovery fails"""
        return {
            'brands': {'all': set(['Purina', 'Hill\'s', 'Royal Canin', 'Blue Buffalo'])},
            'categories': {'all': set(['Dog Food', 'Cat Food', 'Treats', 'Toys'])},
            'ingredients': {'all': set(['Chicken', 'Beef', 'Salmon', 'Rice'])},
            'diet_tags': {'all': set(['Grain-Free', 'Limited Ingredient', 'Organic'])},
            'pet_attributes': {'types': set(['Dog', 'Cat', 'Bird'])}
        }
    
    def extract_search_criteria(self, query: str) -> Dict[str, List[str]]:
        """Extract search criteria by matching query against discovered metadata"""
        start_time = time.time()
        
        query_lower = query.lower().strip()
        query_words = set(query_lower.split())
        
        print(f"🔍 Analyzing query: '{query}' -> words: {query_words}")
        
        found_criteria = {
            'Brands': [],
            'Categories': [],
            'Ingredients': [],
            'Diet & Health': [],
            'Pet Types': [],
            'Product Forms': []
        }
        
        # Match against discovered brands
        for brand in self.metadata_filters['brands']['all']:
            if self._matches_query(brand, query_lower, query_words):
                found_criteria['Brands'].append(brand)
        
        # Match against discovered categories
        for category in self.metadata_filters['categories']['all']:
            if self._matches_query(category, query_lower, query_words):
                found_criteria['Categories'].append(category)
        
        # Match against discovered ingredients
        for ingredient in self.metadata_filters['ingredients']['all']:
            if self._matches_query(ingredient, query_lower, query_words):
                found_criteria['Ingredients'].append(ingredient)
        
        # Match against discovered diet tags
        for diet_tag in self.metadata_filters['diet_tags']['all']:
            if self._matches_query(diet_tag, query_lower, query_words):
                found_criteria['Diet & Health'].append(diet_tag)
        
        # Match against discovered pet types
        for pet_type in self.metadata_filters['pet_attributes']['types']:
            if self._matches_query(pet_type, query_lower, query_words):
                found_criteria['Pet Types'].append(pet_type)
        
        # Match against discovered food forms
        for food_form in self.metadata_filters['pet_attributes'].get('food_forms', []):
            if self._matches_query(food_form, query_lower, query_words):
                found_criteria['Product Forms'].append(food_form)
        
        # Add universal patterns for life stages and sizes
        self._add_universal_patterns(query_lower, query_words, found_criteria)
        
        # Remove empty categories
        result = {k: v for k, v in found_criteria.items() if v}
        
        extraction_time = time.time() - start_time
        print(f"📋 Found criteria: {result}")
        # print(f"      📋 Criteria extraction took: {extraction_time:.3f}s (found {len(result)} categories)")
        
        return result


    def _matches_query(self, term: str, query_lower: str, query_words: Set[str]) -> bool:
        """Check if a metadata term matches the user's query"""
        term_lower = term.lower()
        
        # Normalize both term and query for better matching (handle hyphens/spaces)
        def normalize_text(text):
            return text.replace('-', ' ').replace('_', ' ')
        
        normalized_term = normalize_text(term_lower)
        normalized_query = normalize_text(query_lower)
        
        # Direct substring match on normalized text
        if normalized_term in normalized_query:
            return True
        
        # Word-based matching for multi-word terms
        term_words = set(normalized_term.split())
        query_words_normalized = set(normalized_query.split())
        
        # For single words, require exact word match
        if len(term_words) == 1:
            return list(term_words)[0] in query_words_normalized
        
        # For multi-word terms, require all words to be present
        return term_words.issubset(query_words_normalized)
    
    def _add_universal_patterns(self, query_lower: str, query_words: Set[str], criteria: Dict[str, List[str]]):
        """Add universal patterns that don't depend on metadata discovery"""
        
        # Life stages (universal across all pet products)
        life_stages = {
            'Puppy': ['puppy', 'pup'],
            'Kitten': ['kitten'],
            'Adult': ['adult'],
            'Senior': ['senior', 'elderly', 'aged']
        }
        
        for stage, patterns in life_stages.items():
            if any(pattern in query_words for pattern in patterns):
                if 'Life Stages' not in criteria:
                    criteria['Life Stages'] = []
                criteria['Life Stages'].append(stage)
        
        # Size/weight parsing
        weight_match = re.search(r'(\d+)\s*(?:lb|lbs|pound|pounds)', query_lower)
        if weight_match:
            weight = int(weight_match.group(1))
            size_category = self._weight_to_size(weight)
            if 'Size/Weight' not in criteria:
                criteria['Size/Weight'] = []
            criteria['Size/Weight'].append(size_category)
    
    def _weight_to_size(self, weight: int) -> str:
        """Convert weight to size category"""
        if weight <= 5:
            return 'Toy/Extra Small (< 5 lbs)'
        elif weight <= 25:
            return 'Small (5-25 lbs)'
        elif weight <= 60:
            return 'Medium (25-60 lbs)'
        elif weight <= 100:
            return 'Large (60-100 lbs)'
        else:
            return 'Giant (100+ lbs)'
    
    def analyze_product_matches(self, product_metadata: dict, categorized_criteria: Dict[str, List[str]], query: str) -> List[SearchMatch]:
        """Analyze which criteria matched this product using metadata"""
        if not categorized_criteria:
            return []
        
        start_time = time.time()
        matches = []
        
        for category, criteria_list in categorized_criteria.items():
            for criterion in criteria_list:
                match_result = self._criterion_matches_product_metadata(criterion, product_metadata, category)
                if match_result.get('matched', False):
                    # Calculate confidence based on match quality
                    confidence = self._calculate_match_confidence(criterion, product_metadata, category, match_result)
                    matches.append(SearchMatch(
                        field=f"{category}: {criterion}",
                        matched_terms=[criterion],
                        confidence=confidence,
                        field_value=self._get_matched_metadata_value(criterion, product_metadata, category)
                    ))
        
        analysis_time = time.time() - start_time
        if analysis_time > 0.01:  # Only log if it takes more than 10ms
            print(f"      🎯 Product match analysis took: {analysis_time:.3f}s (found {len(matches)} matches)")
        
        return matches
    
    def _criterion_matches_product_metadata(self, criterion: str, metadata: dict, category: str) -> dict:
        """Check if criterion matches product using metadata fields and return match details"""
        criterion_lower = criterion.lower()
        
        # Brand matching - handle multi-value fields
        if category == 'Brands':
            brand_field = str(metadata.get('PURCHASE_BRAND', ''))
            brand_parts = [part.strip().lower() for part in brand_field.split('||')]
            for brand in brand_parts:
                if criterion_lower in brand:
                    exact_match = criterion_lower == brand
                    return {
                        'matched': True,
                        'exact_match': exact_match,
                        'matched_value': brand,
                        'field_type': 'brand'
                    }
            return {'matched': False}
        
        # Category matching
        elif category == 'Categories':
            categories = [
                ('CATEGORY_LEVEL1', str(metadata.get('CATEGORY_LEVEL1', '')).lower()),
                ('CATEGORY_LEVEL2', str(metadata.get('CATEGORY_LEVEL2', '')).lower()),
                ('CATEGORY_LEVEL3', str(metadata.get('CATEGORY_LEVEL3', '')).lower())
            ]
            for field_name, cat in categories:
                if criterion_lower in cat and cat:
                    exact_match = criterion_lower == cat
                    return {
                        'matched': True,
                        'exact_match': exact_match,
                        'matched_value': cat,
                        'field_type': field_name.lower()
                    }
            return {'matched': False}
        
        # Ingredient matching
        elif category == 'Ingredients':
            for key in metadata:
                if key.startswith('ingredienttag:'):
                    ingredient = key.split(':', 1)[1].lower()
                    if criterion_lower in ingredient or ingredient in criterion_lower:
                        exact_match = criterion_lower == ingredient
                        return {
                            'matched': True,
                            'exact_match': exact_match,
                            'matched_value': ingredient,
                            'field_type': 'ingredient_tag'
                        }
            return {'matched': False}
        
        # Diet & health matching
        elif category == 'Diet & Health':
            for key in metadata:
                if key.startswith('specialdiettag:'):
                    diet_tag = key.split(':', 1)[1].lower()
                    if criterion_lower in diet_tag or diet_tag in criterion_lower:
                        exact_match = criterion_lower == diet_tag
                        return {
                            'matched': True,
                            'exact_match': exact_match,
                            'matched_value': diet_tag,
                            'field_type': 'diet_tag'
                        }
            return {'matched': False}
        
        # Pet type matching
        elif category == 'Pet Types':
            pet_type = str(metadata.get('ATTR_PET_TYPE', '')).lower()
            if criterion_lower in pet_type and pet_type:
                exact_match = criterion_lower == pet_type
                return {
                    'matched': True,
                    'exact_match': exact_match,
                    'matched_value': pet_type,
                    'field_type': 'pet_type'
                }
            return {'matched': False}
        
        # Product form matching
        elif category == 'Product Forms':
            food_form = str(metadata.get('ATTR_FOOD_FORM', '')).lower()
            if criterion_lower in food_form and food_form:
                exact_match = criterion_lower == food_form
                return {
                    'matched': True,
                    'exact_match': exact_match,
                    'matched_value': food_form,
                    'field_type': 'food_form'
                }
            return {'matched': False}
        
        # Default: search in product name and description
        else:
            searchable_fields = [
                ('name', str(metadata.get('CLEAN_NAME', ''))),
                ('title', str(metadata.get('NAME', ''))),
                ('description', str(metadata.get('DESCRIPTION_LONG', '')))
            ]
            
            for field_name, field_value in searchable_fields:
                field_lower = field_value.lower()
                if criterion_lower in field_lower and field_value:
                    # For text fields, exact match means the criterion is a complete word
                    words = field_lower.split()
                    exact_match = criterion_lower in words
                    return {
                        'matched': True,
                        'exact_match': exact_match,
                        'matched_value': field_value[:100],  # Truncate for display
                        'field_type': field_name
                    }
            
            return {'matched': False}

    # TODO: FIX HARDCODED CONFIDENCE VALUES, only reason is because of search match requiring confidence score
    def _calculate_match_confidence(self, criterion: str, metadata: dict, category: str, match_result: dict) -> float:
        """Calculate confidence score based on match quality and context"""
        if not match_result.get('matched', False):
            return 0.0
        
        # Base confidence scores by field type (how reliable the match is)
        field_type_scores = {
            'diet_tag': 0.95,        # Diet tags are very specific and reliable
            'ingredient_tag': 0.9,   # Ingredient tags are highly reliable
            'brand': 0.85,           # Brand matches are quite reliable
            'pet_type': 0.85,        # Pet type is very specific
            'food_form': 0.8,        # Food form is fairly specific
            'category_level1': 0.75, # Top-level categories are less specific
            'category_level2': 0.8,  # Mid-level categories are more specific
            'category_level3': 0.85, # Detailed categories are quite specific
            'name': 0.7,             # Product name matches are good but less structured
            'title': 0.7,            # Product title matches are good but less structured
            'description': 0.6       # Description matches are less reliable (noisy)
        }
        
        # Category importance weights
        category_weights = {
            'Diet & Health': 1.0,    # Most important for pet health
            'Pet Types': 0.95,       # Very important for targeting
            'Ingredients': 0.9,      # Important for allergies/preferences
            'Brands': 0.8,          # Important for brand loyalty
            'Categories': 0.75,      # Useful for product type
            'Product Forms': 0.7,    # Useful but less critical
            'Life Stages': 0.85,     # Important for age-appropriate products
            'Size/Weight': 0.8       # Important for breed-specific needs
        }
        
        # Get base score from field type
        field_type = match_result.get('field_type', 'unknown')
        base_score = field_type_scores.get(field_type, 0.5)
        
        # Get category weight
        category_weight = category_weights.get(category, 0.6)
        
        # Exact match bonus
        exact_match_bonus = 0.1 if match_result.get('exact_match', False) else 0.0
        
        # Calculate final confidence
        confidence = (base_score * category_weight) + exact_match_bonus
        
        # Ensure confidence is between 0.1 and 1.0
        confidence = max(0.1, min(1.0, confidence))
        
        return round(confidence, 2)

    def _get_matched_metadata_value(self, criterion: str, metadata: dict, category: str) -> str:
        """Get the actual metadata value that was matched"""
        if category == 'Brands':
            return metadata.get('PURCHASE_BRAND', '')
        elif category == 'Categories':
            return metadata.get('CATEGORY_LEVEL1', '')
        else:
            return metadata.get('CLEAN_NAME', '')[:50] + '...' 