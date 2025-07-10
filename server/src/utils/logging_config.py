import logging
import sys
import time
from pathlib import Path

def setup_logging():
    """Set up logging configuration for the application"""
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure the root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # File handler for all logs
            logging.FileHandler(log_dir / "app.log"),
            # Console handler for INFO and above
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific log levels for different modules
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

def get_logger(name: str = None):
    """Get a logger instance with the given name"""
    return logging.getLogger(name or __name__)

def log_timing(operation: str, start_time: float, logger_instance=None):
    """Log timing information for an operation"""
    if logger_instance is None:
        logger_instance = logging.getLogger(__name__)
    
    elapsed = time.time() - start_time
    logger_instance.debug(f"{operation} took: {elapsed:.3f}s")
    return elapsed

# Initialize logging when this module is imported
logger = setup_logging()
