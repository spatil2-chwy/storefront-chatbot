import chromadb
from functools import lru_cache
import time
import math
import json
from openai import OpenAI
from dotenv import load_dotenv
from typing import cast, Any

load_dotenv()

PRODUCT_COLLECTION_NAME = "products"
REVIEW_COLLECTION_NAME = "review_synthesis"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Global variables for lazy initialization
_model = None
_client = None
_product_collection = None
_review_collection = None

# Global product buffer for conversation management
_product_buffer = []
_buffer_query = None
_buffer_filters = None

def get_model():
    """Lazy load and cache the SentenceTransformer model"""
    global _model
    if _model is None:
        start_time = time.time()
        print("Loading SentenceTransformer model...")
        _model = SentenceTransformer(EMBEDDING_MODEL)
        print(f"Model loaded successfully in {time.time() - start_time:.4f} seconds")
    return _model

def get_client():
    """Lazy load and cache the ChromaDB client"""
    global _client
    if _client is None:
        start_time = time.time()
        print("Initializing ChromaDB client...")
        chroma_path = "./../scripts/chroma_db"
        _client = chromadb.PersistentClient(path=chroma_path)
        print(f"ChromaDB client initialized in {time.time() - start_time:.4f} seconds")
    return _client

def get_product_collection():
    """Lazy load and cache the product ChromaDB collection"""
    global _product_collection
    if _product_collection is None:
        start_time = time.time()
        print("Loading product collection...")
        client = get_client()
        _product_collection = client.get_collection(name=PRODUCT_COLLECTION_NAME)
        print(f"Product collection loaded successfully in {time.time() - start_time:.4f} seconds")
    return _product_collection

def get_review_collection():
    """Lazy load and cache the review synthesis ChromaDB collection"""
    global _review_collection
    if _review_collection is None:
        start_time = time.time()
        print("Loading review synthesis collection...")
        client = get_client()
        _review_collection = client.get_collection(name=REVIEW_COLLECTION_NAME)
        print(f"Review synthesis collection loaded successfully in {time.time() - start_time:.4f} seconds")
    return _review_collection


def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set. Please check your .env file.")
    return OpenAI(api_key=api_key)

@lru_cache(maxsize=100)
def encode_query(query: str):
    """Cache query encodings to avoid re-encoding the same queries"""
    start_time = time.time()
    result = get_model().encode([query])
    print(f"Query encoded in {time.time() - start_time:.4f} seconds")
    return result

def get_product_buffer():
    """Get the current product buffer"""
    global _product_buffer
    return _product_buffer.copy()

def set_product_buffer(products, query, filters):
    """Set the product buffer with new products and context"""
    global _product_buffer, _buffer_query, _buffer_filters
    _product_buffer = products
    _buffer_query = query
    _buffer_filters = filters
    print(f"Product buffer updated with {len(products)} products for query: '{query}'")

def clear_product_buffer():
    """Clear the product buffer"""
    global _product_buffer, _buffer_query, _buffer_filters
    _product_buffer = []
    _buffer_query = None
    _buffer_filters = None
    print("Product buffer cleared")

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

def warmup():
    """Pre-load model and collection to avoid cold start delays"""
    print("Warming up search engine...")
    start_time = time.time()
    get_model()
    get_product_collection()
    get_review_collection()
    # Test query to ensure everything is working
    encode_query("test query")
    print(f"Search engine warmed up in {time.time() - start_time:.4f} seconds")

