import chromadb
import pandas as pd
from functools import lru_cache
import time
import math
import logging
from typing import cast, Any

# Initialize logging first
from src.evaluation.logging_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

import os
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
product_df_path = os.path.join(project_root, "data", "backend", "products", "product_df.csv")
product_df = pd.read_csv(product_df_path)

import os
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
chromadb_path = os.path.join(project_root, "data", "databases", "chroma_db")
client = chromadb.PersistentClient(path=chromadb_path)
REVIEW_COLLECTION_NAME = "review_synthesis"
review_collection = client.get_collection(name=REVIEW_COLLECTION_NAME)

def filter_product_ids(required_ingredients: list, excluded_ingredients: list, category_level_1: list, category_level_2: list):
    """Filter product DataFrame to get product IDs based on ingredients and categories"""
    # Start with all products
    mask = pd.Series([True] * len(product_df), index=product_df.index)
    
    # Filter by required ingredients
    for ingredient in required_ingredients:
        ingredient_mask = product_df['INGREDIENTS'].str.contains(ingredient, case=False, na=False)
        mask = mask & ingredient_mask
    
    # Filter out excluded ingredients
    for ingredient in excluded_ingredients:
        excluded_mask = product_df['INGREDIENTS'].str.contains(ingredient, case=False, na=False)
        mask = mask & ~excluded_mask
    
    # Filter by category level 1
    for category in category_level_1:
        if 'CATEGORY_LEVEL_1' in product_df.columns:
            category_mask = product_df['CATEGORY_LEVEL_1'].str.contains(category, case=False, na=False)
            mask = mask & category_mask
    
    # Filter by category level 2
    for category in category_level_2:
        if 'CATEGORY_LEVEL_2' in product_df.columns:
            category_mask = product_df['CATEGORY_LEVEL_2'].str.contains(category, case=False, na=False)
            mask = mask & category_mask
    
    # Get filtered product IDs
    filtered_ids = product_df[mask]['PRODUCT_ID'].astype(str).tolist()
    return filtered_ids


@lru_cache(maxsize=128)
def query_products(query: str, required_ingredients=(), excluded_ingredients=(), category_level_1=(), category_level_2=()):
    logger.debug(f"Query cache info: {query_products.cache_info()}")

    # Use pandas to filter product IDs based on ingredients and categories
    filtered_ids = filter_product_ids(
        list(required_ingredients), 
        list(excluded_ingredients), 
        list(category_level_1), 
        list(category_level_2)
    )
    
    db_start = time.time()
    
    # If no products match the criteria, return empty results
    if not filtered_ids:
        logger.warning("No products found matching the filter criteria")
        return {
            'metadatas': [[]],
            'documents': [[]],
            'ids': [[]],
            'distances': [[]],
        }
    
    # Query ChromaDB with specific product IDs
    results = review_collection.query(
        query_texts=[query],
        ids=filtered_ids,
        n_results=min(300, len(filtered_ids))
    )
    db_time = time.time() - db_start
    logger.info(f"Database query completed in {db_time:.4f} seconds")
    
    # Handle case where no results are returned
    if not results or not results['metadatas'] or not results['metadatas'][0]:
        logger.warning("No results found in database query")
        return {
            'metadatas': [[]],
            'documents': [[]],
            'ids': [[]],
            'distances': [[]],
        }
    
    logger.debug(f"Number of results: {len(results['metadatas'][0])}")
    
    filter_start = time.time()
    # Filter out excluded ingredients
    if excluded_ingredients:
        filtered_metadatas = []
        filtered_documents = []
        filtered_ids = []
        filtered_distances = []
        documents = (results.get('documents') or [[]])[0] or []
        metadatas = (results.get('metadatas') or [[]])[0] or []
        ids = (results.get('ids') or [[]])[0] or []
        distances = (results.get('distances') or [[]])[0] or []
        
        for i in range(len(documents)):
            metadata = metadatas[i] if i < len(metadatas) else {}
            # Check if any excluded ingredient appears as a substring in any ingredient tag
            has_excluded_ingredient = False
            for ingredient in excluded_ingredients:
                ingredient_lower = ingredient.lower().strip()
                # Check all metadata keys that start with "ingredienttag:"
                for key in metadata.keys():
                    if key.startswith("ingredienttag:") and ingredient_lower in key.lower():
                        has_excluded_ingredient = True
                        break
                if has_excluded_ingredient:
                    break
            
            if not has_excluded_ingredient:
                filtered_metadatas.append(metadata)
                filtered_documents.append(documents[i] if i < len(documents) else '')
                filtered_ids.append(ids[i] if i < len(ids) else '')
                filtered_distances.append(distances[i] if i < len(distances) else 0.0)
        results = {
            'metadatas': [filtered_metadatas],
            'documents': [filtered_documents],
            'ids': [filtered_ids],
            'distances': [filtered_distances],
        }
    else:
        # Ensure results are always lists of lists for compatibility
        results = {
            'metadatas': [results['metadatas'][0] if results['metadatas'] else []],
            'documents': [results['documents'][0] if results['documents'] else []],
            'ids': [results['ids'][0] if results['ids'] else []],
            'distances': [results['distances'][0] if results['distances'] else []],
        }

    filter_time = time.time() - filter_start
    logger.info(f"Filtering out excluded ingredients completed in {filter_time:.4f} seconds")

    return results


