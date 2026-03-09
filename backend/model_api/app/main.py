import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .schemas import (
    PredictRequest,
    PredictResponse,
    BatchPredictRequest,
    BatchPredictResponse,
)
from .predictor import (
    MODEL_VERSION,
    T_MID,
    T_HIGH,
    load_metadata,
    score,
    risk_level,
    SCORER,
)


app = FastAPI(title='model-api', version='0.1.0')
metadata = load_metadata()

allowed_origins = os.getenv(
    'ALLOWED_ORIGINS',
    'http://localhost:3000,http://127.0.0.1:3000'
).split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins if origin.strip()],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/health')
def health():
    return {
        'status': 'ok',
        'service': 'model-api',
        'model_version': MODEL_VERSION,
        'runtime_model': SCORER.runtime_model,
        'model_loaded': SCORER.enabled,
        'loaded_models': list(SCORER.models.keys()),
        'model_paths': SCORER.model_paths,
        'load_errors': SCORER.load_errors,
        'metadata': metadata,
    }


@app.post('/v1/model/predict', response_model=PredictResponse)
def predict(payload: PredictRequest):
    prob, used_model = score(payload.model_dump(), model_name=payload.model_name)
    return PredictResponse(
        fraud_prob=prob,
        risk_level=risk_level(prob),
        thresholds={'t_mid': T_MID, 't_high': T_HIGH},
        model_version=MODEL_VERSION,
        model_used=used_model,
    )


@app.post('/v1/model/predict-batch', response_model=BatchPredictResponse)
def predict_batch(payload: BatchPredictRequest):
    items = []
    for row in payload.items:
        prob, used_model = score(row.model_dump(), model_name=row.model_name)
        items.append(
            PredictResponse(
                fraud_prob=prob,
                risk_level=risk_level(prob),
                thresholds={'t_mid': T_MID, 't_high': T_HIGH},
                model_version=MODEL_VERSION,
                model_used=used_model,
            )
        )
    return BatchPredictResponse(items=items)
