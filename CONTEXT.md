# EstimAir — Airbnb Price Predictor

MLOps project predicting Airbnb nightly prices in Paris.
Stack: XGBoost · MLflow · DVC · DagsHub · FastAPI · Next.js · pytest · GitHub Actions · Docker.
Dataset: Inside Airbnb Paris (`data/raw/listings.csv`, 86 064 listings → 55 655 après preprocessing).

---

## Stack technique

| Layer               | Technology                                    |
|---------------------|-----------------------------------------------|
| Model               | XGBoost — R²=0.51, MAE=69€                   |
| Experiment tracking | MLflow → DagsHub                              |
| Data versioning     | DVC → DagsHub remote                          |
| Backend API         | FastAPI + Uvicorn · port 8000                 |
| Frontend            | Next.js 16 + Tailwind CSS + framer-motion · port 3000 |
| Tests               | pytest + pytest-asyncio + httpx               |
| CI/CD               | GitHub Actions (3 pipelines)                  |
| Containerisation    | Docker                                        |
| Dataset             | Inside Airbnb Paris                           |

---

## Liens importants

| Ressource | URL |
|---|---|
| DagsHub repo | `BradleyJason/airbnb-price-predictor` |
| MLflow Registry | `models:/airbnb-price-predictor@champion` |
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
│       └── listings_clean.csv    # Output de preprocess.py (55 655 lignes, 10 features)
│                                 # Colonnes ordonnées : room_type, neighbourhood_cleansed,
│                                 # accommodates, bedrooms, bathrooms, number_of_reviews,
│                                 # review_scores_rating, availability_365, minimum_nights, price
├── src/
│   ├── preprocess.py             # load → clean_price → clean_bathrooms
│   │                             # → fill_missing → encode_categoricals → FINAL_COLUMNS order
│   ├── train.py                  # XGBoost 500 arbres + log1p(price) + MLflow logging
│   └── predict.py                # FEATURE_ORDER fixé · expm1 · modèle @champion
├── api/
│   └── main.py                   # FastAPI: GET /health  POST /predict + CORSMiddleware
├── frontend/                     # Next.js 16 (App Router)
│   ├── app/
│   │   ├── layout.tsx            # Root layout, Geist font, dark bg
│   │   ├── page.tsx              # Page principale (form + result + tooltip)
│   │   └── globals.css           # Glassmorphism, sliders, selects
│   ├── .env.local                # NEXT_PUBLIC_API_URL=http://localhost:8000
│   └── package.json
├── scripts/
│   └── set_alias.py              # Assigner manuellement l'alias "champion" sur une version
├── notebooks/
│   └── eda.ipynb                 # Full EDA (7 sections, seaborn plots)
├── tests/
│   ├── conftest.py               # Shared fixtures (raw_price_df, full_raw_df…)
│   ├── unit/
│   │   └── test_preprocess.py    # 16 tests: clean_price, clean_bathrooms,
│   │                             #           encode_categoricals
│   ├── integration/
│   │   └── test_api.py           # 4 tests: /health, /predict, 422, 500
│   │                             #   VALID_PAYLOAD = tous les 9 champs
│   └── e2e/
│       └── test_pipeline.py      # 7 tests: full preprocess() pipeline
├── .github/
│   └── workflows/
│       ├── pr-dev.yml            # PR → dev : tests unit+integration + docker build
│       ├── dev-staging.yml       # push → staging : full tests + quality gates → alias "candidate"
│       └── staging-main.yml      # push → main : alias "candidate" → "champion" + e2e
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
- [x] `data/raw/listings.csv` (86 064 lignes, 79 colonnes) — DVC tracké, remote DagsHub
- [x] `src/preprocess.py` complet : nettoyage `price` (`$`/`,`), `bathrooms_text`, imputation médiane, label-encoding
- [x] Ordre des colonnes fixé (`FINAL_COLUMNS`) pour correspondre à `FEATURE_ORDER` dans `predict.py`

### Modèle
- [x] `src/train.py` : XGBoost 500 arbres, log1p(price), cap outliers p99 (€1 700), MLflow logging complet
- [x] **R²=0.51, MAE=69€** — modèle **v3** avec alias **`champion`** sur DagsHub MLflow Registry
- [x] MLflow logging : params, MAE, R², price_cap, git_commit, dvc_data_version

### API
- [x] `api/main.py` : FastAPI avec `GET /health` et `POST /predict`
  - 9 champs obligatoires : `room_type`, `neighbourhood_cleansed`, `accommodates`, `bedrooms`, `bathrooms`, `number_of_reviews`, `review_scores_rating`, `availability_365`, `minimum_nights`
  - `CORSMiddleware` configuré (`allow_origins=["*"]` — à restreindre au domaine Vercel en prod)
- [x] `src/predict.py` : charge `models:/airbnb-price-predictor@champion`, `FEATURE_ORDER` fixé, `np.expm1()` appliqué

