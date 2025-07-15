import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

class EvaluationDataParser:
    """
    Parser for LLM evaluation data from different JSON file types.
    Handles eval_*.json, llm_eval_*.json, and quantitative_report_*.json files.
    """
    
    def __init__(self):
        pass
    
    def load_eval_data(self, file_path: str) -> Dict[str, Any]:
        """
        Load and parse eval_*.json files containing raw session data.
        
        Args:
            file_path: Path to the eval JSON file
            
        Returns:
            Dictionary containing parsed evaluation data
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"Error loading eval data from {file_path}: {e}")
            return {}
    
    def load_llm_eval_data(self, file_path: str) -> Dict[str, Any]:
        """
        Load and parse llm_eval_*.json files containing evaluation scores.
        
        Args:
            file_path: Path to the llm_eval JSON file
            
        Returns:
            Dictionary containing parsed LLM evaluation data
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"Error loading LLM eval data from {file_path}: {e}")
            return {}
    
    def load_quantitative_data(self, file_path: str) -> Dict[str, Any]:
        """
        Load and parse quantitative_report_*.json files containing aggregated metrics.
        
        Args:
            file_path: Path to the quantitative report JSON file
            
        Returns:
            Dictionary containing parsed quantitative data
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"Error loading quantitative data from {file_path}: {e}")
            return {}
    
    def extract_pets_info(self, user_context: str) -> List[Dict[str, str]]:
        """
        Extract pet information from user context string.
        
        Args:
            user_context: String containing user context with pet information
            
        Returns:
            List of dictionaries containing pet information
        """
        pets = []
        
        # Pattern to match pet information blocks
        pet_pattern = r'Pet \d+:\s*\nName:\s*([^\n]+)\s*\nBreed:\s*([^\n]+)\s*\nAge:\s*([^\n]+)\s*\nLife Stage:\s*([^\n]+)\s*\nSize:\s*([^\n]+)\s*\nWeight:\s*([^\n]+)lbs'
        
        matches = re.finditer(pet_pattern, user_context, re.MULTILINE)
        
        for match in matches:
            pet_info = {
                'name': match.group(1).strip(),
                'breed': match.group(2).strip(),
                'age': match.group(3).strip(),
                'life_stage': match.group(4).strip(),
                'size': match.group(5).strip(),
                'weight': match.group(6).strip()
            }
            pets.append(pet_info)
        
        return pets
    
    def extract_customer_info(self, user_context: str) -> Dict[str, str]:
        """
        Extract customer information from user context string.
        
        Args:
            user_context: String containing user context
            
        Returns:
            Dictionary containing customer information
        """
        customer_info = {}
        
        # Extract customer name
        name_match = re.search(r'Customer:\s*([^\n]+)', user_context)
        if name_match:
            customer_info['name'] = name_match.group(1).strip()
        
        # Extract location
        location_match = re.search(r'Location:\s*([^\n]+)', user_context)
        if location_match:
            customer_info['location'] = location_match.group(1).strip()
        
        # Extract preferred brands
        brands_match = re.search(r'Preferred Brands:\s*([^\n]+)', user_context)
        if brands_match:
            customer_info['preferred_brands'] = brands_match.group(1).strip()
        
        # Extract dietary preferences
        dietary_match = re.search(r'Dietary Preferences:\s*([^\n]+)', user_context)
        if dietary_match:
            customer_info['dietary_preferences'] = dietary_match.group(1).strip()
        
        return customer_info
    
    def parse_tool_arguments(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Parse and format tool call arguments for display.
        
        Args:
            tool_calls: List of tool call dictionaries
            
        Returns:
            List of formatted tool call dictionaries
        """
        formatted_calls = []
        
        for call in tool_calls:
            formatted_call = {
                'tool_name': call.get('tool_name', 'Unknown'),
                'arguments': call.get('arguments', {})
            }
            
            # Format arguments for better display
            if isinstance(formatted_call['arguments'], str):
                try:
                    formatted_call['arguments'] = json.loads(formatted_call['arguments'])
                except:
                    pass
            
            formatted_calls.append(formatted_call)
        
        return formatted_calls
    
    def extract_enhanced_query(self, tool_calls: List[Dict[str, Any]]) -> str:
        """
        Extract the enhanced query from tool calls.
        
        Args:
            tool_calls: List of tool call dictionaries
            
        Returns:
            Enhanced query string
        """
        for call in tool_calls:
            if call.get('tool_name') == 'search_products':
                arguments = call.get('arguments', {})
                if isinstance(arguments, dict):
                    return arguments.get('query', 'No enhanced query found')
                elif isinstance(arguments, str):
                    try:
                        parsed_args = json.loads(arguments)
                        return parsed_args.get('query', 'No enhanced query found')
                    except:
                        return 'Could not parse enhanced query'
        
        return 'No enhanced query found'
    
    def format_timestamp(self, timestamp_str: str) -> str:
        """
        Format timestamp string for display.
        
        Args:
            timestamp_str: ISO format timestamp string
            
        Returns:
            Formatted timestamp string
        """
        try:
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return timestamp_str
    
    def get_performance_summary(self, eval_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract performance metrics from evaluation data.
        
        Args:
            eval_data: Evaluation data dictionary
            
        Returns:
            Dictionary containing performance metrics
        """
        return {
            'total_processing_time': eval_data.get('total_processing_time', 0),
            'function_call_time': eval_data.get('function_call_time', 0),
            'tool_execution_time': eval_data.get('tool_execution_time', 0),
            'product_search_time': eval_data.get('product_search_time', 0),
            'llm_response_time': eval_data.get('llm_response_time', 0),
            'products_returned': len(eval_data.get('product_results', []))
        }
    
    def get_product_summary(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary statistics for product results.
        
        Args:
            products: List of product dictionaries
            
        Returns:
            Dictionary containing product summary statistics
        """
        if not products:
            return {}
        
        prices = [p.get('price', 0) for p in products if p.get('price') is not None]
        ratings = [p.get('rating', 0) for p in products if p.get('rating') is not None]
        brands = [p.get('brand', '') for p in products if p.get('brand')]
        
        return {
            'total_products': len(products),
            'avg_price': sum(prices) / len(prices) if prices else 0,
            'min_price': min(prices) if prices else 0,
            'max_price': max(prices) if prices else 0,
            'avg_rating': sum(ratings) / len(ratings) if ratings else 0,
            'unique_brands': len(set(brands)),
            'brands': list(set(brands))
        } 