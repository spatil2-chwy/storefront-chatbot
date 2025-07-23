## Quick Start

1. Run Test Queries

- Start the FastAPI server:
```bash
cd server
uvicorn src.main:app --reload --host localhost --port 8000
```

- Single Query Test
```bash
cd server
python src/evaluation/test_suite_runner.py
```

- Full Test Suite - uncomment in test_suite_runner.py
await runner.run_test_suite(customer_key=customer_key)

```bash
python src/evaluation/test_suite_runner.py
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
streamlit run src/evaluation/dashboard.py
```

Then visit `http://localhost:8050` for the interactive dashboard.


## 📋 Output Files

- `logs/logs/eval_*.json` - Raw evaluation logs
- `logs/llm_evaluations/llm_eval_*.json` - LLM evaluation results
- `logs/quantitative_reports/quantitative_report_*.json` - Quantitative analysis reports