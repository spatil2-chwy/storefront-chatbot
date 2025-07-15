import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import openai
from dotenv import load_dotenv
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_openai_client():
    """Get OpenAI client with API key"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    return openai.OpenAI(api_key=api_key)

def read_log_file(log_file_path: str) -> Dict[str, Any]:
    """Read and parse a log file"""
    try:
        with open(log_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading log file {log_file_path}: {e}")
        raise

def structure_log_data(log_data: Dict[str, Any]) -> str:
    """Structure log data into a readable format for LLM"""
    
    # Extract key information
    user_query = log_data.get('raw_user_query', 'N/A')
    user_context = log_data.get('user_context', 'N/A')
    assistant_response = log_data.get('assistant_response', 'N/A')
    
    # Structure tool calls
    tool_calls_info = ""
    for tool_call in log_data.get('tool_calls', []):
        tool_calls_info += f"- Tool: {tool_call.get('tool_name', 'N/A')}\n"
        tool_calls_info += f"  Arguments: {json.dumps(tool_call.get('arguments', {}), indent=2)}\n"
    
    # Structure product results
    products_info = ""
    for product in log_data.get('product_results', [])[:10]:  # Top 10 products
        products_info += f"- {product.get('rank', 'N/A')}. {product.get('title', 'N/A')} (${product.get('price', 'N/A')}, {product.get('brand', 'N/A')}, Rating: {product.get('rating', 'N/A')})\n"
    
    # Structure performance metrics
    performance_info = f"""
- Total Processing Time: {log_data.get('total_processing_time', 'N/A')}s
- Function Call Time: {log_data.get('function_call_time', 'N/A')}s
- Tool Execution Time: {log_data.get('tool_execution_time', 'N/A')}s
- Product Search Time: {log_data.get('product_search_time', 'N/A')}s
- Ranking Time: {log_data.get('ranking_time', 'N/A')}s
- LLM Response Time: {log_data.get('llm_response_time', 'N/A')}s
"""
    
    # Combine everything
    structured_data = f"""
EVALUATION DATA:

USER QUERY: {user_query}

USER CONTEXT: {user_context}

TOOL CALLS:
{tool_calls_info}

PRODUCT RESULTS (Top 10):
{products_info}

ASSISTANT RESPONSE: {assistant_response}

PERFORMANCE METRICS:
{performance_info}

ERRORS: {log_data.get('errors', [])}
"""
    
    return structured_data

def create_evaluation_prompt(log_data: str) -> str:
    """Create the evaluation prompt with log data"""
    
    return f"""You are an expert evaluator of AI-powered shopping assistant systems. Your job is to comprehensively evaluate the performance of a pet product search and recommendation pipeline.

EVALUATION CRITERIA:

1. QUERY UNDERSTANDING (0-10):
   - Did the system correctly interpret the user's intent?
   - Did it identify key constraints (allergies, preferences, pet info)?
   - Did it extract relevant context from user profile?

2. TOOL SELECTION ACCURACY (0-10):
   - Was the correct tool chosen (product search vs article search)?
   - Were the tool parameters appropriate?

3. SEARCH QUALITY (0-10):
   - Was the search query well-constructed?
   - Did it capture the user's intent effectively?
   - Were filters applied correctly?

4. PRODUCT RELEVANCE (0-10):
   - Do the returned products match the user's needs?
   - Are they appropriate for the pet's characteristics?
   - Do they address the stated constraints (allergies, etc.)?

5. PRODUCT DIVERSITY (0-10):
   - Is there a good variety of options?
   - Are different price points represented?
   - Are different brands included?

6. BRAND PREFERENCE ALIGNMENT (0-10):
   - Do the results align with user's preferred brands?
   - Are preferred brands prioritized appropriately?

7. RESPONSE HELPFULNESS (0-10):
   - Is the response informative and actionable?
   - Does it provide useful insights about the products?
   - Is it appropriately concise?

8. FOLLOW-UP QUESTION QUALITY (0-10):
   - Are the follow-up questions relevant and specific?
   - Do they help narrow down choices effectively?
   - Are they based on actual product differences?

PERFORMANCE ANALYSIS:
- Identify bottlenecks in the pipeline
- Suggest optimizations
- Note any critical issues

LOG DATA:
{log_data}

