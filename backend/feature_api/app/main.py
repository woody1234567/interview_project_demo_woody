import os

from typing import Annotated
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware

from .schemas import (
    TransactionInput,
    FeatureOutput,
    BatchTransactionInput,
    BatchFeatureOutput,
)
from .transformers import transform_single


app = FastAPI(title='feature-api', version='0.1.0')

allowed_origins = os.getenv(
    'ALLOWED_ORIGINS',
    'http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,https://frauddetection.zeabur.app'
).split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins if origin.strip()],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/health')
def health() -> dict[str, str]:
    return {'status': 'ok', 'service': 'feature-api'}


@app.post('/v1/features/transform')
def transform(payload: Annotated[TransactionInput, Body()]) -> FeatureOutput:
    return transform_single(payload)


@app.post('/v1/features/transform-batch')
def transform_batch(payload: Annotated[BatchTransactionInput, Body()]) -> BatchFeatureOutput:
    return BatchFeatureOutput(items=[transform_single(x) for x in payload.items])
