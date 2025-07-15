# Logging System

This logging system captures comprehensive data about your chatbot pipeline's performance and provides tools to analyze and improve it.

## Overview

The logging system logs every aspect of a user query through your chatbot pipeline, including:

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

The logging system is automatically integrated into your chatbot pipeline. Every time a user makes a query, the system:

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


## Evaluation Pipeline

## 🎯 Overview

This evaluation system captures and analyzes every aspect of your chatbot pipeline's performance, including:

- **Performance Metrics**: Response times, bottlenecks, and efficiency
- **Quality Assessment**: Product relevance, diversity, and user satisfaction
- **Reliability Analysis**: Error rates and system stability
- **LLM Evaluation**: AI-powered assessment of response quality and relevance
- **Trend Analysis**: Performance patterns over time
- **Actionable Recommendations**: Specific improvements to implement


## 📊 What Gets Evaluated

### 1. **Quantitative Metrics** (No LLM Required)

#### Performance Metrics
- **Total Processing Time**: End-to-end response time
- **Product Search Time**: Database query performance
- **LLM Response Time**: AI generation speed
- **Function Call Time**: Tool selection efficiency
- **Ranking Time**: Product ranking algorithm speed

#### Success Metrics
- **Success Rate**: Percentage of queries without errors
- **Error Rate**: System reliability
- **Products Returned**: Search result coverage
- **Average Product Rating**: Result quality
- **Average Product Price**: Price range coverage

#### Quality Metrics
- **Query Length Analysis**: User input patterns
- **Tool Usage Distribution**: Which tools are used most
- **Brand Diversity**: Variety in search results
- **Price Range**: Economic diversity
- **Rating Distribution**: Quality spread

#### User Context Analysis
- **Context Usage**: How often user context is available
- **Context Length**: Richness of user information

### 2. **LLM-as-a-Judge Evaluation** (Qualitative)

#### Query Understanding (0-10)
- Intent interpretation accuracy
- Constraint identification (allergies, preferences)
- Context extraction quality

#### Tool Selection Accuracy (0-10)
- Correct tool choice (product vs article search)
- Parameter appropriateness

#### Search Quality (0-10)
- Query construction effectiveness
- Filter application correctness

#### Product Relevance (0-10)
- Result match to user needs
- Pet characteristic alignment
- Constraint satisfaction

#### Product Diversity (0-10)
- Option variety
- Price point representation
- Brand variety

#### Brand Preference Alignment (0-10)
- Preferred brand prioritization
- Brand preference respect

#### Response Helpfulness (0-10)
- Information usefulness
- Actionability
- Conciseness

#### Follow-up Question Quality (0-10)
- Question relevance
- Choice narrowing effectiveness
- Product difference basis

## 🚀 Quick Start

### 1. **Run Comprehensive Evaluation**

```bash
cd server/src/evaluation
python run_evaluation.py --print-summary
```

This will:
- Analyze all evaluation logs
- Run both quantitative and LLM evaluation
- Generate comprehensive report
- Print summary to console
- Save detailed results to JSON

### 2. **Run Only Quantitative Analysis**

```bash
python run_evaluation.py --no-llm --print-summary
```

### 3. **Start Dashboard**

```bash
python dashboard.py
```

Then visit `http://localhost:8000` for the web dashboard.

## 📈 Understanding Your Results

### Health Score Breakdown

The system calculates an overall **Health Score (0-100)** based on:

- **Performance Score (40%)**: Response times and efficiency
- **Quality Score (40%)**: Result relevance and diversity  
- **Reliability Score (20%)**: Error rates and stability

### Status Levels

- **Excellent (80-100)**: System performing optimally
- **Good (60-79)**: Minor optimizations needed
- **Fair (40-59)**: Significant improvements required
- **Poor (0-39)**: Critical issues need immediate attention

### Key Metrics to Monitor

#### 🚨 Critical Metrics
- **Response Time > 15s**: Unacceptable user experience
- **Error Rate > 5%**: System reliability issues
- **Success Rate < 95%**: Core functionality problems

#### ⚠️ Warning Metrics
- **Slow Queries > 20%**: Performance degradation
- **Product Count < 5**: Poor search coverage
- **Brand Diversity < 0.3**: Limited variety

#### 💡 Optimization Opportunities
- **LLM Score < 6.0**: Response quality improvements
- **Context Usage < 50%**: Personalization opportunities
- **Tool Usage Imbalance**: Workflow optimization