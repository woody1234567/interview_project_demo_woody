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
model-api 目前會優先載入專案根目錄的 joblib 模型：
1. `models/xgboost_pipeline.joblib`（預設優先）
2. `models/decision_tree_pipeline.joblib`（次要備援）

若兩者都不可用，才會退回 heuristic fallback scorer。

可用環境變數覆蓋模型路徑：
- `MODEL_PATH=/absolute/or/relative/path/to/model.joblib`
