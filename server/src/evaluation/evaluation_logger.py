import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict, field
import logging

logger = logging.getLogger(__name__)

@dataclass
class EvaluationLog:
    """Data class for structured evaluation logging"""
    # Basic identification
    session_id: str
    timestamp: str
    
    # User input
    raw_user_query: str
    user_context: Optional[str] = None
    has_image: bool = False
    
    # Chat history
    chat_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Tool calls and function execution
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    
    # Product results
    product_results: List[Dict[str, Any]] = field(default_factory=list)
    
    # Response generation
    assistant_response: Optional[str] = None

    # Performance metrics - detailed breakdown
    total_processing_time: Optional[float] = None
    function_call_time: Optional[float] = None  # Time for LLM to generate function call arguments
    tool_execution_time: Optional[float] = None  # Total time to execute tool call
    product_search_time: Optional[float] = None  # Time for database query in search_products
    ranking_time: Optional[float] = None  # Time for ranking products
    search_analyzer_time: Optional[float] = None  # Time to convert ranked results to Product objects
    article_search_time: Optional[float] = None  # Time for article search
    llm_response_time: Optional[float] = None  # Time for final LLM response generation
    context_formatting_time: Optional[float] = None  # Time to format products for LLM
    
    # Error handling
    errors: List[str] = field(default_factory=list)
    


class EvaluationLogger:
    """Logger for capturing evaluation data from the chatbot pipeline"""
    
    def __init__(self, log_dir: str = "logs/evaluation"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.current_session_id = str(uuid.uuid4())
        self.current_log: Optional[EvaluationLog] = None
        
    def start_new_query(self, raw_user_query: str, user_context: str = "", has_image: bool = False) -> str:
        """Start logging a new user query"""
        
        self.current_log = EvaluationLog(
            session_id=self.current_session_id,
            timestamp=datetime.now().isoformat(),
            raw_user_query=raw_user_query,
            user_context=user_context if user_context else None,
            has_image=has_image
        )
        
        logger.info(f"Started evaluation logging for query: {raw_user_query}")
        return self.current_session_id
    
    def log_tool_call(self, tool_name: str, arguments: Dict[str, Any], execution_time: float):
        """Log a tool call with its arguments and execution time"""
        if self.current_log:
            tool_call_data = {
                "tool_name": tool_name,
                "arguments": arguments,
            }
            self.current_log.tool_execution_time = execution_time
            self.current_log.tool_calls.append(tool_call_data)
            
            logger.debug(f"Tool call logged: {tool_name} ({execution_time:.3f}s)")
    
    def log_product_results(self, products: List[Any], limit: int = 10):
        """Log product search results"""
        if self.current_log:
            # Extract top products for evaluation
            top_products = []
            for i, product in enumerate(products[:limit]):
                try:
                    product_data = {
                        "rank": i + 1,
                        "product_id": getattr(product, 'id', None),
                        "title": getattr(product, 'title', None),
                        "brand": getattr(product, 'brand', None),
                        "category": getattr(product, 'category', None),
                        "price": getattr(product, 'price', None),
                        "rating": getattr(product, 'rating', None),
                        "review_count": getattr(product, 'review_count', None)
                    }
                    top_products.append(product_data)
                except Exception as e:
                    logger.warning(f"Error extracting product data: {e}")
            
            # Store the product results in the log
            self.current_log.product_results = top_products
            logger.debug(f"Product results logged: {len(products)} found, {len(top_products)} logged")
    
    def log_chat_history(self, history: List[Dict[str, Any]]):
        """Log the chat history"""
        if self.current_log:
            self.current_log.chat_history = history
            logger.debug(f"Chat history logged: {len(history)} messages")
    
    def log_categories(self, filtered: List[str], matched: List[str]):
        """Log category filtering and matching information"""
        if self.current_log:
            logger.debug(f"Categories logged: {len(filtered)} filtered, {len(matched)} matched")
    
    def log_assistant_response(self, response: str):
        """Log the final assistant response"""
        if self.current_log:
            self.current_log.assistant_response = response
            logger.debug(f"Assistant response logged")
    
    def log_timing(self, 
                   function_call_time: Optional[float] = None,
                   tool_execution_time: Optional[float] = None,
                   product_search_time: Optional[float] = None,
                   ranking_time: Optional[float] = None,
                   search_analyzer_time: Optional[float] = None,
                   article_search_time: Optional[float] = None,
                   llm_response_time: Optional[float] = None,
                   context_formatting_time: Optional[float] = None,
                   total_processing_time: Optional[float] = None):
        """Log any timing information. Only updates fields that are not None."""
        if self.current_log:
            if function_call_time is not None:
                self.current_log.function_call_time = function_call_time
            if tool_execution_time is not None:
                self.current_log.tool_execution_time = tool_execution_time
            if product_search_time is not None:
                self.current_log.product_search_time = product_search_time
            if ranking_time is not None:
                self.current_log.ranking_time = ranking_time
            if search_analyzer_time is not None:
                self.current_log.search_analyzer_time = search_analyzer_time
            if article_search_time is not None:
                self.current_log.article_search_time = article_search_time
            if llm_response_time is not None:
                self.current_log.llm_response_time = llm_response_time
            if context_formatting_time is not None:
                self.current_log.context_formatting_time = context_formatting_time
            if total_processing_time is not None:
                self.current_log.total_processing_time = total_processing_time
            logger.debug(f"Timing logged: {locals()}")
    
    def log_error(self, error: str):
        """Log errors that occur during processing"""
        if self.current_log:
            self.current_log.errors.append(error)
            logger.error(f"Error logged: {error}")
    
    def save_log(self) -> Optional[str]:
        """Save the current log to file and return the filename"""
        if not self.current_log:
            logger.warning("No current log to save")
            return None

        # Create filename with timestamp and query ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"eval_{timestamp}_{self.current_log.raw_user_query[:8]}.json"
        filepath = self.log_dir / filename
        
        try:
            # Convert to dict and save as JSON
            log_data = asdict(self.current_log)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Evaluation log saved: {filepath}")
            return str(filepath)
        
        except Exception as e:
            logger.error(f"Error saving evaluation log: {e}")
            return None
    
    def get_current_log(self) -> Optional[EvaluationLog]:
        """Get the current log object"""
        return self.current_log
    
    def clear_current_log(self):
        """Clear the current log"""
        self.current_log = None

# Global instance for easy access
evaluation_logger = EvaluationLogger() 