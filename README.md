# EstimAir

> AI-powered Airbnb price estimator for Paris

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-2.x-FF6600?style=flat&logo=xgboost&logoColor=white)
![MLflow](https://img.shields.io/badge/MLflow-3.x-0194E2?style=flat&logo=mlflow&logoColor=white)
![DVC](https://img.shields.io/badge/DVC-tracked-945DD6?style=flat&logo=dvc&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-16-000000?style=flat&logo=nextdotjs&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-2088FF?style=flat&logo=githubactions&logoColor=white)
![Render](https://img.shields.io/badge/Deployed_on-Render-46E3B7?style=flat&logo=render&logoColor=white)

---

## Live Demo

| Service | URL |
|---|---|
| Frontend | https://estimair-frontend.onrender.com |
| Backend API | https://estimair-backend.onrender.com |
| API Docs | https://estimair-backend.onrender.com/docs |
| MLflow Experiments | https://dagshub.com/BradleyJason/airbnb-price-predictor.mlflow |

---

## Project Overview

**EstimAir** is an end-to-end MLOps project that predicts the nightly price of an Airbnb listing in Paris using a machine learning model. It covers the full production ML lifecycle: data versioning, preprocessing, model training, experiment tracking, automated quality gates, and deployment.

**Dataset**: [Inside Airbnb - Paris](http://insideairbnb.com/get-the-data/) (March 2025)
- 86,064 raw listings · 79 columns
- 55,655 listings after cleaning · 9 features

**Goal**: Given a listing’s characteristics (room type, neighbourhood, capacity, amenities, reviews, availability), predict the nightly price in euros.

---

##  Architecture

```
                          ┌─────────────────────────────────────────┐
                          │           GitHub Actions CI/CD           │
                          │  PR→dev  ·  dev→staging  ·  staging→main │
                          └────────────────┬────────────────────────┘
                                           │
                                           ▼
┌─────────────┐   HTTPS    ┌──────────────────────────┐   MLflow URI   ┌──────────────────────┐
│             │ ─────────► │   Backend (FastAPI)       │ ─────────────► │   DagsHub            │
│  User       │            │   POST /predict           │                │   MLflow Registry    │
│  Browser    │            │   GET  /health            │ ◄─────────────── │   DVC Storage        │
│             │ ◄───────── │   Render · port 8000      │   XGBoost      │                      │
└──────┬──────┘            └──────────────────────────┘   @champion     └──────────────────────┘
       │
       ▼
┌─────────────────────────┐
│  Frontend (Next.js)     │
│  Dark UI · Glassmorphism│
│  Render · port 3000     │
└─────────────────────────┘
```

**Request flow**:
1. User fills the form on the Next.js frontend (9 fields)
2. Frontend sends `POST /predict` to the FastAPI backend
3. Backend loads the `@champion` XGBoost model from DagsHub MLflow Registry
4. Model returns a predicted price (inverse log1p transform applied)
5. Frontend displays the price with a confidence band (±€69 MAE)

---

##  Model Performance

| Metric | Value |
|---|---|
| Algorithm | XGBoost (500 estimators) |
| R² (test set) | **0.51** |
| MAE (test set) | **€69** |
| Training data | 55,655 Paris Airbnb listings |
| Target transform | `log1p(price)` → `expm1()` at inference |
| Outlier cap | p99 = €1,700 |

**Features** (9 inputs):

| Feature | Type | Description |
|---|---|---|
| `room_type` | int (0–3) | Entire home, Hotel, Private room, Shared room |
| `neighbourhood_cleansed` | int (0–19) | Paris arrondissement (LabelEncoded) |
| `accommodates` | int | Number of guests |
| `bedrooms` | int | Number of bedrooms |
| `bathrooms` | float | Number of bathrooms |
| `number_of_reviews` | int | Total reviews |
| `review_scores_rating` | float | Average rating (0–5) |
| `availability_365` | int | Days available per year |
| `minimum_nights` | int | Minimum stay |

---

## MLOps Pipeline

```
  Raw Data (DVC)
       │
       ▼
  src/preprocess.py          ← clean, encode, fix column order
       │
       ▼
  src/train.py               ← XGBoost · log1p target · MLflow logging
       │
       ▼
  MLflow Registry            ← experiment tracking on DagsHub
       │
       ├── dev→staging CI    ← quality gates: R²>0.45 · MAE<80€
       │         └──────────────► alias: candidate
       │
       └── staging→main CI   ← e2e smoke tests
                 └──────────────► alias: champion
                                       │
                                       ▼
                               src/predict.py    ← load @champion · expm1()
                                       │
                                       ▼
                               FastAPI /predict
```

**Model aliases** (MLflow 3.x - stages deprecated):
- `candidate` - passed quality gates, awaiting promotion
- `champion` - live in production

---

## Tests

**27 tests - all passing**

| Suite | Count | What it covers |
|---|---|---|
| Unit | 16 | `clean_price`, `clean_bathrooms`, `encode_categoricals` |
| Integration | 4 | FastAPI `/health`, `/predict`, 422 validation, 500 error |
| E2E | 7 | Full `preprocess()` pipeline on a mini CSV |

```bash
pytest tests/ -v                            # all tests
pytest tests/unit/                          # unit only
pytest tests/ -v --cov=src --cov=api        # with coverage
```

---

##  CI/CD Pipelines

Three GitHub Actions workflows trigger automatically:

### 1. `pr-dev.yml` - Pull Request to `dev`
- Run unit + integration tests
- Build Docker image (smoke test)

### 2. `dev-staging.yml` - Push to `staging`
- Run full test suite (unit + integration + e2e) with coverage
- **Quality gates**: R² > 0.45 AND MAE < 80€
- If gates pass → assign `candidate` alias in MLflow Registry

### 3. `staging-main.yml` - Push to `main`
- Verify `candidate` alias exists
- Promote `candidate` → `champion`
- Run e2e smoke tests on champion model

---

##  Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 16 · React 19 · Tailwind CSS 4 · framer-motion |
| **Backend** | FastAPI · Uvicorn · Pydantic v2 |
| **ML Model** | XGBoost 2.x · scikit-learn (LabelEncoder) |
| **Experiment tracking** | MLflow 3.x → DagsHub |
| **Data versioning** | DVC → DagsHub remote storage |
| **Tests** | pytest · pytest-asyncio · httpx · pytest-cov |
| **CI/CD** | GitHub Actions (3 pipelines) |
| **Containerisation** | Docker (Python 3.11-slim) |
| **Deployment** | Render (backend + frontend) |

---

##  Project Structure

```
airbnb-price-predictor/
├── data/
│   ├── raw/
│   │   ├── listings.csv          # Raw dataset (DVC tracked, git-ignored)
│   │   └── listings.csv.dvc      # DVC pointer → DagsHub remote
│   └── processed/
│       └── listings_clean.csv    # Output of preprocess.py (55,655 rows)
├── src/
│   ├── preprocess.py             # load → clean → encode → stable column order
│   ├── train.py                  # XGBoost + log1p(price) + MLflow logging
│   └── predict.py                # Load @champion · FEATURE_ORDER · expm1()
├── api/
│   └── main.py                   # FastAPI: GET /health  POST /predict + CORS
├── frontend/                     # Next.js 16 (App Router)
│   ├── app/
│   │   ├── layout.tsx            # Root layout · Geist font · dark bg
│   │   ├── page.tsx              # Form + result + interactive tooltip
│   │   └── globals.css           # Glassmorphism · sliders · selects
│   ├── next.config.ts            # Static export for Render/Vercel
│   └── package.json
├── scripts/
│   └── set_alias.py              # Manually assign MLflow alias
├── notebooks/
│   └── eda.ipynb                 # EDA (7 sections · seaborn plots)
├── tests/
│   ├── conftest.py               # Shared fixtures
│   ├── unit/test_preprocess.py   # 16 tests
│   ├── integration/test_api.py   # 4 tests
│   └── e2e/test_pipeline.py      # 7 tests
├── .github/workflows/
│   ├── pr-dev.yml
│   ├── dev-staging.yml
│   └── staging-main.yml
├── Dockerfile
├── requirements.txt
├── setup.py
└── CONTEXT.md
```

---

##  Quick Start

### Prerequisites
- Python 3.11
- Node.js 18+
- A [DagsHub](https://dagshub.com) account with access to `BradleyJason/airbnb-price-predictor`

### 1. Clone and install

```bash
git clone https://github.com/BradleyJason/airbnb-price-predictor.git
cd airbnb-price-predictor

pip install -r requirements.txt
pip install -e .
```

### 2. Configure environment variables

Create a `.env` file at the root:

```env
DAGSHUB_USERNAME=BradleyJason
DAGSHUB_TOKEN=<your-dagshub-token>
MLFLOW_TRACKING_URI=https://dagshub.com/BradleyJason/airbnb-price-predictor.mlflow
```

### 3. Pull the dataset

```bash
dvc pull          # downloads data/raw/listings.csv from DagsHub
```

### 4. Preprocess and train

```bash
python src/preprocess.py          # → data/processed/listings_clean.csv
python src/train.py               # → logs experiment to MLflow, registers model
python scripts/set_alias.py 3     # promote version 3 to @champion
```

### 5. Run the API

```bash
uvicorn api.main:app --reload
# → http://localhost:8000/docs
```

### 6. Run the frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

### 7. Run with Docker

```bash
docker build -t airbnb-price-predictor .
docker run -p 8000:8000 --env-file .env airbnb-price-predictor
```

---

##  Environment Variables

### Backend (`.env` at root)

| Variable | Description | Example |
|---|---|---|
| `DAGSHUB_USERNAME` | DagsHub account username | `BradleyJason` |
| `DAGSHUB_TOKEN` | DagsHub access token | `abc123...` |
| `MLFLOW_TRACKING_URI` | MLflow tracking server URL | `https://dagshub.com/BradleyJason/airbnb-price-predictor.mlflow` |

### Frontend (`frontend/.env.local`)

| Variable | Description | Example |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `http://localhost:8000` |

### GitHub Actions Secrets

Add under `Settings → Secrets → Actions`:
- `DAGSHUB_USERNAME`
- `DAGSHUB_TOKEN`
- `MLFLOW_TRACKING_URI`

---

##  12-Factor App Compliance

| # | Factor | Implementation |
|---|---|---|
| I | **Codebase** | Single Git repo · one codebase tracked in version control |
| II | **Dependencies** | `requirements.txt` + `setup.py` · `package.json` for frontend · no implicit system deps |
| III | **Config** | All secrets in environment variables (`.env`, Render env, GitHub Secrets) · zero hardcoded credentials |
| IV | **Backing services** | MLflow/DagsHub treated as attached resource via `MLFLOW_TRACKING_URI` |
| V | **Build, release, run** | Docker build (CI) → release image → run on Render · frontend built statically |
| VI | **Processes** | Stateless FastAPI process · no shared local state between requests |
| VII | **Port binding** | Uvicorn binds to port 8000 · Next.js on 3000 · both configurable via env |
| VIII | **Concurrency** | Uvicorn workers handle concurrency · horizontally scalable on Render |
| IX | **Disposability** | Fast startup · graceful shutdown via SIGTERM |
| X | **Dev/prod parity** | Same Docker image locally and on Render · DVC ensures identical datasets |
| XI | **Logs** | All output to stdout/stderr · no log files · collected by Render |
| XII | **Admin processes** | `scripts/set_alias.py` and `python src/train.py` run as explicit one-off tasks |
