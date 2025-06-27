import re
import json
import os
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from src.models.product import SearchMatch

class SearchAnalyzer:
    def __init__(self):
        self.cache_file = "search_analysis_cache.json"
        self.cache_duration = timedelta(hours=24)  # Refresh cache daily
        
        # Initialize ChromaDB connection
        self._init_chromadb()
        
        # Load or build semantic pattern database
        self._load_or_build_semantic_patterns()
        print("✅ SearchAnalyzer initialized with semantic similarity matching")
    
    def _init_chromadb(self):
        """Initialize ChromaDB connection"""
        try:
            import chromadb
            self.client = chromadb.PersistentClient(path="../scripts/chroma_db")
            self.collection = self.client.get_collection(name="products")
            print("📊 Connected to ChromaDB for semantic pattern matching")
        except Exception as e:
            print(f"⚠️ ChromaDB connection failed: {e}")
            self.client = None
            self.collection = None
    
    def _load_or_build_semantic_patterns(self):
        """Load semantic patterns from cache or build from database"""
        if self._should_refresh_cache():
            print("🔄 Building semantic pattern database...")
            self._build_semantic_pattern_database()
            self._save_cache()
        else:
            print("📂 Loading semantic patterns from cache...")
            self._load_cache()
    
    def _should_refresh_cache(self) -> bool:
        """Check if cache needs refreshing"""
        if not os.path.exists(self.cache_file):
            return True
        
        try:
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
                cache_time = datetime.fromisoformat(cache_data.get('timestamp', '2000-01-01'))
                return datetime.now() - cache_time > self.cache_duration
        except:
            return True
    
    def _build_semantic_pattern_database(self):
        """Build semantic pattern database by analyzing actual product data"""
        if not self.collection:
            self._initialize_fallback_patterns()
            return
        
        try:
            # Get all unique field values for semantic analysis
            results = self.collection.get(limit=5000)  # Sample for performance
            
            if not results['metadatas']:
                self._initialize_fallback_patterns()
                return
            
            print(f"Analyzing {len(results['metadatas'])} products for semantic patterns...")
            
            # Collect unique values by category
            self.semantic_patterns = {
                'brands': set(),
                'categories': set(),
                'special_diets': set(),
                'ingredients': set(),
                'product_names': [],
                'descriptions': []
            }
            
            for metadata in results['metadatas']:
                if not metadata:
                    continue
                
                # Collect brands - handle compound brands with || separator
                brand = metadata.get('PURCHASE_BRAND', '').strip()
                if brand and len(brand) > 1:
                    # Split on || and add all brand parts
                    brand_parts = brand.split('||')
                    for brand_part in brand_parts:
                        brand_clean = brand_part.strip().lower()
                        if brand_clean and len(brand_clean) > 2:
                            self.semantic_patterns['brands'].add(brand_clean)
                            
                            # Also add individual words for better matching
                            brand_words = brand_clean.split()
                            if len(brand_words) > 1:
                                for word in brand_words:
                                    # Filter out common descriptive words that could conflict with other categories
                                    excluded_words = {
                                        'the', 'and', 'for', 'pet', 'dog', 'cat', 'small', 'large', 'mini', 
                                        'big', 'tiny', 'giant', 'super', 'ultra', 'premium', 'natural', 
                                        'organic', 'grain', 'free', 'fresh', 'dry', 'wet', 'soft', 'hard',
                                        'senior', 'adult', 'puppy', 'kitten', 'healthy', 'diet', 'food',
                                        'treats', 'chews', 'toys', 'care', 'health', 'nutrition', 'plus'
                                    }
                                    if len(word) > 2 and word not in excluded_words:
                                        self.semantic_patterns['brands'].add(word)
                
                # Collect categories
                for cat_field in ['CATEGORY_LEVEL1', 'CATEGORY_LEVEL2', 'CATEGORY_LEVEL3']:
                    category = metadata.get(cat_field, '').strip()
                    if category and len(category) > 1:
                        self.semantic_patterns['categories'].add(category.lower())
                
                # Collect special diet and ingredient tags
                for key in metadata:
                    if key.startswith('specialdiettag:'):
                        tag = key.split(':', 1)[1].strip()
                        if tag and len(tag) > 2:  # Filter out very short tags
                            self.semantic_patterns['special_diets'].add(tag.lower())
                    elif key.startswith('ingredienttag:'):
                        tag = key.split(':', 1)[1].strip()
                        if tag and len(tag) > 2 and not tag.isdigit():  # Filter out very short tags and numbers
                            # Also filter out single letters and meaningless tags
                            tag_lower = tag.lower()
                            if not (len(tag_lower) == 1 or tag_lower in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']):
                                self.semantic_patterns['ingredients'].add(tag_lower)
                
                # Collect product names and descriptions for context
                name = metadata.get('CLEAN_NAME', '').strip()
                if name:
                    self.semantic_patterns['product_names'].append(name.lower())
                
                desc = metadata.get('DESCRIPTION_LONG', '').strip()
                if desc and len(desc) > 20:  # Only meaningful descriptions
                    self.semantic_patterns['descriptions'].append(desc.lower()[:200])  # Truncate long descriptions
            
            # Convert sets to lists for JSON serialization
            for key in ['brands', 'categories', 'special_diets', 'ingredients']:
                self.semantic_patterns[key] = list(self.semantic_patterns[key])
            
            print(f"✅ Built semantic database:")
            print(f"  • {len(self.semantic_patterns['brands'])} unique brands")
            print(f"  • {len(self.semantic_patterns['categories'])} unique categories")
            print(f"  • {len(self.semantic_patterns['special_diets'])} special diet tags")
            print(f"  • {len(self.semantic_patterns['ingredients'])} ingredient tags")
            
        except Exception as e:
            print(f"Error building semantic patterns: {e}")
            self._initialize_fallback_patterns()
    
    def _initialize_fallback_patterns(self):
        """Initialize with basic fallback patterns if database analysis fails"""
        print("⚠️ Using fallback semantic patterns")
        self.semantic_patterns = {
            'brands': ['purina', 'hills', 'royal canin', 'blue buffalo', 'wellness'],
            'categories': ['dog food', 'cat food', 'treats', 'toys', 'supplements'],
            'special_diets': ['grain-free', 'limited ingredient', 'high protein', 'low fat'],
            'ingredients': ['chicken', 'beef', 'salmon', 'lamb', 'turkey'],
            'product_names': [],
            'descriptions': []
        }
    
    def extract_search_criteria(self, query: str) -> Dict[str, List[str]]:
        """Extract and categorize search criteria using semantic similarity"""
        query_lower = query.lower().strip()
        
        # Initialize result categories
        categorized_criteria = {
            'Pet Type': [],
            'Life Stage': [],
            'Size/Weight': [],
            'Brand': [],
            'Product Type': [],
            'Health Concern': [],
            'Form': [],
            'Diet/Special Needs': [],
            'Flavor': [],
            'Other': []
        }
        
        # Extract weight-based size first (this is rule-based)
        weight_categories = self._extract_size_weight_categories(query_lower)
        if weight_categories:
            categorized_criteria['Size/Weight'].extend(weight_categories)
        
        # Use semantic similarity for other categories
        self._extract_semantic_matches(query_lower, categorized_criteria)
        
        # Remove empty categories
        return {k: v for k, v in categorized_criteria.items() if v}
    
    def _extract_semantic_matches(self, query: str, categorized_criteria: Dict[str, List[str]]):
        """Use semantic similarity to find matches in each category"""
        
        # Semantic brand matching
        brand_matches = self._find_semantic_matches(query, self.semantic_patterns['brands'], threshold=0.3)
        for brand, confidence in brand_matches:
            categorized_criteria['Brand'].append(brand.title())
        
        # Semantic category matching for Product Type
        category_matches = self._find_semantic_matches(query, self.semantic_patterns['categories'], threshold=0.3)
        for category, confidence in category_matches:
            # Categorize the category into product types
            product_type = self._categorize_product_type(category)
            if product_type and product_type not in categorized_criteria['Product Type']:
                categorized_criteria['Product Type'].append(product_type)
        
        # Semantic diet matching
        diet_matches = self._find_semantic_matches(query, self.semantic_patterns['special_diets'], threshold=0.3)
        for diet, confidence in diet_matches:
            diet_formatted = diet.replace('-', ' ').replace('_', ' ').title()
            if diet_formatted not in categorized_criteria['Diet/Special Needs']:
                categorized_criteria['Diet/Special Needs'].append(diet_formatted)
        
        # Semantic ingredient/flavor matching
        ingredient_matches = self._find_semantic_matches(query, self.semantic_patterns['ingredients'], threshold=0.3)
        for ingredient, confidence in ingredient_matches:
            flavor = self._categorize_flavor(ingredient)
            if flavor and flavor not in categorized_criteria['Flavor']:
                categorized_criteria['Flavor'].append(flavor)
        
        # Rule-based pet type and life stage (these are universal)
        self._extract_rule_based_categories(query, categorized_criteria)
        
        # Rule-based health concerns and forms
        self._extract_health_and_form_categories(query, categorized_criteria)
    
    def _find_semantic_matches(self, query_text, pattern_list, threshold=0.3):
        """Find semantic matches using Jaccard similarity and substring matching"""
        if not pattern_list:
            return []
        
        query_lower = query_text.lower()
        query_words = set(query_lower.split())
        matches = []
        
        for pattern in pattern_list:
            pattern_lower = pattern.lower()
            pattern_words = set(pattern_lower.split())
            
            # Direct substring match (high confidence)
            if pattern_lower in query_lower or query_lower in pattern_lower:
                matches.append((pattern, 0.9))
                continue
            
            # Check if all words in pattern are in query (for compound brands)
            if pattern_words.issubset(query_words):
                matches.append((pattern, 0.8))
                continue
            
            # Jaccard similarity
            intersection = len(query_words.intersection(pattern_words))
            union = len(query_words.union(pattern_words))
            
            if union > 0:
                similarity = intersection / union
                if similarity >= threshold:
                    matches.append((pattern, similarity))
        
        # Sort by similarity score descending
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches[:5]  # Return top 5 matches
    
    def _categorize_product_type(self, category: str) -> str:
        """Categorize a discovered category into standard product types"""
        category_lower = category.lower()
        
        if any(word in category_lower for word in ['food', 'nutrition', 'diet', 'kibble']):
            if any(word in category_lower for word in ['dry', 'kibble']):
                return 'Dry Food'
            elif any(word in category_lower for word in ['wet', 'canned', 'pate']):
                return 'Wet Food'
            else:
                return 'Food'
        elif any(word in category_lower for word in ['treat', 'chew', 'snack', 'biscuit']):
            return 'Treats & Chews'
        elif any(word in category_lower for word in ['toy', 'play']):
            return 'Toys'
        elif any(word in category_lower for word in ['supplement', 'vitamin', 'health']):
            return 'Healthcare'
        elif any(word in category_lower for word in ['grooming', 'shampoo', 'brush']):
            return 'Grooming'
        else:
            return category.title()
    
    def _categorize_flavor(self, ingredient: str) -> str:
        """Categorize an ingredient into standard flavor categories"""
        ingredient_lower = ingredient.lower()
        
        if 'chicken' in ingredient_lower or 'poultry' in ingredient_lower:
            return 'Chicken'
        elif 'beef' in ingredient_lower or 'steak' in ingredient_lower:
            return 'Beef'
        elif any(fish in ingredient_lower for fish in ['salmon', 'tuna', 'cod', 'fish']):
            return 'Fish'
        elif 'lamb' in ingredient_lower:
            return 'Lamb'
        elif 'turkey' in ingredient_lower:
            return 'Turkey'
        elif 'duck' in ingredient_lower:
            return 'Duck'
        elif 'pork' in ingredient_lower:
            return 'Pork'
        else:
            return ingredient.title()
    
    def _extract_rule_based_categories(self, query: str, categorized_criteria: Dict[str, List[str]]):
        """Extract pet type and life stage using rule-based matching (these are universal)"""
        
        # Pet Type patterns
        pet_patterns = {
            'Dog': ['dog', 'canine', 'puppy', 'pup', 'k9'],
            'Cat': ['cat', 'feline', 'kitten', 'kitty'],
            'Bird': ['bird', 'avian', 'parrot'],
            'Fish': ['fish', 'aquatic', 'aquarium'],
            'Small Pet': ['rabbit', 'hamster', 'guinea pig', 'ferret'],
            'Horse': ['horse', 'equine'],
            'Reptile': ['reptile', 'snake', 'lizard', 'turtle']
        }
        
        # Dog breed patterns (automatically categorize as Dog and add size)
        dog_breed_patterns = {
            # Small breeds
            'Small Breeds (5-25 lbs)': [
                'pomeranian', 'chihuahua', 'yorkshire terrier', 'yorkie', 'maltese', 'pug', 
                'french bulldog', 'boston terrier', 'cavalier king charles', 'shih tzu',
                'jack russell', 'beagle', 'cocker spaniel', 'dachshund', 'wiener dog'
            ],
            # Medium breeds  
            'Medium Breeds (25-60 lbs)': [
                'border collie', 'australian shepherd', 'bulldog', 'boxer', 'siberian husky',
                'golden retriever', 'labrador', 'lab', 'german shepherd', 'rottweiler'
            ],
            # Large breeds
            'Large Breeds (60-100 lbs)': [
                'great dane', 'mastiff', 'saint bernard', 'newfoundland', 'bernese mountain dog'
            ]
        }
        
        # Life Stage patterns
        life_stage_patterns = {
            'Puppy': ['puppy', 'pup'],
            'Kitten': ['kitten'],
            'Adult': ['adult', 'grown'],
            'Senior': ['senior', 'old', 'elderly', 'aged']
        }
        
        # Check for regular pet types
        for pet_type, patterns in pet_patterns.items():
            if any(pattern in query.lower() for pattern in patterns):
                if pet_type not in categorized_criteria['Pet Type']:
                    categorized_criteria['Pet Type'].append(pet_type)
        
        # Check for dog breeds (automatically adds Dog and size)
        for size_category, breeds in dog_breed_patterns.items():
            if any(breed in query.lower() for breed in breeds):
                # Add Dog as pet type
                if 'Dog' not in categorized_criteria['Pet Type']:
                    categorized_criteria['Pet Type'].append('Dog')
                # Add size category
                if size_category not in categorized_criteria['Size/Weight']:
                    categorized_criteria['Size/Weight'].append(size_category)
        
        # Check for life stages
        for life_stage, patterns in life_stage_patterns.items():
            if any(pattern in query.lower() for pattern in patterns):
                if life_stage not in categorized_criteria['Life Stage']:
                    categorized_criteria['Life Stage'].append(life_stage)
    
    def _extract_health_and_form_categories(self, query: str, categorized_criteria: Dict[str, List[str]]):
        """Extract health concerns and forms using rule-based matching"""
        
        # Health concern patterns
        health_patterns = {
            'Dental Health': ['dental', 'teeth', 'oral', 'breath'],
            'Joint Health': ['joint', 'hip', 'arthritis', 'mobility'],
            'Digestive Health': ['digestive', 'stomach', 'probiotic', 'sensitive'],
            'Skin & Coat': ['skin', 'coat', 'fur', 'omega', 'itchy'],
            'Weight Management': ['weight', 'diet', 'low fat', 'lean']
        }
        
        # Form patterns
        form_patterns = {
            'Tablet': ['tablet', 'tablets', 'pill', 'pills'],
            'Soft Chews': ['soft chew', 'soft chews', 'chewy'],
            'Hard Chews': ['hard chew', 'hard chews', 'dental stick'],
            'Powder': ['powder', 'powdered'],
            'Liquid': ['liquid', 'drops', 'oil']
        }
        
        for health_concern, patterns in health_patterns.items():
            if any(pattern in query.lower() for pattern in patterns):
                if health_concern not in categorized_criteria['Health Concern']:
                    categorized_criteria['Health Concern'].append(health_concern)
        
        for form, patterns in form_patterns.items():
            if any(pattern in query.lower() for pattern in patterns):
                if form not in categorized_criteria['Form']:
                    categorized_criteria['Form'].append(form)
    
    def _extract_size_weight_categories(self, query: str) -> List[str]:
        """Extract size and weight categories from query"""
        categories = []
        query_lower = query.lower()
        
        # Weight patterns with size conversion
        weight_patterns = [
            (r'(\d+)\s*(?:lb|lbs|pound|pounds)', lambda m: self._weight_to_size(int(m.group(1)))),
            (r'(\d+)\s*(?:kg|kilograms?)', lambda m: self._weight_to_size(int(m.group(1)) * 2.2)),  # Convert kg to lbs
        ]
        
        for pattern, converter in weight_patterns:
            matches = re.finditer(pattern, query_lower)
            for match in matches:
                size_category = converter(match)
                if size_category:
                    categories.append(size_category)
        
        # Direct size descriptors - enhanced patterns
        size_patterns = [
            # Dog-specific sizes
            (r'\b(?:toy|teacup|micro|mini)\s+(?:dog|breed|size)', 'Toy/Extra Small (< 5 lbs)'),
            (r'\b(?:small|little|petite)\s+(?:dog|breed|size)', 'Small Breeds (5-25 lbs)'),
            (r'\b(?:medium|mid|average)\s+(?:dog|breed|size)', 'Medium Breeds (25-60 lbs)'),
            (r'\b(?:large|big)\s+(?:dog|breed|size)', 'Large Breeds (60-100 lbs)'),
            (r'\b(?:giant|extra\s+large|xl)\s+(?:dog|breed|size)', 'Giant Breeds (100+ lbs)'),
            
            # General size descriptors
            (r'\btoy\b(?!\s+(?:car|truck|vehicle))', 'Toy/Extra Small (< 5 lbs)'),
            (r'\bsmall\b(?!\s+(?:business|company))', 'Small Breeds (5-25 lbs)'),
            (r'\bmedium\b', 'Medium Breeds (25-60 lbs)'),
            (r'\blarge\b(?!\s+(?:business|company))', 'Large Breeds (60-100 lbs)'),
            (r'\bgiant\b', 'Giant Breeds (100+ lbs)'),
            (r'\bextra\s+large\b', 'Giant Breeds (100+ lbs)'),
            (r'\bxl\b', 'Giant Breeds (100+ lbs)'),
            
            # Puppy/kitten sizes
            (r'\bpuppy\b', 'Puppy/Kitten'),
            (r'\bkitten\b', 'Puppy/Kitten'),
        ]
        
        for pattern, category in size_patterns:
            if re.search(pattern, query_lower):
                categories.append(category)
        
        return list(set(categories))  # Remove duplicates
    
    def _weight_to_size(self, weight: int) -> str:
        """Convert weight to appropriate size category"""
        if weight <= 5:
            return 'Toy/Extra Small (< 5 lbs)'
        elif weight <= 25:
            return 'Small Breeds (5-25 lbs)'
        elif weight <= 60:
            return 'Medium Breeds (25-60 lbs)'
        elif weight <= 100:
            return 'Large Breeds (60-100 lbs)'
        else:
            return 'Giant Breeds (100+ lbs)'
    
    def analyze_product_matches(self, product_metadata: dict, categorized_criteria: Dict[str, List[str]], query: str) -> List[SearchMatch]:
        """Analyze which categorized criteria matched this product using semantic similarity"""
        if not categorized_criteria:
            return []
        
        matches = []
        
        # Get all searchable text from the product once
        searchable_text = self._get_product_searchable_text(product_metadata)
        
        # Pre-compute common checks
        product_name = (product_metadata.get('CLEAN_NAME', '') + ' ' + product_metadata.get('NAME', '')).lower()
        brand = str(product_metadata.get('PURCHASE_BRAND', '')).lower()
        
        for category, criteria_list in categorized_criteria.items():
            for criterion in criteria_list:
                if self._criterion_matches_product_semantic(criterion, searchable_text, product_name, brand, category, product_metadata):
                    # Determine match type efficiently
                    match_type = self._determine_match_type_fast(criterion, searchable_text, product_name, brand, product_metadata)
                    confidence = self._calculate_confidence_fast(criterion, match_type, category)
                    
                    matches.append(SearchMatch(
                        field=f"{category}: {criterion}",
                        matched_terms=[criterion],
                        confidence=confidence,
                        field_value=self._get_field_value_for_match(match_type, product_metadata)
                    ))
        
        return matches
    
    def _criterion_matches_product_semantic(self, criterion: str, searchable_text: str, product_name: str, brand: str, category: str, metadata: dict) -> bool:
        """Check if criterion matches product using semantic similarity"""
        criterion_lower = criterion.lower()
        
        # Quick checks first (most common cases)
        if criterion_lower in product_name or criterion_lower in brand:
            return True
        
        # Category-specific semantic matching
        if category == 'Brand':
            # For brands, check if the criterion matches the actual brand field
            return criterion_lower in brand or any(word in brand for word in criterion_lower.split())
        
        elif category == 'Product Type':
            # Check categories and product type indicators
            categories = ' '.join([
                str(metadata.get('CATEGORY_LEVEL1', '')),
                str(metadata.get('CATEGORY_LEVEL2', '')),
                str(metadata.get('CATEGORY_LEVEL3', ''))
            ]).lower()
            
            if criterion == 'Treats & Chews':
                return any(term in searchable_text for term in ['treat', 'treats', 'chew', 'chews', 'snack', 'biscuit'])
            elif criterion == 'Dry Food':
                return any(term in searchable_text for term in ['dry', 'kibble', 'food']) and 'wet' not in searchable_text
            elif criterion == 'Wet Food':
                return any(term in searchable_text for term in ['wet', 'canned', 'pate', 'gravy'])
            else:
                return criterion_lower in categories
        
        elif category == 'Diet/Special Needs':
            # Check special diet tags
            for key in metadata:
                if key.startswith('specialdiettag:') and criterion_lower.replace(' ', '-') in key.lower():
                    return True
            return criterion_lower in searchable_text
        
        elif category == 'Flavor':
            # Check ingredient tags and product text
            for key in metadata:
                if key.startswith('ingredienttag:') and criterion_lower in key.lower():
                    return True
            return criterion_lower in searchable_text
        
        elif category == 'Health Concern':
            if criterion == 'Dental Health':
                return any(term in searchable_text for term in ['dental', 'teeth', 'oral', 'breath', 'tartar', 'plaque'])
            elif criterion == 'Joint Health':
                return any(term in searchable_text for term in ['joint', 'hip', 'arthritis', 'mobility', 'glucosamine'])
            elif criterion == 'Digestive Health':
                return any(term in searchable_text for term in ['digestive', 'stomach', 'probiotic', 'fiber', 'sensitive'])
        
        elif category == 'Form':
            if criterion == 'Soft Chews':
                return any(term in searchable_text for term in ['soft chew', 'soft chews', 'chewy', 'gummy'])
            elif criterion == 'Tablet':
                return any(term in searchable_text for term in ['tablet', 'tablets', 'pill', 'pills'])
        
        # General text match as fallback
        return criterion_lower in searchable_text
    
    def _calculate_confidence_fast(self, criterion: str, match_type: str, category: str) -> float:
        """Fast confidence calculation with category awareness"""
        base_confidence = {
            'Product Name': 0.95,
            'Brand': 0.90,
            'Special Diet': 0.90,
            'Category': 0.85,
            'Ingredients': 0.80,
            'Description': 0.70,
            'General Match': 0.60
        }
        
        confidence = base_confidence.get(match_type, 0.60)
        
        # Boost confidence for important categories
        if category in ['Health Concern', 'Pet Type', 'Life Stage', 'Brand']:
            confidence = min(confidence + 0.1, 1.0)
        
        return confidence
    
    def _determine_match_type_fast(self, criterion: str, searchable_text: str, product_name: str, brand: str, metadata: dict) -> str:
        """Fast version of match type determination"""
        criterion_lower = criterion.lower()
        
        # Quick checks in order of likelihood
        if criterion_lower in product_name:
            return 'Product Name'
        
        if criterion_lower in brand:
            return 'Brand'
        
        # Check categories (combine all category fields)
        categories = ' '.join([
            str(metadata.get('CATEGORY_LEVEL1', '')),
            str(metadata.get('CATEGORY_LEVEL2', '')),
            str(metadata.get('CATEGORY_LEVEL3', ''))
        ]).lower()
        if criterion_lower in categories:
            return 'Category'
        
        # Check special diet tags (only if not already matched)
        if any(key.startswith('specialdiettag:') and criterion_lower in key.lower() for key in metadata):
            return 'Special Diet'
        
        # Check ingredient tags
        if any(key.startswith('ingredienttag:') and criterion_lower in key.lower() for key in metadata):
            return 'Ingredients'
        
        # Check description as last resort
        description = str(metadata.get('DESCRIPTION_LONG', '')).lower()
        if criterion_lower in description:
            return 'Description'
        
        return 'General Match'
    
    def _get_field_value_for_match(self, match_type: str, metadata: dict) -> str:
        """Get the field value that was matched"""
        if match_type == 'Product Name':
            return metadata.get('CLEAN_NAME', metadata.get('NAME', ''))
        elif match_type == 'Brand':
            return metadata.get('PURCHASE_BRAND', '')
        elif match_type == 'Category':
            return metadata.get('CATEGORY_LEVEL1', '')
        elif match_type == 'Description':
            return metadata.get('DESCRIPTION_LONG', '')[:100] + '...'
        else:
            return ''
    
    def _get_product_searchable_text(self, metadata: dict) -> str:
        """Get all searchable text from product metadata"""
        try:
            # Combine all searchable text fields
            text_parts = [
                str(metadata.get('CLEAN_NAME', '')),
                str(metadata.get('NAME', '')),
                str(metadata.get('PURCHASE_BRAND', '')),
                str(metadata.get('CATEGORY_LEVEL1', '')),
                str(metadata.get('CATEGORY_LEVEL2', '')),
                str(metadata.get('CATEGORY_LEVEL3', '')),
                str(metadata.get('DESCRIPTION_LONG', '')),
            ]
            
            # Add tag fields
            for key in metadata:
                if key.startswith(('specialdiettag:', 'ingredienttag:')):
                    text_parts.append(key.split(':', 1)[1])
            
            return ' '.join(text_parts).lower()
        except Exception:
            return ''
    
    def _save_cache(self):
        """Save discovered patterns to cache"""
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'semantic_patterns': self.semantic_patterns
            }
            
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            print(f"💾 Semantic patterns cached to {self.cache_file}")
        except Exception as e:
            print(f"⚠️ Failed to save cache: {e}")
    
    def _load_cache(self):
        """Load patterns from cache"""
        try:
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
            
            self.semantic_patterns = cache_data.get('semantic_patterns', {})
            
            print(f"📂 Loaded semantic patterns from cache")
            print(f"  • {len(self.semantic_patterns.get('brands', []))} brands")
            print(f"  • {len(self.semantic_patterns.get('categories', []))} categories")
        except Exception as e:
            print(f"⚠️ Failed to load cache: {e}")
            self._initialize_fallback_patterns()
    
    def get_discovered_patterns_summary(self) -> Dict:
        """Get a summary of discovered semantic patterns for debugging"""
        return {
            'brands': self.semantic_patterns.get('brands', [])[:10],  # Top 10 brands
            'categories': self.semantic_patterns.get('categories', [])[:10],  # Top 10 categories
            'special_diets': self.semantic_patterns.get('special_diets', [])[:10],
            'ingredients': self.semantic_patterns.get('ingredients', [])[:10],
            'total_brands': len(self.semantic_patterns.get('brands', [])),
            'total_categories': len(self.semantic_patterns.get('categories', [])),
            'cache_file': self.cache_file,
            'cache_exists': os.path.exists(self.cache_file)
        }
    
    # Legacy method for compatibility - convert new format to old format
    def extract_search_terms(self, query: str) -> Dict[str, List[str]]:
        """Legacy method - flatten categorized criteria for backward compatibility"""
        categorized = self.extract_search_criteria(query)
        all_criteria = []
        for criteria_list in categorized.values():
            all_criteria.extend(criteria_list)
        
        return {
            'general': all_criteria,
            'pet_terms': categorized.get('Pet Type', []),
            'diet_terms': categorized.get('Diet/Special Needs', []),
            'size_terms': categorized.get('Size/Weight', []),
            'brand_terms': categorized.get('Brand', [])
        }
    
    def get_available_terms(self) -> Dict[str, any]:
        """Return empty dict for compatibility"""
        return {'message': 'Using lightweight search criteria extraction'}
    
    def get_searchable_fields(self) -> Dict[str, str]:
        """Return empty dict for compatibility"""
        return {'message': 'Using lightweight search criteria extraction'}
    
    def get_category_context(self) -> Dict[str, any]:
        """Return empty dict for compatibility"""
        return {'message': 'Using lightweight search criteria extraction'} 