# Backend Services (FastAPI MVP)

## Services
- `feature_api`: 對齊 `baseline_model_revised.ipynb` 的 baseline 特徵轉換
- `model_api`: 接收特徵後輸出 `fraud_prob` 與 `risk_level`

## Run (feature api)
```bash
cd backend/feature_api
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

## Run (model api)
```bash
cd backend/model_api
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002
```

## Endpoints
### feature-api
- `GET /health`
- `POST /v1/features/transform`
- `POST /v1/features/transform-batch`

### model-api
- `GET /health`
- `POST /v1/model/predict`
- `POST /v1/model/predict-batch`

## Notes
model-api 目前會嘗試載入專案根目錄的三個 joblib 模型：
1. `models/xgboost_pipeline.joblib`
2. `models/decision_tree_pipeline.joblib`
3. `models/logistic_regression_pipeline.joblib`

前端可在 `POST /v1/model/predict` 的 request body 指定：
- `model_name`: `xgboost` | `decision_tree` | `logistic_regression`

若指定模型不可用，會優先回退到已載入的 `xgboost`，再回退到其他可用模型；若都不可用，才退回 heuristic fallback scorer。