### Frontend (EstimAir)
- [x] Next.js 16 + Tailwind + framer-motion dans `frontend/`
- [x] Dark theme (#0a0a0f), glassmorphism cards, ambient glow
- [x] Formulaire complet (9 champs) : 2 dropdowns + 5 sliders + 2 inputs
  - Quartiers affichés par arrondissement (1er → 20e), encodage LabelEncoder envoyé à l'API
  - Sous-titre "Paris intra-muros · 20 arrondissements"
- [x] Résultat : prix estimé, comparaison vs moyenne du quartier, barre de confiance ±€69 avec tooltip interactif
- [x] Bouton "Try another"

### Tests (27 tests, tous passing ✅)
- [x] 16 tests unitaires (`clean_price`, `clean_bathrooms`, `encode_categoricals`)
- [x] 4 tests d'intégration (FastAPI avec mocks MLflow/DagsHub) — payload à 9 champs
- [x] 7 tests e2e (pipeline complet sur mini-CSV temporaire)

### CI/CD (3 pipelines)
- [x] `pr-dev.yml` : tests unit+integration + coverage + docker build
- [x] `dev-staging.yml` : full tests + quality gates (R²>0.45, MAE<80€) → alias `candidate`
- [x] `staging-main.yml` : vérification alias `candidate` → alias `champion` + smoke tests e2e
- [x] Auth MLflow CI via `MLFLOW_TRACKING_USERNAME/PASSWORD` (pas de `dagshub.init()`)
- [x] MLflow 3.x : stages dépréciés → **aliases** (`candidate` / `champion`)

### Analyse
- [x] `notebooks/eda.ipynb` : 7 sections (overview, distribution prix, catégorielles, numériques, corrélations, outliers, conclusions)

### Infrastructure
- [x] `Dockerfile` : image Python 3.11-slim, expose port 8000
- [x] `scripts/set_alias.py` : script utilitaire pour assigner un alias manuellement

---

## Encodage des features (LabelEncoder alphabétique)

### room_type
| Code | Label |
|---|---|
| 0 | Entire home/apt |
| 1 | Hotel room |
| 2 | Private room |
| 3 | Shared room |

### neighbourhood_cleansed (affiché par arrondissement, encodé alphabétiquement)
| Arrondissement | Label affiché | Code API |
|---|---|---|
| 1er | Louvre | 7 |
| 2e | Bourse | 1 |
| 3e | Temple | 17 |
| 4e | Hôtel-de-Ville | 6 |
| 5e | Panthéon | 13 |
| 6e | Luxembourg | 8 |
| 7e | Palais-Bourbon | 12 |
| 8e | Élysée | 19 |
| 9e | Opéra | 11 |
| 10e | Entrepôt | 4 |
| 11e | Popincourt | 15 |
| 12e | Reuilly | 16 |
| 13e | Gobelins | 5 |
| 14e | Observatoire | 10 |
| 15e | Vaugirard | 18 |
| 16e | Passy | 14 |
| 17e | Batignolles-Monceau | 0 |
| 18e | Buttes-Montmartre | 3 |
| 19e | Buttes-Chaumont | 2 |
| 20e | Ménilmontant | 9 |

---

## Commandes importantes

```bash
# Installation
pip install -r requirements.txt && pip install -e .

# Preprocessing
python src/preprocess.py

# Entraînement
python src/train.py

# Assigner l'alias "champion" manuellement (après un train)
python scripts/set_alias.py 3    # remplacer 3 par le numéro de version

# API locale
uvicorn api.main:app --reload
# → http://localhost:8000/docs

# Frontend local
cd frontend && npm run dev
# → http://localhost:3000

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

Fichier `frontend/.env.local` (git-ignoré) :

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
# En production : URL du backend Render
```

Secrets GitHub Actions (`Settings → Secrets → Actions`) :
- `DAGSHUB_USERNAME`
- `DAGSHUB_TOKEN`
- `MLFLOW_TRACKING_URI`

---

## Ce qui reste à faire 🔜

### Déploiement Backend sur Render (priorité 1)
- [ ] Créer un service Web Render depuis l'image Docker
- [ ] Configurer les variables d'environnement (`DAGSHUB_TOKEN`, `MLFLOW_TRACKING_URI`, `DAGSHUB_USERNAME`)
- [ ] Mettre à jour `NEXT_PUBLIC_API_URL` dans `frontend/.env.local` (et sur Vercel)
- [ ] Restreindre `allow_origins` dans `api/main.py` au domaine Vercel

### Déploiement Frontend sur Vercel (priorité 2)
- [ ] Importer le repo sur Vercel (dossier `frontend/`)
- [ ] Configurer la variable d'environnement `NEXT_PUBLIC_API_URL` sur Vercel

### README (priorité 3)
- [ ] Diagramme d'architecture (MLOps pipeline complet)
- [ ] Instructions d'installation et de déploiement
- [ ] Badges CI, coverage, modèle

### Nettoyage final
- [ ] Supprimer le dossier `.claude/` (config temporaire Claude Code)
