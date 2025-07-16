import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
import statistics
from collections import defaultdict, Counter
from data_parser import EvaluationDataParser

logger = logging.getLogger(__name__)

@dataclass
class QuantitativeMetrics:
    """Quantitative metrics that can be calculated without LLM"""
    
    # Performance Metrics
    avg_total_processing_time: float
    avg_product_search_time: float
    avg_llm_response_time: float
    avg_function_call_time: float
    avg_ranking_time: float
    
    # Success Metrics
    success_rate: float  # Percentage of queries without errors
    error_rate: float
    
    # Query Analysis
    avg_query_length: float
    most_common_tools: List[str]
    tool_usage_distribution: Dict[str, float]
    
    # Product Analysis
    brand_diversity: float  # Number of unique brands / total products
    price_range: Dict[str, float]
    rating_distribution: Dict[str, int]
    
    # Performance Bottlenecks
    slow_queries_percentage: float  # Queries taking >10s
    very_slow_queries_percentage: float  # Queries taking >20s

class QuantitativeEvaluator:
    """Evaluator for quantitative metrics that don't require LLM"""
    
    def __init__(self):
        self.metrics = {}
    
    def evaluate_single_log(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single log file for quantitative metrics"""
        
        metrics = {}
        
        # Performance metrics
        metrics['total_processing_time'] = log_data.get('total_processing_time', 0)
        metrics['product_search_time'] = log_data.get('product_search_time', 0)
        metrics['llm_response_time'] = log_data.get('llm_response_time', 0)
        metrics['function_call_time'] = log_data.get('function_call_time', 0)
        metrics['ranking_time'] = log_data.get('ranking_time', 0)
        
        # Success metrics
        metrics['has_errors'] = len(log_data.get('errors', [])) > 0
        metrics['products_returned'] = len(log_data.get('product_results', []))
        
        # Query analysis
        metrics['query_length'] = len(log_data.get('raw_user_query', ''))
        metrics['has_user_context'] = bool(log_data.get('user_context'))
        metrics['context_length'] = len(log_data.get('user_context', ''))
        
        # Tool analysis
        metrics['tools_used'] = [tool.get('tool_name') for tool in log_data.get('tool_calls', [])]
        
        # Product analysis
        products = log_data.get('product_results', [])
        if products:
            metrics['avg_product_rating'] = statistics.mean([p.get('rating', 0) for p in products if p.get('rating')])
            metrics['avg_product_price'] = statistics.mean([p.get('price', 0) for p in products if p.get('price')])
            metrics['unique_brands'] = len(set(p.get('brand') for p in products if p.get('brand')))
            metrics['brand_diversity'] = metrics['unique_brands'] / len(products)
        else:
            metrics['avg_product_rating'] = 0
            metrics['avg_product_price'] = 0
            metrics['unique_brands'] = 0
            metrics['brand_diversity'] = 0
        
        return metrics
    
    def evaluate_all_logs(self, log_dir: str = "logs/logs") -> QuantitativeMetrics:
        """Evaluate all logs and return aggregate metrics"""
        
        log_path = Path(log_dir)
        if not log_path.exists():
            logger.error(f"Log directory {log_dir} does not exist")
            return self._create_empty_metrics()
        
        all_metrics = []
        tool_counter = Counter()
        
        # Process all evaluation logs
        parser = EvaluationDataParser()
        for log_file in log_path.glob("eval_*.json"):
            try:
                log_data = parser.load_eval_data(str(log_file))
                
                metrics = self.evaluate_single_log(log_data)
                all_metrics.append(metrics)
                
                # Count tool usage
                for tool in metrics.get('tools_used', []):
                    tool_counter[tool] += 1
                
            except Exception as e:
                logger.error(f"Error evaluating {log_file.name}: {e}")
        
        if not all_metrics:
            return self._create_empty_metrics()
        
        # Calculate aggregate metrics
        return self._calculate_aggregate_metrics(all_metrics, tool_counter)
    
    def _calculate_aggregate_metrics(self, all_metrics: List[Dict[str, Any]], tool_counter: Counter) -> QuantitativeMetrics:
        """Calculate aggregate metrics from individual log metrics"""
        
        # Performance metrics
        total_times = [m.get('total_processing_time', 0) for m in all_metrics]
        search_times = [m.get('product_search_time', 0) for m in all_metrics]
        llm_times = [m.get('llm_response_time', 0) for m in all_metrics]
        function_times = [m.get('function_call_time', 0) for m in all_metrics]
        ranking_times = [m.get('ranking_time', 0) for m in all_metrics]
        
        # Success metrics
        error_count = sum(1 for m in all_metrics if m.get('has_errors', False))
        success_rate = (len(all_metrics) - error_count) / len(all_metrics) * 100

        product_prices = [m.get('avg_product_price', 0) for m in all_metrics if m.get('avg_product_price', 0) > 0]
 
        # Query analysis
        query_lengths = [m.get('query_length', 0) for m in all_metrics]
        avg_query_length = statistics.mean(query_lengths) if query_lengths else 0
        
        # Tool analysis
        total_queries = len(all_metrics)
        tool_usage_distribution = {tool: (count / total_queries) * 100 for tool, count in tool_counter.items()}
        most_common_tools = [tool for tool, _ in tool_counter.most_common(5)]
        
        # Performance bottlenecks
        slow_queries = sum(1 for t in total_times if t > 10)
        very_slow_queries = sum(1 for t in total_times if t > 20)
        slow_queries_percentage = (slow_queries / len(total_times)) * 100 if total_times else 0
        very_slow_queries_percentage = (very_slow_queries / len(total_times)) * 100 if total_times else 0
        
        return QuantitativeMetrics(
            avg_total_processing_time=statistics.mean(total_times) if total_times else 0,
            avg_product_search_time=statistics.mean(search_times) if search_times else 0,
            avg_llm_response_time=statistics.mean(llm_times) if llm_times else 0,
            avg_function_call_time=statistics.mean(function_times) if function_times else 0,
            avg_ranking_time=statistics.mean(ranking_times) if ranking_times else 0,
            success_rate=success_rate,
            error_rate=100 - success_rate,
            avg_query_length=avg_query_length,
            most_common_tools=most_common_tools,
            tool_usage_distribution=tool_usage_distribution,
            brand_diversity=statistics.mean([m.get('brand_diversity', 0) for m in all_metrics]),
            price_range={
                'min': min(product_prices) if product_prices else 0,
                'max': max(product_prices) if product_prices else 0
            },
            rating_distribution=self._calculate_rating_distribution(all_metrics),
            slow_queries_percentage=slow_queries_percentage,
            very_slow_queries_percentage=very_slow_queries_percentage
        )
    
    def _calculate_rating_distribution(self, all_metrics: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate distribution of product ratings"""
        rating_ranges = {
            '1-2': 0,
            '2-3': 0,
            '3-4': 0,
            '4-5': 0
        }
        
        for metrics in all_metrics:
            rating = metrics.get('avg_product_rating', 0)
            if 1 <= rating < 2:
                rating_ranges['1-2'] += 1
            elif 2 <= rating < 3:
                rating_ranges['2-3'] += 1
            elif 3 <= rating < 4:
                rating_ranges['3-4'] += 1
            elif 4 <= rating <= 5:
                rating_ranges['4-5'] += 1
        
        return rating_ranges
    
    def _create_empty_metrics(self) -> QuantitativeMetrics:
        """Create empty metrics when no logs are available"""
        return QuantitativeMetrics(
            avg_total_processing_time=0,
            avg_product_search_time=0,
            avg_llm_response_time=0,
            avg_function_call_time=0,
            avg_ranking_time=0,
            success_rate=0,
            error_rate=0,
            avg_query_length=0,
            most_common_tools=[],
            tool_usage_distribution={},
            brand_diversity=0,
            price_range={'min': 0, 'max': 0},
            rating_distribution={},
            slow_queries_percentage=0,
            very_slow_queries_percentage=0
        )
    

def generate_performance_report(log_dir: str = "logs/logs") -> Dict[str, Any]:
    """Generate a comprehensive performance report"""
    
    evaluator = QuantitativeEvaluator()
    metrics = evaluator.evaluate_all_logs(log_dir)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "metrics": asdict(metrics),
        "recommendations": generate_recommendations(metrics)
    }
    
    return report

