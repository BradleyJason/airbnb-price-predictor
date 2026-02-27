# Airbnb Price Predictor

Airbnb Price Predictor - MLOps project using XGBoost, MLflow, DVC and DagsHub. Backend: FastAPI. Dataset: Inside Airbnb Paris.

## Stack

| Component       | Technology          |
|----------------|---------------------|
| Model          | XGBoost             |
| Experiment tracking | MLflow + DagsHub |
| Data versioning | DVC + DagsHub      |
| API            | FastAPI + Uvicorn   |
| Dataset        | Inside Airbnb Paris |
| Tests          | pytest + httpx      |

## Project Structure

```
airbnb-price-predictor/
├── data/raw/           # Raw CSV data (DVC tracked, git-ignored)
├── src/
│   ├── preprocess.py   # Data cleaning and feature engineering
│   ├── train.py        # Model training with MLflow logging
│   └── predict.py      # Inference logic
├── api/
│   └── main.py         # FastAPI application
├── tests/
│   ├── unit/           # Unit tests for src modules
│   ├── integration/    # Integration tests for API
│   └── e2e/            # End-to-end tests
└── .github/workflows/  # CI/CD pipelines
```

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run training
python src/train.py

# Run API
uvicorn api.main:app --reload

# Run tests
pytest tests/
```

## Environment Variables

Copy `.env.example` to `.env` and fill in:
- `MLFLOW_TRACKING_URI`
- `DAGSHUB_TOKEN`
