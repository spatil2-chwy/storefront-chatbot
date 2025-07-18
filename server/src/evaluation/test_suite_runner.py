"""
Test Suite Runner for Storefront Chatbot

This module runs test queries through the chatbot system via HTTP endpoints,
allowing for testing with customer context and user personas.

Usage:
1. Start the FastAPI server: uvicorn src.main:app --reload --host localhost --port 8000
2. Run the test suite: python src/evaluation/test_suite_runner.py

The test suite will use customer key 2098751972 (Kathleen Sumpson) by default
to test personalized responses with user context.
"""

import json
import asyncio
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys
import os
import requests

logger = logging.getLogger(__name__)

class TestSuiteRunner:
    """Runs test queries through the chatbot system and saves evaluation logs"""
    
    def __init__(self, test_queries_path: str = "../data/core/test_queries.json", base_url: str = "http://localhost:8000"):
        self.test_queries_path = Path(test_queries_path)
        self.base_url = base_url
        
    def load_test_queries(self) -> Dict[str, Any]:
        """Load test queries from JSON file"""
        try:
            with open(self.test_queries_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading test queries: {e}")
            raise
    
    def get_all_queries(self) -> List[Dict[str, Any]]:
        """Extract all queries from the test suite with their category information"""
        test_data = self.load_test_queries()
        queries = []
        
        for category_key, category_data in test_data['test_suite']['categories'].items():
            category_name = category_data['name']
            category_description = category_data['description']

            for query in category_data['queries']:
                queries.append({
                    'query': query,
                    'category_key': category_key,
                    'category_name': category_name,
                    'category_description': category_description
                })
                break # only run 1 query per category, uncomment to run all queries
            else:
                continue
        
        return queries
    
    async def run_single_query(self, query_data: Dict[str, Any], customer_key: Optional[int] = None):
        """Run a single query through the chatbot system via HTTP endpoint"""
        query = query_data['query']
        category = query_data['category_name']
        
        logger.info(f"Running query from category '{category}': {query}...")
        if customer_key:
            logger.info(f"Using customer key: {customer_key}")
        
        start_time = time.time()
        
        try:
            # Prepare the request payload
            payload = {
                "message": query,
                "history": [],
                "customer_key": customer_key,
                "image": None
            }
            
            # Make HTTP request to the chatbot stream endpoint
            response = requests.post(
                f"{self.base_url}/chats/chatbot/stream",
                json=payload,
                headers={"Content-Type": "application/json"},
                stream=True
            )
            
            if response.status_code != 200:
                error_text = response.text
                raise Exception(f"HTTP {response.status_code}: {error_text}")
            
            # Process the streaming response
            response_text = ""
            products = []
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8').strip()
                    if line_str.startswith('data: '):
                        try:
                            json_str = line_str[6:]  # Remove 'data: ' prefix
                            if json_str.strip():  # Skip empty data lines
                                data = json.loads(json_str)
                                
                                if 'chunk' in data:
                                    response_text += data['chunk']
                                elif 'products' in data:
                                    products = data['products']
                                    logger.info(f"Received {len(products)} products")
                                elif 'end' in data:
                                    break
                                elif 'error' in data:
                                    raise Exception(f"Streaming error: {data['error']}")
                                    
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse JSON from line: {line_str}")
                            continue
            
            processing_time = time.time() - start_time
            
            logger.info(f"✅ Query completed in {processing_time:.2f}s - {len(products)} products found")
            logger.info(f"Response length: {len(response_text)} characters")
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"❌ Error running query '{query}': {e}")
            
    
    async def run_test_suite(self, 
                           customer_key: Optional[int] = None, 
                           categories: Optional[List[str]] = None,
                           max_queries: Optional[int] = None):
        """Run the entire test suite or a subset of categories"""
        
        all_queries = self.get_all_queries()

        # Filter by categories if specified
        if categories:
            all_queries = [q for q in all_queries if q['category_key'] in categories]
        
        # Limit number of queries if specified
        if max_queries:
            all_queries = all_queries[:max_queries]
        
        logger.info(f"Starting test suite with {len(all_queries)} queries")
        if customer_key:
            logger.info(f"Using customer key: {customer_key} for all queries")
        
        # Run queries sequentially to avoid overwhelming the system
        for i, query_data in enumerate(all_queries, 1):
            logger.info(f"Progress: {i}/{len(all_queries)}")
            
            await self.run_single_query(query_data, customer_key)
            
            # Small delay between queries to be respectful to the system
            await asyncio.sleep(0.5)


async def main():
    """Main function to run the test suite"""
    runner = TestSuiteRunner()
    
    # Use customer key 2098751972 (Kathleen Sumpson) for testing
    customer_key = 2098751972
    
    # queries = runner.get_all_queries()

    # # Test a single query first to verify functionality
    # print("Testing single query with customer context...")
    # await runner.run_single_query(queries[0], customer_key)
    
    # Uncomment the line below to run the full test suite
    # This will test all categories with customer context
    await runner.run_test_suite(customer_key=customer_key)
    


if __name__ == "__main__":
    asyncio.run(main()) 