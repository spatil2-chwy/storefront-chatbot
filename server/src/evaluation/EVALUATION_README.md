# Chatbot Pipeline Evaluation System

A comprehensive evaluation and monitoring system for AI-powered product recommendation chatbots. This system captures, analyzes, and visualizes every aspect of your chatbot pipeline's performance to help optimize user experience and system efficiency.

## 🎯 Overview

The evaluation system provides:

- **📊 Real-time Logging**: Automatic capture of every user interaction
- **🔍 Quantitative Analysis**: Performance metrics without LLM costs
- **🤖 LLM Evaluation**: AI-powered quality assessment using GPT-4
- **📈 Interactive Dashboard**: Web-based visualization and monitoring
- **📋 Actionable Insights**: Specific recommendations for improvement

## 🔄 Logging System

### Automatic Data Capture

The `evaluation_logger.py` automatically logs every user interaction through your chatbot pipeline:

#### Captured Data
- **Session Information**: Unique IDs, timestamps, processing times
- **User Input**: Raw queries, user context, pet information
- **Pipeline Execution**: Tool calls, search parameters, chat history
- **Results**: Top 10 product recommendations with rankings
- **Performance**: Detailed timing breakdown for each component
- **Errors**: Any failures during processing

### Performance Metrics

The system captures detailed timing for each pipeline component:

- **function_call_time**: LLM function call generation
- **tool_execution_time**: Total tool execution time
- **product_search_time**: Database query performance
- **ranking_time**: Product ranking algorithm
- **search_analyzer_time**: Result conversion time
- **article_search_time**: Article search performance
- **llm_response_time**: Final response generation
- **context_formatting_time**: Product formatting for LLM
- **total_processing_time**: End-to-end processing

## 📊 Evaluation Types

### 1. Quantitative Evaluation (`quantitative_evaluation.py`)

**No LLM Required** - Calculates metrics from log data:

#### Performance Metrics
- Average response times for each component
- Performance bottlenecks identification
- Slow query analysis (>10s, >20s thresholds)

#### Success Metrics
- Success rate (queries without errors)
- Error rate and error patterns
- Products returned per query
- Average product ratings and prices

#### Quality Metrics
- Brand diversity in results
- Price range coverage
- Rating distribution analysis
- Tool usage patterns

#### User Context Analysis
- Context availability percentage
- Average context length
- Personalization effectiveness

### 2. LLM Evaluation (`llm_evaluation.py`)

**AI-Powered Assessment** - Uses GPT-4 to evaluate response quality:

#### Evaluation Criteria (0-10 Scale)
- **Query Understanding**: Intent interpretation accuracy
- **Tool Selection**: Correct tool choice and parameters
- **Search Quality**: Query construction effectiveness
- **Product Relevance**: Result match to user needs
- **Product Diversity**: Option variety and representation
- **Brand Preference Alignment**: Preferred brand prioritization
- **Response Helpfulness**: Information usefulness and actionability
- **Follow-up Question Quality**: Question relevance and effectiveness


## 🖥️ Interactive Dashboard

### Dashboard Features (`dashboard.py`)

A web-based dashboard built with Dash/Plotly providing:

#### 1. Session Overview Tab
- User query and context display
- Pet information extraction and visualization
- Tool usage breakdown
- Processing time analysis

#### 2. Query Flow Tab
- Step-by-step pipeline visualization
- Chat history display
- Tool call sequence
- Performance timing breakdown

#### 3. Product Results Tab
- Product ranking analysis
- Price distribution charts
- Brand diversity visualization
- Rating analysis

#### 4. Evaluation Metrics Tab
- LLM evaluation scores with reasoning
- Performance analysis
- Bottleneck identification
- Optimization suggestions

#### 5. System Metrics Tab
- Performance trends over time
- Error rate monitoring
- Success rate tracking
- Health score calculation

### Data Integration (`data_parser.py`)

Handles loading and parsing of:
- Evaluation logs (`eval_*.json`)
- LLM evaluations (`llm_eval_*.json`)
- Quantitative reports (`quantitative_report_*.json`)

Extracts structured data for visualization:
- Pet information from user context
- Customer preferences and demographics
- Tool call arguments and parameters
- Performance metrics and timing data

## 🚀 Quick Start

1. Run Quantitative Analysis

```bash
cd server/src/evaluation
python quantitative_evaluation.py
```

### 3. Run LLM Evaluation

```bash
python llm_evaluation.py
```

### 4. Start Dashboard

```bash
python dashboard.py
```

Then visit `http://localhost:8050` for the interactive dashboard.


## 📋 Output Files

- `logs/logs/eval_*.json` - Raw evaluation logs
- `logs/llm_evaluations/llm_eval_*.json` - LLM evaluation results
- `logs/quantitative_reports/quantitative_report_*.json` - Quantitative analysis reports