Return your evaluation as a JSON object with the following structure:
{{
    "query_understanding_score": 0-10,
    "query_understanding_reasoning": "Reasoning for the score",
    "tool_selection_accuracy": 0-10,
    "tool_selection_reasoning": "Reasoning for the score",
    "search_relevance_score": 0-10,
    "search_relevance_reasoning": "Reasoning for the score",
    "query_enhancement_quality": 0-10,
    "query_enhancement_reasoning": "Reasoning for the score",
    "product_relevance_score": 0-10,
    "product_relevance_reasoning": "Reasoning for the score",
    "product_diversity_score": 0-10,
    "product_diversity_reasoning": "Reasoning for the score",
    "brand_preference_alignment": 0-10,
    "brand_preference_reasoning": "Reasoning for the score",
    "response_helpfulness": 0-10,
    "response_helpfulness_reasoning": "Reasoning for the score",
    "follow_up_question_quality": 0-10,
    "follow_up_question_reasoning": "Reasoning for the score",
    "performance_analysis": "Analysis of the pipeline performance",
    "bottlenecks_identified": ["List of bottlenecks"],
    "optimization_suggestions": ["List of optimization suggestions"],
    "overall_score": 0-10,
    "overall_assessment": "Overall assessment of the pipeline",
    "critical_issues": ["List of critical issues"],
    "strengths": ["List of strengths"]
}}"""

def evaluate_log_with_llm(log_file_path: str, model: str = "gpt-4o") -> Dict[str, Any]:
    """Evaluate a single log file using LLM"""
    
    try:
        # 1. Read the log file
        logger.info(f"Reading log file: {log_file_path}")
        log_data = read_log_file(log_file_path)
        
        # 2. Structure the log data
        logger.info("Structuring log data")
        structured_data = structure_log_data(log_data)
        
        # 3. Create evaluation prompt
        logger.info("Creating evaluation prompt")
        prompt = create_evaluation_prompt(structured_data)
        
        # 4. Send to LLM
        logger.info("Sending to LLM for evaluation")
        client = get_openai_client()
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert evaluator of AI systems. Provide detailed, constructive feedback."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        # 5. Parse JSON response
        logger.info("Parsing LLM response")
        content = response.choices[0].message.content
        if content is None:
            content = "{}"
        evaluation_result = json.loads(content)
        
        # 6. Add metadata
        evaluation_result["metadata"] = {
            "log_file": log_file_path,
            "evaluation_timestamp": datetime.now().isoformat(),
            "model_used": model,
            "original_log_data": {
                "session_id": log_data.get("session_id"),
                "raw_query": log_data.get("raw_user_query"),
                "total_processing_time": log_data.get("total_processing_time"),
                "products_returned": len(log_data.get("product_results", [])),
                "has_errors": len(log_data.get("errors", [])) > 0
            }
        }
        
        return evaluation_result
        
    except Exception as e:
        logger.error(f"Error evaluating log file {log_file_path}: {e}")
        return {
            "error": str(e),
            "log_file": log_file_path,
            "evaluation_timestamp": datetime.now().isoformat()
        }

def save_evaluation_result(evaluation_result: Dict[str, Any], output_path: Optional[str] = None) -> str:
    """Save evaluation result to file"""
    
    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = Path(evaluation_result.get("metadata", {}).get("log_file", "unknown")).stem
        output_path = f"llm_evaluation_{log_filename}_{timestamp}.json"
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(evaluation_result, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Evaluation result saved to: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error saving evaluation result: {e}")
        raise

def evaluate_single_log(log_file_path: str, save_result: bool = True, output_path: Optional[str] = None) -> Dict[str, Any]:
    """Complete workflow: read log, evaluate with LLM, optionally save result"""
    
    # Evaluate with LLM
    evaluation_result = evaluate_log_with_llm(log_file_path)
    
    # Save if requested
    if save_result and not evaluation_result.get("error"):
        save_evaluation_result(evaluation_result, output_path)
    
    return evaluation_result

def evaluate_all_logs(log_dir: str = "logs/logs", output_dir: str = "logs/llm_evaluations") -> List[Dict[str, Any]]:
    """Evaluate all log files in a directory"""
    
    log_path = Path(log_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    if not log_path.exists():
        logger.error(f"Log directory {log_dir} does not exist")
        return []
    
    results = []
    log_files = list(log_path.glob("eval_*.json"))
    
    logger.info(f"Found {len(log_files)} log files to evaluate")
    
    for log_file in log_files:
        try:
            logger.info(f"Evaluating {log_file.name}")
            
            # Evaluate the log
            evaluation_result = evaluate_log_with_llm(str(log_file))
            
            # Save result
            if not evaluation_result.get("error"):
                output_file = output_path / f"llm_eval_{log_file.stem}.json"
                save_evaluation_result(evaluation_result, str(output_file))
            
            results.append(evaluation_result)
            
        except Exception as e:
            logger.error(f"Error processing {log_file.name}: {e}")
            results.append({
                "error": str(e),
                "log_file": str(log_file),
                "evaluation_timestamp": datetime.now().isoformat()
            })
    
    return results

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Evaluate pipeline logs using LLM")
    parser.add_argument("--log-file", help="Single log file to evaluate")
    parser.add_argument("--log-dir", default="logs/logs", help="Directory containing logs to evaluate")
    parser.add_argument("--output-dir", default="logs/llm_evaluations", help="Directory to save results")
    parser.add_argument("--model", default="gpt-4o", help="LLM model to use")
    parser.add_argument("--no-save", action="store_true", help="Don't save results to file")
    
    args = parser.parse_args()
    
    if args.log_file:
        # Evaluate single log file
        result = evaluate_single_log(
            args.log_file, 
            save_result=not args.no_save,
            output_path=None if args.no_save else f"llm_eval_{Path(args.log_file).stem}.json"
        )
        
        if not args.no_save:
            print(f"Evaluation saved to: llm_eval_{Path(args.log_file).stem}.json")
        
        # Print summary
        if not result.get("error"):
            print(f"\nOverall Score: {result.get('overall_score', 'N/A')}/10")
            print(f"Query Understanding: {result.get('query_understanding_score', 'N/A')}/10")
            print(f"Product Relevance: {result.get('product_relevance_score', 'N/A')}/10")
            print(f"Response Helpfulness: {result.get('response_helpfulness', 'N/A')}/10")
        else:
            print(f"Error: {result.get('error')}")
    
    else:
        # Evaluate all logs in directory
        results = evaluate_all_logs(args.log_dir, args.output_dir)
        
        print(f"\nEvaluated {len(results)} log files")
        print(f"Results saved to: {args.output_dir}")
        
        # Print summary
        successful_results = [r for r in results if not r.get("error")]
        if successful_results:
            avg_score = sum(r.get('overall_score', 0) for r in successful_results) / len(successful_results)
            print(f"Average overall score: {avg_score:.2f}/10")