def rank_products(results):
    """Advanced ranking with multiple non-linear scoring strategies and follow-up question generation"""
    start_time = time.time()
    
    # Debug: Count products with reviews and FAQs
    total_products = len(results['metadatas'][0]) if results['metadatas'] and results['metadatas'][0] else 0
    products_with_reviews = 0
    products_with_faqs = 0
    products_with_both = 0
    
    for metadata in results['metadatas'][0]:
        # Check review synthesis content using the flag
        has_review_content = metadata.get('review_synthesis_flag', False)
        
        answered_faqs = metadata.get('answered_faqs', '') or ''
        
        if has_review_content:
            products_with_reviews += 1
        if answered_faqs and answered_faqs.strip():
            products_with_faqs += 1
        if has_review_content and answered_faqs and answered_faqs.strip():
            products_with_both += 1
    
    print(f"\n=== PRODUCT CONTENT STATISTICS ===")
    print(f"Total products: {total_products}")
    if total_products > 0:
        print(f"Products with synthesized reviews: {products_with_reviews} ({products_with_reviews/total_products*100:.1f}%)")
        print(f"Products with answered FAQs: {products_with_faqs} ({products_with_faqs/total_products*100:.1f}%)")
        print(f"Products with both: {products_with_both} ({products_with_both/total_products*100:.1f}%)")
        print(f"Products with neither: {total_products - max(products_with_reviews, products_with_faqs)}")
    else:
        print("No products found in query results")
    print(f"================================\n")
    
    def wilson_score(positive_ratings, total_ratings, confidence=0.95):
        """
        Wilson Score Interval - a more statistically sound way to rank items
        by rating that accounts for uncertainty with fewer reviews
        """
        if total_ratings == 0:
            return 0
        
        z = 1.96  # 95% confidence interval
        phat = positive_ratings / total_ratings
        
        numerator = phat + z*z/(2*total_ratings) - z * math.sqrt((phat*(1-phat)+z*z/(4*total_ratings))/total_ratings)
        denominator = 1 + z*z/total_ratings
        
        return numerator / denominator
    
    def bayesian_rating(rating_avg, rating_count, prior_rating=3.0, prior_count=10):
        """
        Bayesian approach that shrinks ratings toward a prior 
        when there are few reviews
        """
        if rating_count == 0:
            return prior_rating
        
        return (prior_rating * prior_count + rating_avg * rating_count) / (prior_count + rating_count)
    
    def popularity_decay(rating_count, half_life=50):
        """
        Exponential decay function that gives diminishing returns for very popular items
        """
        return 1 - math.exp(-rating_count / half_life)
    
    def content_quality_score(metadata):
        """
        Score based on content quality - synthesized reviews and FAQs
        """
        score = 0.0
        
        # Check review synthesis content using the flag
        has_review_content = metadata.get('review_synthesis_flag', False)
        
        # Synthesized reviews presence bonus (0.3 points for having review content)
        if has_review_content:
            score += 0.3
        
        # FAQ presence bonus (0.2 points for having answered FAQs)
        answered_faqs = metadata.get('answered_faqs', '') or ''
        if answered_faqs and str(answered_faqs).strip():
            score += 0.2
        
        # Additional bonus for having both synthesized reviews and FAQs (0.1 points)
        if has_review_content and answered_faqs and str(answered_faqs).strip():
            score += 0.1
        
        return score

    
    scored_results = []
    for metadata, document, product_id, distance in zip(
        results['metadatas'][0], 
        results['documents'][0], 
        results['ids'][0], 
        results['distances'][0]
    ):
        # Convert to float/number, handling string values
        try:
            rating_avg = float(metadata.get('RATING_AVG', 0) or 2.5)
        except (ValueError, TypeError):
            rating_avg = 2.5
        
        try:
            rating_count = int(metadata.get('RATING_CNT', 0) or 0)
        except (ValueError, TypeError):
            rating_count = 0
        
        # Method 1: Wilson Score (treating 4+ stars as "positive")
        positive_ratings = max(0, (rating_avg - 3) * rating_count / 2)  # Approximate
        wilson = wilson_score(positive_ratings, rating_count)
        
        # Method 2: Bayesian Rating
        bayesian = bayesian_rating(rating_avg, rating_count)
        
        # Method 3: Popularity with decay
        popularity = popularity_decay(rating_count)
        
        # Method 4: Semantic relevance
        relevance = max(0, 1 - distance)
        
        # Method 5: Content quality (synthesized reviews and FAQs presence)
        content_quality = content_quality_score(metadata)
        
        
        # Combine with weights - brand preference gets high priority
        final_score = (
            wilson * 0.1 +
            (bayesian / 5.0) * 0.1 +  # Normalize to 0-1
            popularity * 0.05 +
            relevance * 0.15 +
            content_quality * 0.6
        )
        
        scored_results.append((metadata, document, product_id, distance, final_score))
    
    # Sort by final score
    sorted_results = sorted(scored_results, key=lambda x: -x[4])
    
    # Return without scores for compatibility
    final_results = [(metadata, document, product_id, distance) 
                    for metadata, document, product_id, distance, score in sorted_results]
    print(f"Products ranked with advanced scoring in {time.time() - start_time:.4f} seconds")
    return final_results

