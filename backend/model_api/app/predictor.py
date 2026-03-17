from __future__ import annotations

import json
import os
import warnings
from pathlib import Path
from typing import Dict, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from .schemas import RiskLevel


MODEL_VERSION = os.getenv('MODEL_VERSION', 'baseline_multi_model_v1')
T_MID = float(os.getenv('T_MID', '0.10'))
T_HIGH = float(os.getenv('T_HIGH', '0.30'))

MODEL_API_DIR = Path(__file__).resolve().parents[1]
METADATA_PATH = MODEL_API_DIR / 'models' / 'metadata.json'
PROJECT_ROOT = Path(__file__).resolve().parents[3]

MODEL_FILES = {
    'xgboost': PROJECT_ROOT / 'models' / 'xgboost_pipeline.joblib',
    'decision_tree': PROJECT_ROOT / 'models' / 'decision_tree_pipeline.joblib',
    'logistic_regression': PROJECT_ROOT / 'models' / 'logistic_regression_pipeline.joblib',
}


def load_metadata() -> Dict:
    if METADATA_PATH.exists():
        return json.loads(METADATA_PATH.read_text(encoding='utf-8'))
    return {
        'note': 'No trained joblib artifact found. Using heuristic fallback scorer.',
        'model_files': {k: str(v) for k, v in MODEL_FILES.items()},
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


class MultiModelScorer:
    def __init__(self) -> None:
        self.models: Dict[str, object] = {}
        self.model_paths: Dict[str, str] = {}
        self.load_errors: Dict[str, str] = {}
        self.runtime_model = 'fallback-heuristic'

        try:
            import joblib  # type: ignore
            import pandas as pd  # type: ignore
            self._pd = pd

            for name, path in MODEL_FILES.items():
                if path.exists():
                    try:
                        with warnings.catch_warnings():
                            warnings.filterwarnings('ignore', category=UserWarning, module='xgboost')
                            model = joblib.load(path)
                        if not hasattr(model, 'predict_proba'):
                            raise ValueError('predict_proba not found')
                        self.models[name] = model
                        self.model_paths[name] = str(path)
                    except Exception as e:
                        self.load_errors[name] = str(e)
                else:
                    self.load_errors[name] = f'file not found: {path}'

            if 'xgboost' in self.models:
                self.runtime_model = 'xgboost'
            elif self.models:
                self.runtime_model = next(iter(self.models.keys()))
        except Exception as e:
            self.load_errors['global'] = str(e)

    @property
    def enabled(self) -> bool:
        return len(self.models) > 0

    def score(self, features: Dict, model_name: Optional[str] = None) -> tuple[float, str]:
        row = dict(features)
        row.pop('feature_version', None)
        row.pop('model_name', None)

        if not self.enabled:
            return fallback_score(row), 'fallback-heuristic'

        selected = model_name or 'xgboost'
        model = self.models.get(selected)
        used_name = selected

        if model is None:
            if 'xgboost' in self.models:
                model = self.models['xgboost']
                used_name = 'xgboost'
            else:
                used_name = next(iter(self.models.keys()))
                model = self.models[used_name]

        X = self._pd.DataFrame([row])
        pred = float(model.predict_proba(X)[:, 1][0])
        return max(0.0, min(1.0, pred)), used_name


SCORER = MultiModelScorer()


def score(features: Dict, model_name: Optional[str] = None) -> tuple[float, str]:
    return SCORER.score(features, model_name=model_name)


def risk_level(prob: float) -> RiskLevel:
    if prob >= T_HIGH:
        return 'HIGH'
    if prob >= T_MID:
        return 'MEDIUM'
    return 'LOW'