def generate_followup_questions(top_products, user_query, previous_questions=None):
    """
    Generate follow-up questions based on review synthesis of top products
    
    Args:
        top_products: List of top 10 ranked products with metadata
        user_query: Original user query
        previous_questions: List of previously asked questions (for follow-up mode)
    
    Returns:
        str: Generated follow-up questions
    """
    if not top_products or len(top_products) == 0:
        return "These look like great options based on the reviews — go with what fits your style or budget!"
    
    # Extract review synthesis from top 10 products
    review_data = []
    for i, (metadata, document, product_id, distance) in enumerate(top_products[:10]):
        try:
            # Parse review synthesis
            review_synthesis_json = metadata.get('review_synthesis', '{}')
            review_data_parsed = json.loads(review_synthesis_json)
            
            # Extract what customers love and what to watch out for
            what_customers_love = review_data_parsed.get('what_customers_love', [])
            what_to_watch_out_for = review_data_parsed.get('what_to_watch_out_for', [])
            
            # Convert lists to strings
            love_str = ' '.join(what_customers_love) if isinstance(what_customers_love, list) else str(what_customers_love)
            watch_str = ' '.join(what_to_watch_out_for) if isinstance(what_to_watch_out_for, list) else str(what_to_watch_out_for)
            
            product_name = metadata.get('CLEAN_NAME', f'Product {product_id}')
            
            review_data.append({
                'product_name': product_name,
                'what_customers_love': love_str,
                'what_to_watch_out_for': watch_str,
            })
        except Exception as e:
            print(f"Error parsing review synthesis for product {product_id}: {e}")
            continue
    
    if not review_data:
        return "These look like great options based on the reviews — go with what fits your style or budget!"
    
    # Create prompt for follow-up questions
    previous_questions_str = ""
    if previous_questions:
        previous_questions_str = f"\nPreviously Asked Questions: {', '.join(previous_questions)}"
    
    reviews_text = "\n\n".join([
        f"Product: {item['product_name']}\n"
        f"What customers love: {item['what_customers_love']}\n"
        f"What to watch out for: {item['what_to_watch_out_for']}\n"

        for item in review_data
    ])
    
    prompt = f"""You're a friendly but efficient Chewy assistant helping a pet parent decide between products based on real customer reviews.

Your job is to surface quick, review-based clarifications that help the pet parent choose what's best for their situation.

Instructions:
- Carefully read the review theme synthesis to identify product trade-offs, standout features, or pain points across products.
- Ask 1-3 short, highly specific follow-up questions or make short statements that help the user narrow their choice. Do not repeat already answered or previously asked questions.
- Only include questions if there's real ambiguity or a decision to make. Don't ask generic questions.
- If one product clearly stands out for a specific use case, you can make a helpful statement instead of asking a question.
- If all reviews are overwhelmingly positive and there are no key differentiators or concerns, say: "These look like great options based on the reviews — go with what fits your style or budget!"

You're not being chatty — you're being helpful, warm, and efficient.

User Query: {user_query}
Product Reviews: {reviews_text}
Previous Questions: {previous_questions_str}

Output Format:
Sure! Just a couple of questions to help you out:
- [question or statement 1]
- [question or statement 2]
(etc.)
- or just a statement if nothing to add, if there's no constructive follow up questions to ask."""

    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a helpful Chewy assistant that generates follow-up questions based on product reviews."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.2
        )
        
        content = response.choices[0].message.content
        if content is None:
            content = ""
        followup_questions = content.strip()
        print(f"Generated follow-up questions: {followup_questions}")
        return followup_questions
        
    except Exception as e:
        print(f"Error generating follow-up questions: {e}")
        return "These look like great options based on the reviews — go with what fits your style or budget!"

