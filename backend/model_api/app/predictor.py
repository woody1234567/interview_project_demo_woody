from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Optional


MODEL_VERSION = os.getenv('MODEL_VERSION', 'baseline_xgboost_v1')
T_MID = float(os.getenv('T_MID', '0.10'))
T_HIGH = float(os.getenv('T_HIGH', '0.30'))

# backend/model_api/app -> backend/model_api
MODEL_API_DIR = Path(__file__).resolve().parents[1]
METADATA_PATH = MODEL_API_DIR / 'models' / 'metadata.json'

# backend/model_api/app -> backend/model_api -> backend -> project root
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_XGB_JOBLIB = PROJECT_ROOT / 'models' / 'xgboost_pipeline.joblib'
DEFAULT_DT_JOBLIB = PROJECT_ROOT / 'models' / 'decision_tree_pipeline.joblib'


def load_metadata() -> Dict:
    if METADATA_PATH.exists():
        return json.loads(METADATA_PATH.read_text(encoding='utf-8'))
    return {
        'note': 'No trained joblib artifact found. Using heuristic fallback scorer.',
        'default_model_candidates': [str(DEFAULT_XGB_JOBLIB), str(DEFAULT_DT_JOBLIB)],
    }


def _sigmoid(x: float) -> float:
    import math
    return 1.0 / (1.0 + math.exp(-x))


def fallback_score(features: Dict) -> float:
    amount = float(features.get('amount', 0.0))
    delta_orig = float(features.get('deltaOrig', 0.0))
    delta_dest = float(features.get('deltaDest', 0.0))
    flagged = int(features.get('isFlaggedFraud', 0))
    tx_type = str(features.get('type', ''))

    z = -6.2
    z += 0.000003 * amount
    z += 0.000002 * max(delta_orig, 0.0)
    z += 0.000002 * max(delta_dest, 0.0)
    z += 2.2 * flagged
    if tx_type in {'TRANSFER', 'CASH_OUT'}:
        z += 0.7

    return max(0.0, min(1.0, _sigmoid(z)))


class JoblibScorer:
    def __init__(self) -> None:
        self.model: Optional[object] = None
        self.enabled = False
        self.runtime_model = 'fallback-heuristic'
        self.model_path: Optional[str] = None
        self.load_error: Optional[str] = None

        model_path_env = os.getenv('MODEL_PATH', '').strip()
        candidates = [Path(model_path_env)] if model_path_env else [DEFAULT_XGB_JOBLIB, DEFAULT_DT_JOBLIB]

        try:
            import joblib  # type: ignore
            import pandas as pd  # type: ignore
            self._pd = pd

            for p in candidates:
                if p.exists():
                    self.model = joblib.load(p)
                    if not hasattr(self.model, 'predict_proba'):
                        raise ValueError(f'Model at {p} has no predict_proba method')
                    self.enabled = True
                    self.model_path = str(p)
                    self.runtime_model = p.stem
                    self.load_error = None
                    return

            self.load_error = f'No model file found in candidates: {[str(c) for c in candidates]}'
        except Exception as e:
            self.enabled = False
            self.load_error = str(e)

    def score(self, features: Dict) -> float:
        if not self.enabled or self.model is None:
            return fallback_score(features)

        row = dict(features)
        row.pop('feature_version', None)
        X = self._pd.DataFrame([row])
        pred = float(self.model.predict_proba(X)[:, 1][0])
        return max(0.0, min(1.0, pred))


SCORER = JoblibScorer()


def score(features: Dict) -> float:
    return SCORER.score(features)


def risk_level(prob: float) -> str:
    if prob >= T_HIGH:
        return 'HIGH'
    if prob >= T_MID:
        return 'MEDIUM'
    return 'LOW'