# testing
if __name__ == "__main__":
    ingredient_needs = ['Chicken', 'Pumpkin']
    excluded_ingredients = []
    # where_clause = build_where_clause(ingredient_needs)
    # print(where_clause)
    # collection = get_collection()
    # results = collection.query(
    #     query_embeddings=encode_query("dog food"),
    #     n_results=100,
    #     where=where_clause,
    # )
    # print("Results:")
    # for doc, meta in zip(results['documents'], results['metadatas']):
    #     print(f"Document: {doc}, Metadata: {meta}")
    # print(f"Total results found: {len(results['documents'])}")

    start = time.time()
    results1 = query_products("dog food", tuple(ingredient_needs), tuple(excluded_ingredients))
    print(f"Query 1 executed in {time.time() - start:.4f} seconds")
    results2 = query_products("cat food", tuple(ingredient_needs), tuple(excluded_ingredients))
    print(f"Query 2 executed in {time.time() - start:.4f} seconds")
    results3 = query_products("dog food", tuple(ingredient_needs), tuple(excluded_ingredients))
    print(f"Query 3 executed in {time.time() - start:.4f} seconds")
    results4 = query_products("cat food", tuple(ingredient_needs), tuple(excluded_ingredients))
    print(f"Query 4 executed in {time.time() - start:.4f} seconds")
    print(results1 == results3 and results2 == results4)  # Should be True due to caching

    # ranked_products = rank_products(results)
    # print("Ranked Products:")
    # for metadata, document, product_id, distance in ranked_products:
    #     print(f"Product ID: {product_id}, Metadata: {metadata}, Document: {document}, Distance: {distance}")