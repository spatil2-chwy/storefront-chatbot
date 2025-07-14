import chromadb
from functools import lru_cache
import time
import math
import logging
from typing import cast, Any

# Initialize logging first
from src.utils.logging_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

client = chromadb.PersistentClient(path="./../scripts/chroma_db")
# client = chromadb.HttpClient(host='localhost', port=8001)
# PRODUCT_COLLECTION_NAME = "products"
REVIEW_COLLECTION_NAME = "review_synthesis"
# product_collection = client.get_collection(name=PRODUCT_COLLECTION_NAME)
review_collection = client.get_collection(name=REVIEW_COLLECTION_NAME)

def build_where_clause(required_ingredients: list, category_level_1: list, category_level_2: list):
    # build where clause for special diet and ingredients tags
    if len(category_level_1) + len(category_level_2) + len(required_ingredients) == 0:
        where_clause = {}
    elif len(category_level_1) + len(category_level_2) + len(required_ingredients) == 1:
        # if only one special diet or ingredient, use a single condition
        if len(category_level_1) == 1:
            where_clause = {f"categorytag1:{category_level_1[0]}": {"$eq": True}}
        
        elif len(category_level_2) == 1:
            where_clause = {f"categorytag2:{category_level_2[0]}": {"$eq": True}}
        else:
            where_clause = {f"ingredienttag:{required_ingredients[0].lower()}": {"$eq": True}}
    else:
        where_clause = {
            "$and": [
                {
                    f"categorytag1:{category}": {
                            "$eq": True
                        }
                    } for category in category_level_1
                ] + [
                    {
                        f"categorytag2:{category}": {
                            "$eq": True
                        }
                    } for category in category_level_2
            ] + [
                {
                    f"ingredienttag:{ingredient.lower()}": {
                        "$eq": True
                    }
                } for ingredient in required_ingredients
            ]
        }

    return where_clause


@lru_cache(maxsize=128)
def query_products(query: str, required_ingredients=(), excluded_ingredients=(), category_level_1=(), category_level_2=()):
    logger.debug(f"Query cache info: {query_products.cache_info()}")
    start_time = time.time()
    where_clause = build_where_clause(required_ingredients, category_level_1, category_level_2)
    if where_clause == {}:
        where_clause = None
    logger.debug(f"Where clause built in {time.time() - start_time:.4f} seconds") 
    
    query_start = time.time()
    logger.debug(f"Query embedding retrieved in {time.time() - query_start:.4f} seconds")
    
    db_start = time.time()
    results = review_collection.query(
        # query_embeddings=query_embedding,
        query_texts=[query],
        n_results=300,
        where=where_clause,
    )
    
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

    logger.debug(f"Database query completed in {time.time() - db_start:.4f} seconds")
    
    logger.info(f"Total query_products time: {time.time() - start_time:.4f} seconds")
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
        rating_avg = metadata.get('RATING_AVG', 0) or 2.5
        rating_count = metadata.get('RATING_CNT', 0) or 0
        
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