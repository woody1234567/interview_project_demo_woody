import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .schemas import (
    FeatureInput,
    PredictResponse,
    BatchFeatureInput,
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
        'model_path': SCORER.model_path,
        'model_loaded': SCORER.enabled,
        'load_error': SCORER.load_error,
        'metadata': metadata,
    }


@app.post('/v1/model/predict', response_model=PredictResponse)
def predict(payload: FeatureInput):
    prob = score(payload.model_dump())
    return PredictResponse(
        fraud_prob=prob,
        risk_level=risk_level(prob),
        thresholds={'t_mid': T_MID, 't_high': T_HIGH},
        model_version=MODEL_VERSION,
    )


@app.post('/v1/model/predict-batch', response_model=BatchPredictResponse)
def predict_batch(payload: BatchFeatureInput):
    items = []
    for row in payload.items:
        prob = score(row.model_dump())
        items.append(
            PredictResponse(
                fraud_prob=prob,
                risk_level=risk_level(prob),
                thresholds={'t_mid': T_MID, 't_high': T_HIGH},
                model_version=MODEL_VERSION,
            )
        )
    return BatchPredictResponse(items=items)
