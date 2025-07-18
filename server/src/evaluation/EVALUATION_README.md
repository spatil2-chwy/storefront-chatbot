## Quick Start

1. Run Test Queries
```bash
cd server
python -m src.evaluation.test_suite_runner  
```

2. Run Quantitative Analysis

```bash
python -m src.evaluation.quantitative_evaluation
```

### 3. Run LLM Evaluation

```bash
python -m src.evaluation.llm_evaluation
```

### 4. Start Dashboard

```bash
cd src/evaluation
python dashboard.py
```

Then visit `http://localhost:8050` for the interactive dashboard.


## 📋 Output Files

- `logs/logs/eval_*.json` - Raw evaluation logs
- `logs/llm_evaluations/llm_eval_*.json` - LLM evaluation results
- `logs/quantitative_reports/quantitative_report_*.json` - Quantitative analysis reports