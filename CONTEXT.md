# EstimAir - Airbnb Price Predictor

MLOps project predicting Airbnb nightly prices in Paris.
Stack: XGBoost - MLflow - DVC - DagsHub - FastAPI - Next.js - pytest - GitHub Actions - Docker.
Dataset: Inside Airbnb Paris (data/raw/listings.csv, 86 064 listings, 55 655 after preprocessing).

---

## Tech Stack

| Layer               | Technology                                           |
|---------------------|------------------------------------------------------|
| Model               | XGBoost - R2=0.51, MAE=69 EUR                        |
| Experiment tracking | MLflow 3.x -> DagsHub                                |
| Data versioning     | DVC -> DagsHub remote                                |
| Backend API         | FastAPI + Uvicorn, port 8000                         |
| Frontend            | Next.js 16 + Tailwind CSS + framer-motion, port 3000 |
| Tests               | pytest + pytest-asyncio + httpx                      |
| CI/CD               | GitHub Actions (3 pipelines)                         |
| Containerisation    | Docker                                               |
| Dataset             | Inside Airbnb Paris                                  |

---

## Important Links

| Resource         | URL                                                    |
|------------------|--------------------------------------------------------|
| DagsHub repo     | BradleyJason/airbnb-price-predictor                    |
| MLflow Registry  | models:/airbnb-price-predictor@champion                |
| Backend (Render) | https://estimair-backend.onrender.com                  |
| Frontend         | https://estimair-frontend.onrender.com                 |

---

## Project Structure

See README.md for the full annotated tree.

Key paths:
- src/preprocess.py      load -> clean_price -> clean_bathrooms -> fill_missing -> encode -> FINAL_COLUMNS
- src/train.py           XGBoost 500 trees + log1p(price) + MLflow logging
- src/predict.py         FEATURE_ORDER enforced, expm1(), @champion model, env var auth
- api/main.py            FastAPI: GET /health  POST /predict + CORSMiddleware
- frontend/app/page.tsx  Main page (form + result + tooltip)
- frontend/next.config.ts Static export config
- tests/unit/            16 tests
- tests/integration/     4 tests
- tests/e2e/             7 tests
- .github/workflows/     3 CI/CD pipelines

---

## What is Done

### Data & Preprocessing
- [x] data/raw/listings.csv (86 064 rows, 79 columns) - DVC tracked, DagsHub remote
- [x] src/preprocess.py: price cleaning ($,), bathrooms_text parsing, median imputation, label-encoding
- [x] Column order enforced via FINAL_COLUMNS to match FEATURE_ORDER in predict.py

### Model
- [x] src/train.py: XGBoost 500 trees, log1p(price), p99 outlier cap (EUR 1700), full MLflow logging
- [x] R2=0.51, MAE=69 EUR - model v3 with alias champion on DagsHub MLflow Registry
- [x] MLflow logs: params, mae, r2, price_cap, git_commit, dvc_data_version

### API
- [x] api/main.py: FastAPI with GET /health and POST /predict
  - 9 required fields: room_type, neighbourhood_cleansed, accommodates, bedrooms, bathrooms,
    number_of_reviews, review_scores_rating, availability_365, minimum_nights
  - CORSMiddleware (allow_origins=["*"] - restrict to frontend domain in production)
- [x] src/predict.py: loads models:/airbnb-price-predictor@champion, enforces FEATURE_ORDER, applies np.expm1()
  - Auth via env vars (MLFLOW_TRACKING_USERNAME/PASSWORD from DAGSHUB_USERNAME/TOKEN) - no dagshub.init()

