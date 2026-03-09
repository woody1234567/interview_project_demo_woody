from pydantic import BaseModel, Field
from typing import Literal, List, Optional

TxnType = Literal['CASH_IN', 'CASH_OUT', 'DEBIT', 'PAYMENT', 'TRANSFER']
RiskLevel = Literal['LOW', 'MEDIUM', 'HIGH']
ModelName = Literal['xgboost', 'decision_tree', 'logistic_regression']


class FeatureInput(BaseModel):
    step: int = Field(..., ge=1)
    type: TxnType
    amount: float = Field(..., ge=0)
    oldbalanceOrg: float
    newbalanceOrig: float
    oldbalanceDest: float
    newbalanceDest: float
    isFlaggedFraud: int = Field(0, ge=0, le=1)
    deltaOrig: float
    deltaDest: float
    isOrigBalanceZero: int = Field(..., ge=0, le=1)
    isDestBalanceZero: int = Field(..., ge=0, le=1)
    feature_version: Optional[str] = None


class PredictRequest(FeatureInput):
    model_name: Optional[ModelName] = 'xgboost'


class PredictResponse(BaseModel):
    fraud_prob: float
    risk_level: RiskLevel
    thresholds: dict
    model_version: str
    model_used: str


class BatchPredictRequest(BaseModel):
    items: List[PredictRequest]


class BatchPredictResponse(BaseModel):
    items: List[PredictResponse]