def query_products(query: str, required_ingredients: list, excluded_ingredients: list, special_diet_tags: list):
    """Initial product search - returns products and stores top 300 in buffer"""
    start_time = time.time()
    where_clause = build_where_clause(required_ingredients, special_diet_tags)
    if where_clause == {}:
        where_clause = None
    print(f"Where clause built in {time.time() - start_time:.4f} seconds") 
    
    collection = get_product_collection()
    query_start = time.time()
    query_embedding = encode_query(query)
    print(f"Query embedding retrieved in {time.time() - query_start:.4f} seconds")
    
    db_start = time.time()
    results = collection.query(
        # query_embeddings=query_embedding,
        query_texts=[query],
        n_results=300,
        where=cast(Any, where_clause),
    )
    
    # Handle case where no results are returned
    if not results or not results['metadatas'] or not results['metadatas'][0]:
        print("No results found in database query")
        return {
            'metadatas': [[]],
            'documents': [[]],
            'ids': [[]],
            'distances': [[]],
        }
    
    # Filter out excluded ingredients
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
    
    # Store the top 300 products in the buffer for follow-up queries
    buffer_products = []
    for i in range(len(results['metadatas'][0])):
        buffer_products.append((
            results['metadatas'][0][i],
            results['documents'][0][i],
            results['ids'][0][i],
            results['distances'][0][i]
        ))
    
    # Store buffer with context
    filters = {
        'required_ingredients': required_ingredients,
        'excluded_ingredients': excluded_ingredients,
        'special_diet_tags': special_diet_tags
    }
    set_product_buffer(buffer_products, query, filters)
    
    print(f"Total query_products time: {time.time() - start_time:.4f} seconds")
    return results

def query_products_with_followup(query: str, required_ingredients: list, excluded_ingredients: list, special_diet_tags: list, previous_products: list):
    """
    Follow-up product search - re-ranks previous products based on user's follow-up response
    
    Args:
        query: User's follow-up response/refinement
        required_ingredients: Required ingredients filter
        excluded_ingredients: Excluded ingredients filter  
        special_diet_tags: Special diet tags filter
        previous_products: List of previous products to re-rank (from search_products)
    """
    start_time = time.time()
    print(f"Starting follow-up search for: '{query}' with {len(previous_products)} previous products")
    
    if not previous_products:
        print("No previous products provided, falling back to regular search")
        return query_products(query, required_ingredients, excluded_ingredients, special_diet_tags)
    
    # Get the review synthesis collection for semantic similarity
    try:
        review_collection = get_review_collection()
        
        # Create embedding for the follow-up query
        query_embedding = encode_query(query)
        
        # Get product IDs from previous products
        previous_product_ids = [str(product[2]) for product in previous_products]  # product_id is at index 2
        
        where_clause = build_where_clause(required_ingredients, special_diet_tags)
        if where_clause == {}:
            where_clause = None
        # Query the review synthesis collection for these specific products
        # We'll use the review collection to get semantic similarity scores
        review_results = review_collection.query(
            query_embeddings=query_embedding,
            n_results=len(previous_product_ids),
            where=cast(Any, where_clause)
        )

        # Handle case where no results are returned
        if not review_results or not review_results['metadatas'] or not review_results['metadatas'][0]:
            print("No results found in review synthesis query")
            return query_products(query, required_ingredients, excluded_ingredients, special_diet_tags)
        
        # Filter out excluded ingredients
        if excluded_ingredients:
            filtered_metadatas = []
            filtered_documents = []
            filtered_ids = []
            filtered_distances = []
            for i in range(len(review_results['documents'][0])):
                metadata = review_results['metadatas'][0][i]
                if not any(f"ingredienttag:{ingredient}" in metadata for ingredient in excluded_ingredients):
                    filtered_metadatas.append(metadata)
                    filtered_documents.append(review_results['documents'][0][i])
                    filtered_ids.append(review_results['ids'][0][i])
                    filtered_distances.append(review_results['distances'][0][i])
            review_results = {
                'metadatas': [filtered_metadatas],
                'documents': [filtered_documents],
                'ids': [filtered_ids],
                'distances': [filtered_distances],
            }

        else:
            review_results = {
                'metadatas': [review_results['metadatas'][0] if review_results['metadatas'] else []],
                'documents': [review_results['documents'][0] if review_results['documents'] else []],
                'ids': [review_results['ids'][0] if review_results['ids'] else []],
                'distances': [review_results['distances'][0] if review_results['distances'] else []],
            }

        # Create a mapping of product_id to distance for re-ranking
        distance_map = {}
        for i, product_id in enumerate(review_results['ids'][0]):
            distance = review_results['distances'][0][i]
            distance_map[product_id] = distance
        
        # Re-rank previous products based on new distances from review collection
        reranked_products = []
        for metadata, document, product_id, old_distance in previous_products:
            new_distance = distance_map.get(str(product_id), old_distance)
            reranked_products.append((metadata, document, product_id, new_distance))
        
        # Sort by new distance (lower is better)
        reranked_products.sort(key=lambda x: x[3])
        
        # Update the product buffer with re-ranked products
        filters = {
            'required_ingredients': required_ingredients,
            'excluded_ingredients': excluded_ingredients,
            'special_diet_tags': special_diet_tags
        }
        set_product_buffer(reranked_products, query, filters)
        
        # Convert back to the expected format
        results = {
            'metadatas': [[p[0] for p in reranked_products]],
            'documents': [[p[1] for p in reranked_products]],
            'ids': [[p[2] for p in reranked_products]],
            'distances': [[p[3] for p in reranked_products]],
        }
        
        print(f"Follow-up search completed in {time.time() - start_time:.4f} seconds")
        return results
        
    except Exception as e:
        print(f"Error in follow-up search: {e}, falling back to regular search")
        return query_products(query, required_ingredients, excluded_ingredients, special_diet_tags)

