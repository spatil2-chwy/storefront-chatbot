import re
from typing import List, Dict
from src.models.product import SearchMatch

class SearchAnalyzer:
    def __init__(self):
        print("Search Analyzer initialized")
    
    def extract_search_criteria(self, query: str) -> Dict[str, List[str]]:
        """Extract and categorize search criteria from query"""
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
            'Flavor': []
        }
        
        # Extract criteria using pattern matching
        self._extract_pet_types(query_lower, categorized_criteria)
        self._extract_life_stages(query_lower, categorized_criteria)
        self._extract_sizes(query_lower, categorized_criteria)
        self._extract_brands(query_lower, categorized_criteria)
        self._extract_product_types(query_lower, categorized_criteria)
        self._extract_health_concerns(query_lower, categorized_criteria)
        self._extract_forms(query_lower, categorized_criteria)
        self._extract_diets(query_lower, categorized_criteria)
        self._extract_flavors(query_lower, categorized_criteria)
        
        # Remove empty categories
        return {k: v for k, v in categorized_criteria.items() if v}
    
    def _extract_pet_types(self, query: str, criteria: Dict[str, List[str]]):
        """Extract pet types and breed-specific size info"""
        # Pet type patterns
        pet_patterns = {
            'Dog': ['dog', 'canine', 'puppy', 'pup', 'k9'],
            'Cat': ['cat', 'feline', 'kitten', 'kitty'],
            'Bird': ['bird', 'avian', 'parrot'],
            'Fish': ['fish', 'aquatic', 'aquarium'],
            'Small Pet': ['rabbit', 'hamster', 'guinea pig', 'ferret'],
            'Horse': ['horse', 'equine'],
            'Reptile': ['reptile', 'snake', 'lizard', 'turtle']
        }
        
        # Dog breed size patterns
        breed_sizes = {
            'Small Breeds (5-25 lbs)': [
                'pomeranian', 'chihuahua', 'yorkie', 'yorkshire terrier', 'maltese', 'pug',
                'french bulldog', 'boston terrier', 'cavalier king charles', 'shih tzu',
                'jack russell', 'beagle', 'cocker spaniel', 'dachshund'
            ],
            'Medium Breeds (25-60 lbs)': [
                'border collie', 'australian shepherd', 'bulldog', 'boxer', 'siberian husky',
                'golden retriever', 'labrador', 'lab', 'german shepherd'
            ],
            'Large Breeds (60-100 lbs)': [
                'great dane', 'mastiff', 'saint bernard', 'newfoundland', 'bernese mountain dog'
            ]
        }
        
        # Check pet types
        for pet_type, patterns in pet_patterns.items():
            if any(pattern in query for pattern in patterns):
                criteria['Pet Type'].append(pet_type)
        
        # Check breed sizes (auto-adds Dog)
        for size, breeds in breed_sizes.items():
            if any(breed in query for breed in breeds):
                if 'Dog' not in criteria['Pet Type']:
                    criteria['Pet Type'].append('Dog')
                criteria['Size/Weight'].append(size)
    
    def _extract_life_stages(self, query: str, criteria: Dict[str, List[str]]):
        """Extract life stage information"""
        life_stages = {
            'Puppy': ['puppy', 'pup'],
            'Kitten': ['kitten'],
            'Adult': ['adult'],
            'Senior': ['senior', 'elderly', 'aged']
        }
        
        for stage, patterns in life_stages.items():
            if any(pattern in query for pattern in patterns):
                criteria['Life Stage'].append(stage)
    
    def _extract_sizes(self, query: str, criteria: Dict[str, List[str]]):
        """Extract size and weight information"""
        # Weight patterns
        weight_match = re.search(r'(\d+)\s*(?:lb|lbs|pound|pounds)', query)
        if weight_match:
            weight = int(weight_match.group(1))
            if weight <= 5:
                criteria['Size/Weight'].append('Toy/Extra Small (< 5 lbs)')
            elif weight <= 25:
                criteria['Size/Weight'].append('Small Breeds (5-25 lbs)')
            elif weight <= 60:
                criteria['Size/Weight'].append('Medium Breeds (25-60 lbs)')
            elif weight <= 100:
                criteria['Size/Weight'].append('Large Breeds (60-100 lbs)')
            else:
                criteria['Size/Weight'].append('Giant Breeds (100+ lbs)')
        
        # Size descriptors
        size_patterns = {
            'Toy/Extra Small (< 5 lbs)': ['toy', 'teacup', 'micro'],
            'Small Breeds (5-25 lbs)': ['small'],
            'Medium Breeds (25-60 lbs)': ['medium'],
            'Large Breeds (60-100 lbs)': ['large', 'big'],
            'Giant Breeds (100+ lbs)': ['giant', 'extra large', 'xl']
        }
        
        for size, patterns in size_patterns.items():
            if any(pattern in query for pattern in patterns):
                criteria['Size/Weight'].append(size)
    
    def _extract_brands(self, query: str, criteria: Dict[str, List[str]]):
        """Extract common brand names"""
        brands = {
            'Purina': ['purina'],
            'Hill\'s': ['hills', 'hill\'s'],
            'Royal Canin': ['royal canin'],
            'Blue Buffalo': ['blue buffalo'],
            'Wellness': ['wellness'],
            'Nutro': ['nutro'],
            'Iams': ['iams'],
            'Eukanuba': ['eukanuba'],
            'Science Diet': ['science diet'],
            'Pro Plan': ['pro plan']
        }
        
        for brand, patterns in brands.items():
            if any(pattern in query for pattern in patterns):
                criteria['Brand'].append(brand)
    
    def _extract_product_types(self, query: str, criteria: Dict[str, List[str]]):
        """Extract product type information"""
        product_types = {
            'Food': ['food', 'nutrition', 'diet', 'kibble'],
            'Dry Food': ['dry food', 'dry kibble'],
            'Wet Food': ['wet food', 'canned food', 'pate'],
            'Treats & Chews': ['treats', 'treat', 'chews', 'chew', 'snacks', 'biscuits'],
            'Toys': ['toys', 'toy', 'play'],
            'Healthcare': ['supplements', 'vitamins', 'medicine'],
            'Grooming': ['grooming', 'shampoo', 'brush']
        }
        
        for product_type, patterns in product_types.items():
            if any(pattern in query for pattern in patterns):
                criteria['Product Type'].append(product_type)
    
    def _extract_health_concerns(self, query: str, criteria: Dict[str, List[str]]):
        """Extract health-related concerns"""
        health_concerns = {
            'Dental Health': ['dental', 'teeth', 'oral', 'breath'],
            'Joint Health': ['joint', 'hip', 'arthritis', 'mobility'],
            'Digestive Health': ['digestive', 'stomach', 'probiotic', 'sensitive'],
            'Skin & Coat': ['skin', 'coat', 'fur', 'omega'],
            'Weight Management': ['weight', 'low fat', 'lean']
        }
        
        for concern, patterns in health_concerns.items():
            if any(pattern in query for pattern in patterns):
                criteria['Health Concern'].append(concern)
    
    def _extract_forms(self, query: str, criteria: Dict[str, List[str]]):
        """Extract product form information"""
        forms = {
            'Tablet': ['tablet', 'tablets', 'pill', 'pills'],
            'Soft Chews': ['soft chew', 'soft chews', 'chewy'],
            'Hard Chews': ['hard chew', 'hard chews'],
            'Powder': ['powder'],
            'Liquid': ['liquid', 'drops', 'oil']
        }
        
        for form, patterns in forms.items():
            if any(pattern in query for pattern in patterns):
                criteria['Form'].append(form)
    
    def _extract_diets(self, query: str, criteria: Dict[str, List[str]]):
        """Extract special diet information"""
        diets = {
            'Grain-Free': ['grain free', 'grain-free'],
            'Limited Ingredient': ['limited ingredient'],
            'High Protein': ['high protein'],
            'Low Fat': ['low fat'],
            'Organic': ['organic'],
            'Natural': ['natural'],
            'Gluten Free': ['gluten free']
        }
        
        for diet, patterns in diets.items():
            if any(pattern in query for pattern in patterns):
                criteria['Diet/Special Needs'].append(diet)
    
    def _extract_flavors(self, query: str, criteria: Dict[str, List[str]]):
        """Extract flavor information"""
        flavors = {
            'Chicken': ['chicken'],
            'Beef': ['beef'],
            'Fish': ['fish', 'salmon', 'tuna'],
            'Lamb': ['lamb'],
            'Turkey': ['turkey'],
            'Duck': ['duck'],
            'Pork': ['pork']
        }
        
        for flavor, patterns in flavors.items():
            if any(pattern in query for pattern in patterns):
                criteria['Flavor'].append(flavor)
    
    def analyze_product_matches(self, product_metadata: dict, categorized_criteria: Dict[str, List[str]], query: str) -> List[SearchMatch]:
        """Analyze which criteria matched this product"""
        if not categorized_criteria:
            return []
        
        matches = []
        
        # Get searchable text from product
        searchable_text = self._get_searchable_text(product_metadata)
        
        for category, criteria_list in categorized_criteria.items():
            for criterion in criteria_list:
                if self._criterion_matches_product(criterion, searchable_text, product_metadata, category):
                    confidence = self._calculate_confidence(criterion, category, product_metadata)
                    matches.append(SearchMatch(
                        field=f"{category}: {criterion}",
                        matched_terms=[criterion],
                        confidence=confidence,
                        field_value=self._get_matched_field_value(criterion, product_metadata)
                    ))
        
        return matches
    
    def _get_searchable_text(self, metadata: dict) -> str:
        """Get all searchable text from product"""
        text_parts = [
            str(metadata.get('CLEAN_NAME', '')),
            str(metadata.get('PURCHASE_BRAND', '')),
            str(metadata.get('CATEGORY_LEVEL1', '')),
            str(metadata.get('DESCRIPTION_LONG', ''))
        ]
        
        # Add tag fields
        for key in metadata:
            if key.startswith(('specialdiettag:', 'ingredienttag:')):
                text_parts.append(key.split(':', 1)[1])
        
        return ' '.join(text_parts).lower()
    
    def _criterion_matches_product(self, criterion: str, searchable_text: str, metadata: dict, category: str) -> bool:
        """Check if criterion matches the product"""
        criterion_lower = criterion.lower()
        
        # Category-specific matching
        if category == 'Brand':
            return criterion_lower in str(metadata.get('PURCHASE_BRAND', '')).lower()
        elif category == 'Product Type':
            return criterion_lower in searchable_text
        elif category == 'Diet/Special Needs':
            # Check special diet tags
            for key in metadata:
                if key.startswith('specialdiettag:') and criterion_lower.replace(' ', '-') in key.lower():
                    return True
            return criterion_lower in searchable_text
        elif category == 'Flavor':
            # Check ingredient tags
            for key in metadata:
                if key.startswith('ingredienttag:') and criterion_lower in key.lower():
                    return True
            return criterion_lower in searchable_text
        
        # General text match
        return criterion_lower in searchable_text
    
    def _calculate_confidence(self, criterion: str, category: str, metadata: dict) -> float:
        """Calculate match confidence"""
        base_confidence = {
            'Pet Type': 0.95,
            'Brand': 0.90,
            'Size/Weight': 0.85,
            'Product Type': 0.80,
            'Health Concern': 0.85,
            'Life Stage': 0.90,
            'Form': 0.75,
            'Diet/Special Needs': 0.85,
            'Flavor': 0.75
        }
        return base_confidence.get(category, 0.70)
    
    def _get_matched_field_value(self, criterion: str, metadata: dict) -> str:
        """Get the field value that was matched"""
        return metadata.get('CLEAN_NAME', '')[:50] + '...' 