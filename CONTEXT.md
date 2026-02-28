# Airbnb Price Predictor

MLOps project predicting Airbnb nightly prices in Paris.
Stack: XGBoost · MLflow · DVC · DagsHub · FastAPI · Next.js · pytest · GitHub Actions · Docker.
Dataset: Inside Airbnb Paris (`data/raw/listings.csv`, 86 064 listings → 55 655 après preprocessing).

---

## Stack technique

| Layer               | Technology                              |
|---------------------|-----------------------------------------|
| Model               | XGBoost — R²=0.51, MAE=69€             |
| Experiment tracking | MLflow → DagsHub                        |
| Data versioning     | DVC → DagsHub remote                    |
| Backend API         | FastAPI + Uvicorn · port 8000           |
| Frontend            | Next.js + Tailwind CSS · port 3000      |
| Tests               | pytest + pytest-asyncio + httpx         |
| CI/CD               | GitHub Actions (3 pipelines)            |
| Containerisation    | Docker                                  |
| Dataset             | Inside Airbnb Paris                     |

---

## Liens importants

| Ressource | URL |
|---|---|
| DagsHub repo | `BradleyJason/airbnb-price-predictor` |
| MLflow Registry | `models:/airbnb-price-predictor/Production` |
| Backend (Render) | à configurer |
| Frontend (Vercel) | à configurer |

---

## Project Structure

```
airbnb-price-predictor/
├── data/
│   ├── raw/
│   │   ├── listings.csv          # Raw dataset (DVC tracked, git-ignored)
│   │   └── listings.csv.dvc      # DVC pointer → remote DagsHub
│   └── processed/
│       └── listings_clean.csv    # Output of preprocess.py (55 655 lignes, 10 features)
├── src/
│   ├── preprocess.py             # load → clean_price → clean_bathrooms
│   │                             # → fill_missing → encode_categoricals
│   ├── train.py                  # XGBoost + log1p(price) + MLflow logging
│   └── predict.py                # Load model from MLflow Registry + expm1
├── api/
│   └── main.py                   # FastAPI: GET /health  POST /predict
├── frontend/                     # Next.js app (dark theme) — à créer
├── notebooks/
│   └── eda.ipynb                 # Full EDA (7 sections, seaborn plots)
├── tests/
│   ├── conftest.py               # Shared fixtures (raw_price_df, full_raw_df…)
│   ├── unit/
│   │   └── test_preprocess.py    # 16 tests: clean_price, clean_bathrooms,
│   │                             #           encode_categoricals
│   ├── integration/
│   │   └── test_api.py           # 4 tests: /health, /predict, 422, 500
│   └── e2e/
│       └── test_pipeline.py      # 7 tests: full preprocess() pipeline
├── .github/
│   └── workflows/
│       ├── pr-dev.yml            # PR → dev : tests unit+integration + docker build
│       ├── dev-staging.yml       # push → staging : full tests + MLflow quality gates
│       └── staging-main.yml      # push → main : promote Staging→Production + e2e
├── .gitignore
├── .dvcignore
├── Dockerfile
├── requirements.txt
├── setup.py
└── CONTEXT.md
```

---

## Ce qui est fait ✅

### Data & Preprocessing
- [x] `data/raw/listings.csv` (86 064 lignes, 79 colonnes)
- [x] DVC configuré avec remote DagsHub
- [x] `src/preprocess.py` complet : nettoyage `price` (`$`/`,`), `bathrooms_text`, imputation médiane, label-encoding → `data/processed/listings_clean.csv`

### Modèle
- [x] `src/train.py` : XGBoost 500 arbres, log-transform target, cap outliers p99 (€1 700)
- [x] **R²=0.51, MAE=69€** — modèle en stage **Production** sur MLflow Registry (DagsHub)
- [x] MLflow logging : params, MAE, R², price_cap, git_commit, dvc_data_version, registered_model_name

### API
- [x] `api/main.py` : FastAPI avec `GET /health` et `POST /predict`
- [x] `src/predict.py` : charge modèle depuis `models:/airbnb-price-predictor/Production`

### Tests (27 tests, tous passing ✅)
- [x] 16 tests unitaires (`clean_price`, `clean_bathrooms`, `encode_categoricals`)
- [x] 4 tests d'intégration (FastAPI avec mocks MLflow/DagsHub)
- [x] 7 tests e2e (pipeline complet sur mini-CSV temporaire)

### CI/CD (3 pipelines, tous verts ✅)
- [x] `pr-dev.yml` : tests unit+integration + coverage + docker build
- [x] `dev-staging.yml` : full tests + quality gates (R²>0.45, MAE<80€) + promotion Staging
- [x] `staging-main.yml` : vérification Staging + promotion Production + smoke tests e2e
- [x] Auth MLflow CI via `MLFLOW_TRACKING_USERNAME/PASSWORD`

### Analyse
- [x] `notebooks/eda.ipynb` : 7 sections (overview, price distribution, catégorielles, numériques, corrélations, outliers, conclusions)

### Infrastructure
- [x] `Dockerfile` : image Python 3.11-slim, expose port 8000

---

## Commandes importantes

```bash
# Installation
pip install -r requirements.txt && pip install -e .

# Preprocessing
python src/preprocess.py

# Entraînement
python src/train.py

# API locale
uvicorn api.main:app --reload
# → http://localhost:8000/docs

# Docker
docker build -t airbnb-price-predictor .
docker run -p 8000:8000 --env-file .env airbnb-price-predictor

# Tests
pytest tests/                          # tous les tests
pytest tests/unit/                     # unitaires seulement
pytest tests/ -v --cov=src --cov=api   # avec coverage

# DVC
dvc pull                               # récupère le dataset depuis DagsHub
dvc push                               # pousse les données vers DagsHub
```

---

## Variables d'environnement

Fichier `.env` (git-ignoré) :

```env
DAGSHUB_USERNAME=BradleyJason
DAGSHUB_TOKEN=<token DagsHub>
MLFLOW_TRACKING_URI=https://dagshub.com/BradleyJason/airbnb-price-predictor.mlflow
```

Secrets GitHub Actions (`Settings → Secrets → Actions`) :
- `DAGSHUB_USERNAME`
- `DAGSHUB_TOKEN`
- `MLFLOW_TRACKING_URI`

---

## Ce qui reste à faire 🔜

### Frontend Next.js (priorité 1)
- [ ] Créer `frontend/` avec Next.js + Tailwind CSS (dark theme)
- [ ] Formulaire de prédiction : accommodates, bedrooms, bathrooms, room_type, neighbourhood
- [ ] Appel `POST /predict` vers l'API FastAPI
- [ ] Affichage du prix prédit (design moderne)
- [ ] Déploiement sur Vercel

### Finaliser api/main.py (priorité 2)
- [ ] Ajouter CORS pour autoriser le domaine Vercel
- [ ] Vérifier que le chargement du modèle Production fonctionne en prod

### Déploiement Backend sur Render (priorité 3)
- [ ] Créer un service Web Render depuis l'image Docker
- [ ] Configurer les variables d'environnement (`DAGSHUB_TOKEN`, `MLFLOW_TRACKING_URI`)
- [ ] Ajouter l'URL Render dans le `.env` du frontend

### README (priorité 4)
- [ ] Diagramme d'architecture (MLOps pipeline complet)
- [ ] Instructions d'installation et de déploiement
- [ ] Badges CI, coverage, modèle

### Nettoyage final
- [ ] Supprimer le dossier `.claude/` (config temporaire Claude Code)
