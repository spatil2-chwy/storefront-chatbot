import json
import asyncio
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys
import os

# Add the server/src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from chat.chatbot_engine import chat_stream_with_products

logger = logging.getLogger(__name__)

class TestSuiteRunner:
    """Runs test queries through the chatbot system and saves evaluation logs"""
    
    def __init__(self, test_queries_path: str = "../data/core/test_queries.json"):
        self.test_queries_path = Path(test_queries_path)
        
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
    
    async def run_single_query(self, query_data: Dict[str, Any], user_context: str = ""):
        """Run a single query through the chatbot system"""
        query = query_data['query']
        category = query_data['category_name']
        
        logger.info(f"Running query from category '{category}': {query}...")
        
        start_time = time.time()
        
        try:
            # Run the query through the chatbot
            stream_generator, products = chat_stream_with_products(
                user_input=query,
                history=[],
                user_context=user_context
            )
            
            # Consume the generator to trigger the save_log() callback
            response_text = ""
            for chunk in stream_generator:
                response_text += chunk
            
            processing_time = time.time() - start_time
            
            logger.info(f"✅ Query completed in {processing_time:.2f}s - {len(products)} products found")
            logger.info(f"Response length: {len(response_text)} characters")
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"❌ Error running query '{query}': {e}")
            
    
    async def run_test_suite(self, 
                           user_context: str = "", 
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
        
        # Run queries sequentially to avoid overwhelming the system
        for i, query_data in enumerate(all_queries, 1):
            logger.info(f"Progress: {i}/{len(all_queries)}")
            
            await self.run_single_query(query_data, user_context)
            
            # Small delay between queries to be respectful to the system
            await asyncio.sleep(0.5)


async def main():
    """Main function to run the test suite"""
    runner = TestSuiteRunner()
    
    queries = runner.get_all_queries()

    # await runner.run_single_query(queries[0])
    await runner.run_test_suite()
    


if __name__ == "__main__":
    asyncio.run(main()) 