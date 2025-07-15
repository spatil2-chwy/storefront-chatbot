# Evaluation System

This evaluation system captures comprehensive data about your chatbot pipeline's performance and provides tools to analyze and improve it.

## Overview

The evaluation system logs every aspect of a user query through your chatbot pipeline, including:

1. **Raw user query** - The original user input
2. **User context** - Customer context and preferences
3. **Chat history** - Complete conversation history
4. **Tool calls** - Which tools were called (product search, article search, or none)
5. **Search parameters** - Category levels, required/excluded ingredients
6. **Product results** - Top 10 recommended products with details (rank, title, brand, price, rating, etc.)
7. **Assistant response** - The final response to the user
8. **Performance metrics** - Detailed timing breakdown for each component
9. **Errors** - Any errors that occurred during processing

## How It Works

### 1. Automatic Logging

The evaluation system is automatically integrated into your chatbot pipeline. Every time a user makes a query, the system:

- Creates a unique session ID
- Logs the raw user input and context
- Captures the complete chat history
- Tracks all tool calls and their parameters
- Records search results and top 10 product recommendations
- Captures the final assistant response
- Measures detailed performance timing
- Saves everything to a structured JSON file

### 2. Log Files

Evaluation logs are saved in `logs/evaluation/` with the format:
```
eval_YYYYMMDD_HHMMSS_<query_id>.json
```

Each log file contains a complete record of one user interaction.

## Performance Metrics

The system captures detailed timing information for each component:

- **function_call_time** - Time for LLM to generate function call arguments
- **tool_execution_time** - Total time to execute tool calls
- **product_search_time** - Time for database query in search_products
- **ranking_time** - Time for ranking products
- **conversion_time** - Time to convert ranked results to Product objects
- **article_search_time** - Time for article search
- **llm_response_time** - Time for final LLM response generation
- **context_formatting_time** - Time to format products for LLM
- **total_processing_time** - Total time for the entire request

## Product Results

The system automatically logs the top 10 recommended products with:
- Rank position
- Product ID
- Title
- Brand
- Category
- Price
- Rating
- Review count

## Usage

### Analyzing Results

#### 1. Basic Pipeline Analysis

Run the pipeline evaluator to get quantitative insights:

```bash
cd server/src/utils
python evaluate_pipeline.py
```

This will provide:
- Performance metrics (response times, tool usage)
- Search pattern analysis
- Product result statistics
- Error analysis
- Automated recommendations

#### 2. LLM-Based Quality Evaluation

For qualitative assessment of accuracy and relevance:

```bash
cd server/src/utils
python llm_evaluation.py
```

This uses GPT-4 to evaluate:
- Query understanding accuracy
- Tool selection appropriateness
- Search relevance
- Product recommendation quality
- Response helpfulness
- Follow-up question relevance

### Output Files

- `pipeline_evaluation_report.json` - Detailed quantitative analysis
- `llm_evaluations.json` - Qualitative LLM evaluations