### Frontend (EstimAir)
- [x] Next.js 16 + Tailwind + framer-motion in frontend/
- [x] Dark theme (#0a0a0f), glassmorphism cards, ambient glow
- [x] Full form (9 fields): 2 dropdowns + 5 sliders + 2 number inputs
  - Neighbourhoods displayed by arrondissement (1er -> 20e), LabelEncoder values sent to API
  - Subtitle: "Paris city limits - 20 districts"
- [x] Result: estimated price, vs neighbourhood average, confidence bar +/-EUR 69 with interactive tooltip
- [x] "Try another" button
- [x] API URL fallback: https://estimair-backend.onrender.com
- [x] next.config.ts: static export (output='export', trailingSlash=true, images.unoptimized=true)

### Tests (27 tests, all passing)
- [x] 16 unit tests (clean_price, clean_bathrooms, encode_categoricals)
- [x] 4 integration tests (FastAPI with mocked mlflow.xgboost.load_model + dotenv.load_dotenv)
- [x] 7 e2e tests (full pipeline on temp mini-CSV)

### CI/CD (3 pipelines)
- [x] pr-dev.yml: unit+integration tests + coverage + docker build
- [x] dev-staging.yml: full tests + quality gates (R2>0.45, MAE<80 EUR) -> alias candidate
- [x] staging-main.yml: verify alias candidate -> alias champion + e2e smoke tests
- [x] MLflow CI auth via MLFLOW_TRACKING_USERNAME/PASSWORD (no dagshub.init())
- [x] MLflow 3.x aliases used throughout: stages are deprecated

### Infrastructure & Documentation
- [x] Dockerfile: Python 3.11-slim image, exposes port 8000
- [x] scripts/set_alias.py: manually assign MLflow alias to a model version
- [x] README.md: complete documentation (architecture, CI/CD, quick start, 12-factor compliance)
- [x] notebooks/eda.ipynb: 7-section EDA

---

## Feature Encoding (sklearn LabelEncoder - alphabetical order)

### room_type
| Code | Label |
|---|---|
| 0 | Entire home/apt |
| 1 | Hotel room |
| 2 | Private room |
| 3 | Shared room |

### neighbourhood_cleansed (displayed by arrondissement, encoded alphabetically)
| Arrondissement | Display label       | API code |
|----------------|---------------------|----------|
| 1er            | Louvre              | 7        |
| 2e             | Bourse              | 1        |
| 3e             | Temple              | 17       |
| 4e             | Hotel-de-Ville      | 6        |
| 5e             | Pantheon            | 13       |
| 6e             | Luxembourg          | 8        |
| 7e             | Palais-Bourbon      | 12       |
| 8e             | Elysee              | 19       |
| 9e             | Opera               | 11       |
| 10e            | Entrepot            | 4        |
| 11e            | Popincourt          | 15       |
| 12e            | Reuilly             | 16       |
| 13e            | Gobelins            | 5        |
| 14e            | Observatoire        | 10       |
| 15e            | Vaugirard           | 18       |
| 16e            | Passy               | 14       |
| 17e            | Batignolles-Monceau | 0        |
| 18e            | Buttes-Montmartre   | 3        |
| 19e            | Buttes-Chaumont     | 2        |
| 20e            | Menilmontant        | 9        |

Note: Python Unicode sort places accented uppercase chars after all ASCII letters,
so "Elysee" (E-acute) sorts last -> code 19.

---

## Key Commands

    # Install
    pip install -r requirements.txt && pip install -e .

    # Preprocessing
    python src/preprocess.py

    # Training
    python src/train.py

    # Assign champion alias manually (after training)
    python scripts/set_alias.py 3    # replace 3 with the actual version number

    # Local API
    uvicorn api.main:app --reload
    # -> http://localhost:8000/docs

    # Local frontend
    cd frontend && npm run dev
    # -> http://localhost:3000

    # Build frontend (static export -> frontend/out/)
    cd frontend && npm run build

    # Docker
    docker build -t airbnb-price-predictor .
    docker run -p 8000:8000 --env-file .env airbnb-price-predictor

    # Tests
    pytest tests/                          # all tests
    pytest tests/unit/                     # unit only
    pytest tests/ -v --cov=src --cov=api   # with coverage

    # DVC
    dvc pull     # fetch dataset from DagsHub
    dvc push     # push data to DagsHub

---

## Environment Variables

.env at root (git-ignored):

    DAGSHUB_USERNAME=BradleyJason
    DAGSHUB_TOKEN=<dagshub token>
    MLFLOW_TRACKING_URI=https://dagshub.com/BradleyJason/airbnb-price-predictor.mlflow

frontend/.env.local (git-ignored):

    NEXT_PUBLIC_API_URL=http://localhost:8000
    # In production: https://estimair-backend.onrender.com

GitHub Actions Secrets (Settings -> Secrets -> Actions):
- DAGSHUB_USERNAME
- DAGSHUB_TOKEN
- MLFLOW_TRACKING_URI

---

## Remaining TODO

- [ ] Deploy backend on Render: create Web Service from Docker image, set env vars
- [ ] Restrict allow_origins in api/main.py to the frontend domain once known
- [ ] Deploy frontend: serve frontend/out/ as static site (Render static or Vercel)
- [ ] Set NEXT_PUBLIC_API_URL to point to Render backend
