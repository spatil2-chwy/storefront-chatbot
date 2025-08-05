from sqlalchemy.orm import Session
from src.services.interaction_service import interaction_svc
from typing import List, Dict, Any
from datetime import datetime, timedelta
import statistics


class InteractionProcessor:
    def __init__(self):
        pass

    def process_user_interactions(self, db: Session, customer_key: int, hours_back: int = 24, minutes_back: int = 0) -> Dict[str, Any]:
        """Process raw interactions into structured summaries for persona updates"""
        
        # Get raw interactions
        raw_interactions = interaction_svc.get_interaction_history(db, customer_key, hours_back, minutes_back)
        
        if not raw_interactions:
            return None
        
        # Process into structured format
        processed_data = self._process_interactions(raw_interactions)
        
        return processed_data

    def _process_interactions(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process raw interactions into structured summaries"""
        
        # Extract product metadata for analysis
        enriched_interactions = []
        for interaction in interactions:
            metadata = interaction.get('product_metadata', {})
            enriched_interactions.append({
                'event_type': interaction['event_type'],
                'event_value': interaction['event_value'],
                'timestamp': interaction['timestamp'],
                'price': metadata.get('price', 0),
                'category_level_1': metadata.get('category_level_1', ''),
                'category_level_2': metadata.get('category_level_2', ''),
                'brand': metadata.get('brand', ''),
                'title': metadata.get('title', ''),
                'keywords': metadata.get('keywords', [])
            })

        # Calculate summary statistics
        summary = self._calculate_summary_stats(enriched_interactions)
        
        # Get top categories
        top_categories = self._get_top_categories(enriched_interactions)
        
        # Get top brands
        top_brands = self._get_top_brands(enriched_interactions)
        
        # Get recent purchases
        recent_purchases = self._get_recent_purchases(enriched_interactions)
        
        return {
            'summary': summary,
            'top_categories': top_categories,
            'top_brands': top_brands,
            'recent_purchases': recent_purchases
        }

    def _calculate_summary_stats(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics from interactions"""
        
        total_events = len(interactions)
        purchases = sum(1 for i in interactions if i['event_type'] == 'purchase')
        carts = sum(1 for i in interactions if i['event_type'] == 'addToCart')
        clicks = sum(1 for i in interactions if i['event_type'] == 'productClick')
        
        # Price analysis
        prices = [i['price'] for i in interactions if i['price'] and i['price'] > 0]
        avg_price_overall = statistics.mean(prices) if prices else 0
        price_stddev = statistics.stdev(prices) if len(prices) > 1 else 0
        
        # Price buckets
        low_price_count = sum(1 for p in prices if p < 30)
        mid_price_count = sum(1 for p in prices if 30 <= p <= 70)
        high_price_count = sum(1 for p in prices if p > 70)
        
        # Weighted average price (weighted by event value)
        weighted_prices = [(i['price'] * (i['event_value'] or 1)) for i in interactions if i['price'] and i['price'] > 0]
        weighted_avg_price = statistics.mean(weighted_prices) if weighted_prices else 0
        
        return {
            'total_events': total_events,
            'purchases': purchases,
            'carts': carts,
            'clicks': clicks,
            'conversion_rate': round(purchases / total_events, 2) if total_events > 0 else 0,
            'weighted_avg_price': round(weighted_avg_price, 2),
            'avg_price_overall': round(avg_price_overall, 2),
            'price_stddev': round(price_stddev, 2),
            'price_bucket_counts': {
                'low': low_price_count,
                'mid': mid_price_count,
                'high': high_price_count
            }
        }

    def _get_top_categories(self, interactions: List[Dict[str, Any]], limit: int = 3) -> List[Dict[str, Any]]:
        """Get top categories by spend"""
        
        category_stats = {}
        
        for interaction in interactions:
            category = interaction.get('category_level_2') or interaction.get('category_level_1', 'Unknown')
            if not category:
                continue
                
            if category not in category_stats:
                category_stats[category] = {
                    'total_events': 0,
                    'purchases': 0,
                    'total_spend': 0,
                    'prices': []
                }
            
            stats = category_stats[category]
            stats['total_events'] += 1
            
            if interaction['event_type'] == 'purchase':
                stats['purchases'] += 1
                spend = interaction['price'] * (interaction['event_value'] or 1)
                stats['total_spend'] += spend
            
            if interaction['price']:
                stats['prices'].append(interaction['price'])
        
        # Convert to list and sort by total spend
        categories = []
        for category, stats in category_stats.items():
            avg_price = statistics.mean(stats['prices']) if stats['prices'] else 0
            purchase_ratio = stats['purchases'] / stats['total_events'] if stats['total_events'] > 0 else 0
            
            categories.append({
                'category': category,
                'purchase_ratio': round(purchase_ratio, 2),
                'avg_price': round(avg_price, 2),
                'total_spend': round(stats['total_spend'], 2),
                'total_events': stats['total_events']
            })
        
        # Sort by total spend and return top N
        categories.sort(key=lambda x: x['total_spend'], reverse=True)
        return categories[:limit]

    def _get_top_brands(self, interactions: List[Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
        """Get top brands by spend"""
        
        brand_stats = {}
        
        for interaction in interactions:
            brand = interaction.get('brand', 'Unknown')
            if not brand:
                continue
                
            if brand not in brand_stats:
                brand_stats[brand] = {
                    'total_events': 0,
                    'purchases': 0,
                    'total_spend': 0
                }
            
            stats = brand_stats[brand]
            stats['total_events'] += 1
            
            if interaction['event_type'] == 'purchase':
                stats['purchases'] += 1
                spend = interaction['price'] * (interaction['event_value'] or 1)
                stats['total_spend'] += spend
        
        # Convert to list and sort by total spend
        brands = []
        for brand, stats in brand_stats.items():
            loyalty_score = stats['purchases'] / stats['total_events'] if stats['total_events'] > 0 else 0
            
            brands.append({
                'brand': brand,
                'loyalty_score': round(loyalty_score, 2),
                'total_purchases': stats['purchases'],
                'total_spend': round(stats['total_spend'], 2)
            })
        
        # Sort by total spend and return top N
        brands.sort(key=lambda x: x['total_spend'], reverse=True)
        return brands[:limit]

    def _get_recent_purchases(self, interactions: List[Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent purchases with metadata"""
        
        purchases = []
        for interaction in interactions:
            if interaction['event_type'] == 'purchase':
                purchases.append({
                    'name': interaction.get('title', 'Unknown Product'),
                    'category': interaction.get('category_level_2') or interaction.get('category_level_1', 'Unknown'),
                    'brand': interaction.get('brand', 'Unknown'),
                    'diet': self._extract_diet_info(interaction.get('keywords', [])),
                    'price': round(interaction['price'], 2) if interaction['price'] else 0,
                    'times_bought': int(interaction.get('event_value', 1))
                })
        
        # Sort by timestamp (most recent first) and return top N
        purchases.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return purchases[:limit]

    def _extract_diet_info(self, keywords: List[str]) -> str:
        """Extract diet information from keywords"""
        diet_keywords = ['grain-free', 'organic', 'natural', 'limited ingredient', 'hypoallergenic', 'senior', 'puppy', 'kitten']
        found_diets = [kw for kw in keywords if any(diet in kw.lower() for diet in diet_keywords)]
        return ', '.join(found_diets) if found_diets else None


# Create singleton instance
interaction_processor = InteractionProcessor() 