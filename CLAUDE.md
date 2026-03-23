# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A fraud detection demo with three independent services:
- **Frontend** (`frontend/`): Nuxt 4 app with `@nuxt/ui` + Tailwind CSS 4
- **Feature API** (`backend/feature_api/`): FastAPI service for feature engineering
- **Model API** (`backend/model_api/`): FastAPI service for ML inference

**Request flow:** Frontend → Feature API (`/v1/features/transform`) → Frontend → Model API (`/v1/model/predict`) → Frontend displays result.

## Running Services Locally

### Backend (requires Python 3.12 + `uv`)

```bash
# Feature API — runs on http://localhost:8001
cd backend/feature_api
uv run fastapi dev app/main.py --port 8001

# Model API — runs on http://localhost:8002
cd backend/model_api
uv run fastapi dev app/main.py --port 8002
```

### Frontend (requires Node.js + pnpm)

```bash
cd frontend
pnpm install
pnpm dev   # runs on http://localhost:3000
```

### Environment Variables (Frontend)

```
NUXT_PUBLIC_FEATURE_API_BASE=http://localhost:8001
NUXT_PUBLIC_MODEL_API_BASE=http://localhost:8002
```

These default to the above values in `nuxt.config.ts` — no `.env` needed for local dev.

## Architecture Notes

### Model Loading (model_api)

`backend/model_api/app/predictor.py` loads three `.joblib` sklearn pipelines at startup from a `models/` directory. Path resolution:
1. Reads `MODELS_DIR` env var if set
2. Falls back to `<project_root>/models/` (local dev: 3 levels up from `predictor.py`)
3. Falls back to `<model_api_root>/models/` (Docker: 2 levels up)
4. Ultimate fallback: `/app/models/`

In local dev, the `models/` directory at the **project root** is used automatically. The three expected files are `xgboost_pipeline.joblib`, `decision_tree_pipeline.joblib`, and `logistic_regression_pipeline.joblib`. If missing, the API falls back to a heuristic scorer — check `/health` to confirm which is active.

The model also reads `backend/model_api/models/metadata.json` for metadata. The `models/` directory under `model_api/` also contains copies of the joblib files (for Docker builds).

### Risk Thresholds

Configurable via env vars `T_MID` (default `0.10`) and `T_HIGH` (default `0.30`):
- `LOW`: prob < 0.10
- `MEDIUM`: 0.10 ≤ prob < 0.30
- `HIGH`: prob ≥ 0.30

### Frontend Structure

The frontend uses Nuxt 4 with `future: { compatibilityVersion: 4 }`, so pages/components live under `frontend/app/` (not project root). Key files:
- `app/pages/index.vue` — main prediction flow
- `app/components/TransactionForm.vue` — transaction input
- `app/components/PredictionCard.vue` — result display

### Dependency Management

Both backend services use `uv` with locked dependencies (`uv.lock`). To add a dependency:
```bash
cd backend/<service>
uv add <package>
```

### Docker

Each service has its own `Dockerfile` (multi-stage, `uv` builder + `python:3.12-slim`). Both expose port `8080`. For the model_api Docker build, the `models/` directory must be present inside `backend/model_api/` (copy from project root before building).
