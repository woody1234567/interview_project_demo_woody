# UV Migration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Migrate `feature_api` and `model_api` from pip + `.venv` to `uv` with `pyproject.toml` + `uv.lock`, using Python 3.12.

**Architecture:** Each API becomes an independent `uv` project with its own `pyproject.toml` declaring dependencies and `requires-python = ">=3.12"`. The old `.venv` is deleted and rebuilt by `uv sync`. No shared workspace — each API is self-contained.

**Tech Stack:** uv 0.10+, Python 3.12 (auto-downloaded by uv), FastAPI, uvicorn

---

### Task 1: Migrate `feature_api`

**Files:**
- Create: `backend/feature_api/pyproject.toml`
- Delete: `backend/feature_api/.venv/` (entire directory)
- Keep: `backend/feature_api/requirements.txt` (renamed to `requirements.txt.bak` for reference)

**Step 1: Remove old venv**

```bash
cd backend/feature_api
rm -rf .venv
```

Expected: `.venv/` directory gone.

**Step 2: Create `pyproject.toml`**

Create `backend/feature_api/pyproject.toml` with this content:

```toml
[project]
name = "feature-api"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi==0.115.0",
    "uvicorn[standard]==0.30.6",
    "pydantic==2.9.2",
]

[tool.uv]
dev-dependencies = []
```

**Step 3: Install dependencies with uv**

```bash
cd backend/feature_api
uv sync --python 3.12
```

Expected output: uv downloads Python 3.12, creates `.venv`, installs packages, generates `uv.lock`.

**Step 4: Verify the venv works**

```bash
cd backend/feature_api
uv run python -c "import fastapi, uvicorn, pydantic; print('OK')"
```

Expected: `OK`

**Step 5: Verify server starts**

```bash
cd backend/feature_api
uv run uvicorn app.main:app --port 8001 &
sleep 2
curl -s http://localhost:8001/health
kill %1
```

Expected: JSON health response (no error).

**Step 6: Rename old requirements file**

```bash
cd backend/feature_api
mv requirements.txt requirements.txt.bak
```

**Step 7: Commit**

```bash
git add backend/feature_api/pyproject.toml backend/feature_api/uv.lock backend/feature_api/requirements.txt.bak
git commit -m "feat: migrate feature_api to uv with Python 3.12"
```

---

### Task 2: Migrate `model_api`

**Files:**
- Create: `backend/model_api/pyproject.toml`
- Delete: `backend/model_api/.venv/` (entire directory)
- Keep: `backend/model_api/requirements.txt` (renamed to `requirements.txt.bak`)

**Step 1: Remove old venv**

```bash
cd backend/model_api
rm -rf .venv
```

Expected: `.venv/` directory gone.

**Step 2: Create `pyproject.toml`**

Create `backend/model_api/pyproject.toml` with this content:

```toml
[project]
name = "model-api"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi==0.115.0",
    "uvicorn[standard]==0.30.6",
    "pydantic==2.9.2",
    "pandas==2.2.3",
    "joblib==1.4.2",
    "scikit-learn==1.6.1",
    "xgboost==2.1.1",
]

[tool.uv]
dev-dependencies = []
```

**Step 3: Install dependencies with uv**

```bash
cd backend/model_api
uv sync --python 3.12
```

Expected: uv reuses the already-downloaded Python 3.12, creates `.venv`, installs all packages including xgboost.

**Step 4: Verify all packages load**

```bash
cd backend/model_api
uv run python -c "import fastapi, uvicorn, pydantic, pandas, joblib, sklearn, xgboost; print('OK')"
```

Expected: `OK`

**Step 5: Verify models load correctly**

```bash
cd backend/model_api
uv run python -c "
from app.predictor import SCORER
print('enabled:', SCORER.enabled)
print('models:', list(SCORER.models.keys()))
print('errors:', SCORER.load_errors)
"
```

Expected:
```
enabled: True
models: ['xgboost', 'decision_tree', 'logistic_regression']
errors: {}
```

**Step 6: Verify server starts**

```bash
cd backend/model_api
uv run uvicorn app.main:app --port 8002 &
sleep 2
curl -s http://localhost:8002/health | python3 -m json.tool
kill %1
```

Expected: JSON with `"model_loaded": true` and `"runtime_model": "xgboost"`.

**Step 7: Rename old requirements file**

```bash
cd backend/model_api
mv requirements.txt requirements.txt.bak
```

**Step 8: Commit**

```bash
git add backend/model_api/pyproject.toml backend/model_api/uv.lock backend/model_api/requirements.txt.bak
git commit -m "feat: migrate model_api to uv with Python 3.12"
```

---

### Task 3: Update README

**Files:**
- Modify: `backend/README.md`

**Step 1: Read current README**

Read `backend/README.md` to see what startup instructions exist.

**Step 2: Update startup instructions**

Replace the old `pip install` + `uvicorn` commands with `uv` equivalents:

```markdown
## feature_api

```bash
cd backend/feature_api
uv sync          # first time: installs deps + creates .venv
uv run uvicorn app.main:app --reload --port 8001
```

## model_api

```bash
cd backend/model_api
uv sync          # first time: installs deps + creates .venv
uv run uvicorn app.main:app --reload --port 8002
```
```

**Step 3: Commit**

```bash
git add backend/README.md
git commit -m "docs: update backend startup instructions for uv"
```