def rank_products(results, user_query=None, previous_questions=None):
    """Advanced ranking with multiple non-linear scoring strategies and follow-up question generation"""
    start_time = time.time()
    
    # Debug: Count products with reviews and FAQs
    total_products = len(results['metadatas'][0]) if results['metadatas'] and results['metadatas'][0] else 0
    products_with_reviews = 0
    products_with_faqs = 0
    products_with_both = 0
    
    for metadata in results['metadatas'][0]:
        # Check review synthesis flag and parse JSON content
        review_synthesis_flag = metadata.get('review_synthesis_flag', False)
        review_synthesis_json = metadata.get('review_synthesis', '{}')
        
        # Parse review synthesis JSON to check for actual content
        try:
            review_data = json.loads(review_synthesis_json)
            has_review_content = (
                review_synthesis_flag and 
                review_data.get('should_you_buy_it', '') != "Insufficient reviews! No review synthesis"
            )
        except:
            has_review_content = review_synthesis_flag
        
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
        
        # Check review synthesis flag and parse JSON content
        review_synthesis_flag = metadata.get('review_synthesis_flag', False)
        review_synthesis_json = metadata.get('review_synthesis', '{}')
        
        # Parse review synthesis JSON to check for actual content
        try:
            review_data = json.loads(review_synthesis_json)
            has_review_content = (
                review_synthesis_flag and 
                review_data.get('should_you_buy_it', '') != "Insufficient reviews! No review synthesis"
            )
        except:
            has_review_content = review_synthesis_flag
        
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
        
        # Combine with weights - maximum priority to content quality
        final_score = (
            wilson * 0.1 +
            (bayesian / 5.0) * 0.1 +  # Normalize to 0-1
            popularity * 0.05 +
            relevance * 0.15 +
            content_quality * 0.6  # Maximum weight for content quality
        )
        
        scored_results.append((metadata, document, product_id, distance, final_score))
    
    # Sort by final score
    sorted_results = sorted(scored_results, key=lambda x: -x[4])
    
    # Return without scores for compatibility
    final_results = [(metadata, document, product_id, distance) 
                    for metadata, document, product_id, distance, score in sorted_results]

    # get top 10
    top_10_results = final_results[:10]
    
    print(f"Products ranked with advanced scoring in {time.time() - start_time:.4f} seconds")
    
    # Generate follow-up questions based on top 10 products
    followup_questions = None
    if user_query and len(top_10_results) > 0:
        followup_start = time.time()
        followup_questions = generate_followup_questions(top_10_results, user_query, previous_questions)
        print(f"Follow-up questions generated in {time.time() - followup_start:.4f} seconds")
    
    # Return both products and follow-up questions
    return final_results, followup_questions

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
