import time
import logging
from typing import Dict, List, Optional
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    operation: str
    duration: float
    timestamp: datetime
    details: Optional[Dict] = None

class PerformanceMonitor:
    def __init__(self, max_metrics: int = 1000):
        self.metrics: deque = deque(maxlen=max_metrics)
        self.operation_stats: Dict[str, List[float]] = defaultdict(list)
        
    def record(self, operation: str, duration: float, details: Optional[Dict] = None):
        """Record a performance metric"""
        metric = PerformanceMetric(
            operation=operation,
            duration=duration,
            timestamp=datetime.now(),
            details=details
        )
        self.metrics.append(metric)
        self.operation_stats[operation].append(duration)
        
        # Keep only last 100 measurements per operation
        if len(self.operation_stats[operation]) > 100:
            self.operation_stats[operation] = self.operation_stats[operation][-100:]
    
    def get_stats(self, operation: str) -> Dict:
        """Get statistics for a specific operation"""
        durations = self.operation_stats.get(operation, [])
        if not durations:
            return {}
        
        return {
            'count': len(durations),
            'avg': sum(durations) / len(durations),
            'min': min(durations),
            'max': max(durations),
            'p95': sorted(durations)[int(len(durations) * 0.95)],
            'p99': sorted(durations)[int(len(durations) * 0.99)],
        }
    
    def get_slow_operations(self, threshold: float = 5.0) -> List[Dict]:
        """Get operations that are consistently slow"""
        slow_ops = []
        for operation, durations in self.operation_stats.items():
            if len(durations) < 5:  # Need at least 5 measurements
                continue
                
            avg_duration = sum(durations) / len(durations)
            if avg_duration > threshold:
                slow_ops.append({
                    'operation': operation,
                    'avg_duration': avg_duration,
                    'count': len(durations),
                    'max_duration': max(durations),
                })
        
        return sorted(slow_ops, key=lambda x: x['avg_duration'], reverse=True)
    
    def print_summary(self):
        """Print a performance summary"""
        logger.info("📊 PERFORMANCE SUMMARY")
        logger.info("=" * 50)
        
        # Overall stats
        total_metrics = len(self.metrics)
        if total_metrics == 0:
            logger.info("No performance metrics recorded yet")
            return
        
        # Recent metrics (last 10 minutes)
        recent_cutoff = datetime.now() - timedelta(minutes=10)
        recent_metrics = [m for m in self.metrics if m.timestamp > recent_cutoff]
        
        logger.info(f"Total metrics recorded: {total_metrics}")
        logger.info(f"Recent metrics (10min): {len(recent_metrics)}")
        
        # Per-operation stats
        logger.info("\n📈 OPERATION STATISTICS:")
        for operation in sorted(self.operation_stats.keys()):
            stats = self.get_stats(operation)
            if stats:
                logger.info(f"  {operation}:")
                logger.info(f"    Count: {stats['count']}")
                logger.info(f"    Avg: {stats['avg']:.3f}s")
                logger.info(f"    Min: {stats['min']:.3f}s")
                logger.info(f"    Max: {stats['max']:.3f}s")
                logger.info(f"    95th percentile: {stats['p95']:.3f}s")
        
        # Slow operations
        slow_ops = self.get_slow_operations(threshold=2.0)
        if slow_ops:
            logger.info("\n🐌 SLOW OPERATIONS (>2s avg):")
            for op in slow_ops[:5]:  # Top 5 slowest
                logger.info(f"  {op['operation']}: {op['avg_duration']:.3f}s avg ({op['count']} calls)")
        
        logger.info("=" * 50)

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

def monitor_performance(operation: str):
    """Decorator to monitor function performance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                performance_monitor.record(operation, duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                performance_monitor.record(f"{operation}_error", duration, {'error': str(e)})
                raise
        return wrapper
    return decorator

def log_performance_summary():
    """Log performance summary (call this periodically)"""
    performance_monitor.print_summary()