def generate_recommendations(metrics: QuantitativeMetrics) -> List[str]:
    """Generate recommendations based on metrics"""
    
    recommendations = []
    
    # Performance recommendations
    if metrics.avg_total_processing_time > 15:
        recommendations.append("🚨 Critical: Average response time exceeds 15 seconds. Consider optimizing database queries and implementing caching.")
    
    if metrics.avg_product_search_time > 10:
        recommendations.append("⚠️ Warning: Product search is taking too long. Optimize database indexing and consider query caching.")
    
    if metrics.slow_queries_percentage > 20:
        recommendations.append("⚠️ Warning: More than 20% of queries are slow (>10s). Investigate performance bottlenecks.")
    
    if metrics.error_rate > 5:
        recommendations.append("🚨 Critical: Error rate exceeds 5%. Review error logs and fix underlying issues.")
    
    # Quality recommendations
    if metrics.brand_diversity < 0.3:
        recommendations.append("💡 Consider: Low brand diversity in results. Review ranking algorithm to ensure variety.")
    
    # Usage recommendations
    if not metrics.most_common_tools:
        recommendations.append("💡 Consider: No tool usage detected. Review tool selection logic.")
    
    return recommendations

if __name__ == "__main__":
    # Generate and save performance report
    report = generate_performance_report()
    
    output_dir = "logs/quantitative_reports"
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_file = f"{output_dir}/quantitative_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"Quantitative report generated: {output_file}")
    print(f"Success rate: {report['metrics']['success_rate']:.1f}%")
    print(f"Average response time: {report['metrics']['avg_total_processing_time']:.2f}s")
    
    if report['recommendations']:
        print("\nRecommendations:")
        for rec in report['recommendations']:
            print(f"  {rec}") 