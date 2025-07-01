import chromadb
from functools import lru_cache
import time
import math

COLLECTION_NAME = "products"
# EMBEDDING_MODEL = "all-MiniLM-L6-v2"


client = chromadb.PersistentClient(path="./../scripts/chroma_db")
collection = client.get_collection(name=COLLECTION_NAME)


def build_where_clause(required_ingredients: list, special_diet_tags: list):
    # build where clause for special diet and ingredients tags
    if len(special_diet_tags) + len(required_ingredients) == 0:
        where_clause = {}
    elif len(special_diet_tags) + len(required_ingredients) == 1:
        # if only one special diet or ingredient, use a single condition
        if len(special_diet_tags) == 1:
            where_clause = {f"specialdiettag:{special_diet_tags[0]}": {"$eq": True}}
        else:
            where_clause = {f"ingredienttag:{required_ingredients[0]}": {"$eq": True}}
    else:
        where_clause = {
            "$and": [
                {
                    f"specialdiettag:{diet}": {
                        "$eq": True
                    }
                } for diet in special_diet_tags
            ] + [
                {
                    f"ingredienttag:{ingredient}": {
                        "$eq": True
                    }
                } for ingredient in required_ingredients
            ] 
        }

    return where_clause


# def query_products(query: str, required_ingredients: list, excluded_ingredients: list, special_diet_tags: list):
#     start_time = time.time()
#     where_clause = build_where_clause(required_ingredients, special_diet_tags)
#     if where_clause == {}:
#         where_clause = None
#     print(f"Where clause built in {time.time() - start_time:.4f} seconds") 
    
#     db_start = time.time()
#     results = collection.query(
#         # query_embeddings=query_embedding,
#         query_texts=[query],
#         n_results=300,
#         where=where_clause,
#     )
#     # make sure products do not have excluded ingredients by checking if they are in the metadata
#     if excluded_ingredients:
#         filtered_metadatas = []
#         filtered_documents = []
#         filtered_ids = []
#         filtered_distances = []
#         for i in range(len(results['documents'][0])):
#             metadata = results['metadatas'][0][i]
#             if not any(f"ingredienttag:{ingredient}" in metadata for ingredient in excluded_ingredients):
#                 filtered_metadatas.append(metadata)
#                 filtered_documents.append(results['documents'][0][i])
#                 filtered_ids.append(results['ids'][0][i])
#                 filtered_distances.append(results['distances'][0][i])
#         results = {
#             'metadatas': [filtered_metadatas],
#             'documents': [filtered_documents],
#             'ids': [filtered_ids],
#             'distances': [filtered_distances],
#         }
#     else:
#         # Ensure results are always lists of lists for compatibility
#         results = {
#             'metadatas': [results['metadatas'][0] if results['metadatas'] else []],
#             'documents': [results['documents'][0] if results['documents'] else []],
#             'ids': [results['ids'][0] if results['ids'] else []],
#             'distances': [results['distances'][0] if results['distances'] else []],
#         }

#     print(f"Database query completed in {time.time() - db_start:.4f} seconds")
#     print(f"Total query_products time: {time.time() - start_time:.4f} seconds")
#     return results

@lru_cache(maxsize=128)
def query_products(query: str, required_ingredients: tuple, excluded_ingredients: tuple, special_diet_tags: tuple):
    print(query_products.cache_info())
    start_time = time.time()
    where_clause = build_where_clause(required_ingredients, special_diet_tags)
    if where_clause == {}:
        where_clause = None
    print(f"Where clause built in {time.time() - start_time:.4f} seconds") 
    
    db_start = time.time()
    results = collection.query(
        # query_embeddings=query_embedding,
        query_texts=[query],
        n_results=300,
        where=where_clause,
    )
    # make sure products do not have excluded ingredients by checking if they are in the metadata
    if excluded_ingredients:
        filtered_metadatas = []
        filtered_documents = []
        filtered_ids = []
        filtered_distances = []
        for i in range(len(results['documents'][0])):
            metadata = results['metadatas'][0][i]
            if not any(f"ingredienttag:{ingredient}" in metadata for ingredient in excluded_ingredients):
                filtered_metadatas.append(metadata)
                filtered_documents.append(results['documents'][0][i])
                filtered_ids.append(results['ids'][0][i])
                filtered_distances.append(results['distances'][0][i])
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

    print(f"Database query completed in {time.time() - db_start:.4f} seconds")
    print(f"Total query_products time: {time.time() - start_time:.4f} seconds")
    return results

def rank_products(results):
    """Rank products by rating average and count"""
    start_time = time.time()
    # for now we can rank like this:
    sorted_results = sorted(
        zip(results['metadatas'][0], results['documents'][0], results['ids'][0], results['distances'][0]),
        key=lambda x: (-x[0].get('RATING_CNT', 0), -x[0].get('RATING_AVG', 0))
    )
    print(f"Products ranked in {time.time() - start_time:.4f} seconds")
    return sorted_results

def rank_products(results):
    """Advanced ranking with multiple non-linear scoring strategies"""
    start_time = time.time()
    
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
        
        # Combine with weights - you can adjust these
        final_score = (
            wilson * 0.3 +
            (bayesian / 5.0) * 0.3 +  # Normalize to 0-1
            popularity * 0.2 +
            relevance * 0.2
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
    special_diet_needs = []
    ingredient_needs = ['Chicken', 'Pumpkin']
    excluded_ingredients = []
    # where_clause = build_where_clause(ingredient_needs, special_diet_needs)
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
    results1 = query_products("dog food", tuple(ingredient_needs), tuple(excluded_ingredients), tuple(special_diet_needs))
    print(f"Query 1 executed in {time.time() - start:.4f} seconds")
    results2 = query_products("cat food", tuple(ingredient_needs), tuple(excluded_ingredients), tuple(special_diet_needs))
    print(f"Query 2 executed in {time.time() - start:.4f} seconds")
    results3 = query_products("dog food", tuple(ingredient_needs), tuple(excluded_ingredients), tuple(special_diet_needs))
    print(f"Query 3 executed in {time.time() - start:.4f} seconds")
    results4 = query_products("cat food", tuple(ingredient_needs), tuple(excluded_ingredients), tuple(special_diet_needs))
    print(f"Query 4 executed in {time.time() - start:.4f} seconds")
    print(results1 == results3 and results2 == results4)  # Should be True due to caching

    # ranked_products = rank_products(results)
    # print("Ranked Products:")
    # for metadata, document, product_id, distance in ranked_products:
    #     print(f"Product ID: {product_id}, Metadata: {metadata}, Document: {document}, Distance: {distance}")
