import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import openai
from dotenv import load_dotenv
from src.evaluation.data_parser import EvaluationDataParser

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
    parser = EvaluationDataParser()
    return parser.read_log_file(log_file_path)

def structure_log_data(log_data: Dict[str, Any]) -> str:
    """Structure log data into a readable format for LLM"""
    parser = EvaluationDataParser()
    return parser.structure_log_data(log_data)

def determine_response_type(log_data: Dict[str, Any]) -> str:
    """Determine the type of response based on tool calls and content"""
    tool_calls = log_data.get('tool_calls', [])
    
    if not tool_calls:
        return "direct_response"
    
    # Check what tools were used
    tools_used = [tool.get('tool_name') for tool in tool_calls]
    
    if 'search_articles' in tools_used:
        return "article_search"
    elif 'search_products' in tools_used:
        return "product_search"
    else:
        return "direct_response"

def create_evaluation_prompt(log_data: str, response_type: str) -> str:
    """Create the evaluation prompt with log data based on response type"""
    
    if response_type == "direct_response":
        return f"""You are an expert evaluator of AI-powered shopping assistant systems.

EVALUATION CRITERIA:

1. QUERY UNDERSTANDING (0-10):
   - Did the system correctly interpret the user's intent?
   - Did it identify the appropriate response type (greeting, casual conversation, etc.)?

2. RESPONSE APPROPRIATENESS (0-10):
   - Is the response appropriate for the type of query?
   - Does it match the expected tone and style for a shopping assistant?

3. ENGAGEMENT QUALITY (0-10):
   - Is the response engaging and welcoming?
   - Does it encourage further interaction or provide clear next steps?

4. HELPFULNESS (0-10):
   - Is the response helpful and informative?
   - Does it provide value to the user?

5. TONE AND PERSONALITY (0-10):
   - Is the tone warm, friendly, and appropriate?
   - Does it reflect the brand personality?

LOG DATA:
{log_data}

Return your evaluation as a JSON object with the following structure:
{{
    "query_understanding_score": 0-10,
    "query_understanding_reasoning": "Reasoning for the score",
    "response_appropriateness": 0-10,
    "response_appropriateness_reasoning": "Reasoning for the score",
    "engagement_quality": 0-10,
    "engagement_quality_reasoning": "Reasoning for the score",
    "helpfulness": 0-10,
    "helpfulness_reasoning": "Reasoning for the score",
    "tone_and_personality": 0-10,
    "tone_and_personality_reasoning": "Reasoning for the score",
    "performance_analysis": "Analysis of the direct response",
    "overall_score": 0-10,
    "overall_assessment": "Overall assessment of the response",
}}"""

    elif response_type == "article_search":
        return f"""You are an expert evaluator of AI-powered shopping assistant systems. Your job is to evaluate the performance of an article search response from a pet shopping assistant.

EVALUATION CRITERIA:

1. QUERY UNDERSTANDING (0-10):
   - Did the system correctly interpret the user's intent?
   - Did it identify that the user needed informational content rather than products?

2. TOOL SELECTION ACCURACY (0-10):
   - Was article search the appropriate tool choice?
   - Were the search parameters well-constructed?

3. ARTICLE RELEVANCE (0-10):
   - Are the returned articles relevant to the user's question?
   - Do they address the specific concerns or topics mentioned?

4. CONTENT QUALITY (0-10):
   - Is the article content high-quality and informative?
   - Are the summaries accurate and helpful?

5. REFERENCE LINK QUALITY (0-10):
   - Are the provided links logical and relevant?
   - Do they lead to appropriate educational content?

6. RESPONSE STRUCTURE (0-10):
   - Is the response well-structured and easy to follow?
   - Does it effectively summarize the article content?

7. ACTIONABILITY (0-10):
   - Does the response provide actionable advice?
   - Does it suggest relevant product categories when appropriate?

LOG DATA:
{log_data}

Return your evaluation as a JSON object with the following structure:
{{
    "query_understanding_score": 0-10,
    "query_understanding_reasoning": "Reasoning for the score",
    "tool_selection_accuracy": 0-10,
    "tool_selection_reasoning": "Reasoning for the score",
    "article_relevance": 0-10,
    "article_relevance_reasoning": "Reasoning for the score",
    "content_quality": 0-10,
    "content_quality_reasoning": "Reasoning for the score",
    "reference_link_quality": 0-10,
    "reference_link_quality_reasoning": "Reasoning for the score",
    "response_structure": 0-10,
    "response_structure_reasoning": "Reasoning for the score",
    "actionability": 0-10,
    "actionability_reasoning": "Reasoning for the score",
    "performance_analysis": "Analysis of the article search response",
    "overall_score": 0-10,
    "overall_assessment": "Overall assessment of the response",
}}"""

    else:  # product_search
        return f"""You are an expert evaluator of AI-powered shopping assistant systems. Your job is to comprehensively evaluate the performance of a product search and recommendation pipeline.

EVALUATION CRITERIA:

1. QUERY UNDERSTANDING (0-10):
   - Did the system correctly interpret the user's intent?
   - Did it identify key constraints (allergies, preferences, pet info)?
   - Did it extract relevant context from user profile?

2. TOOL SELECTION ACCURACY (0-10):
   - Was product search the appropriate tool choice?
   - Were the tool parameters appropriate?

3. SEARCH QUALITY (0-10):
   - Was the search query well-constructed?
   - Did it capture the user's intent effectively?
   - Were filters and user context applied correctly?

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
   - Are the follow-up questions relevant and specific?
   - Does it provide useful insights about the products or help narrow down choices effectively?

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
    "product_relevance_score": 0-10,
    "product_relevance_reasoning": "Reasoning for the score",
    "product_diversity_score": 0-10,
    "product_diversity_reasoning": "Reasoning for the score",
    "brand_preference_alignment": 0-10,
    "brand_preference_reasoning": "Reasoning for the score",
    "response_helpfulness": 0-10,
    "response_helpfulness_reasoning": "Reasoning for the score",
    "performance_analysis": "Analysis of the product search pipeline",
    "overall_score": 0-10,
    "overall_assessment": "Overall assessment of the pipeline",
}}"""

def evaluate_log_with_llm(log_file_path: str, model: str = "gpt-4o") -> Dict[str, Any]:
    """Evaluate a single log file using LLM"""
    
    try:
        # 1. Read the log file
        logger.info(f"Reading log file: {log_file_path}")
        log_data = read_log_file(log_file_path)
        
        # 2. Determine response type
        response_type = determine_response_type(log_data)
        logger.info(f"Detected response type: {response_type}")
        
        # 3. Structure the log data
        logger.info("Structuring log data")
        structured_data = structure_log_data(log_data)
        
        # 4. Create evaluation prompt based on response type
        logger.info(f"Creating evaluation prompt for {response_type}")
        prompt = create_evaluation_prompt(structured_data, response_type)
        
        # 5. Send to LLM
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
        
        # 6. Parse JSON response
        logger.info("Parsing LLM response")
        content = response.choices[0].message.content
        if content is None:
            content = "{}"
        evaluation_result = json.loads(content)
        
        # 7. Add metadata including response type
        evaluation_result["metadata"] = {
            "log_file": log_file_path,
            "evaluation_timestamp": datetime.now().isoformat(),
            "model_used": model,
            "response_type": response_type,
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
        
    else:
        # Evaluate all logs in directory
        results = evaluate_all_logs(args.log_dir, args.output_dir)
        
        print(f"\nEvaluated {len(results)} log files")
        print(f"Results saved to: {args.output_dir}")