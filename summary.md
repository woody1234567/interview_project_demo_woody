# interview_project_demo — Codebase Understanding Summary

## 1) 專案目前定位
這是一個 **Fraud Detection Demo 應用**，採用前後端分離與微服務流程：
- Frontend（Nuxt）負責輸入交易資料與顯示結果
- Feature API（FastAPI）負責 baseline 特徵轉換
- Model API（FastAPI）負責風險機率推論與風險分級

整體流程：
1. 前端送交易資料到 `feature_api`
2. `feature_api` 回傳特徵
3. 前端把特徵送到 `model_api`
4. `model_api` 回傳 `fraud_prob` 與 `risk_level`

---

## 2) 目前資料夾與角色
- `frontend/`：Nuxt 前端
- `backend/feature_api/`：特徵轉換服務
- `backend/model_api/`：模型推論服務
- `deploy/`：規劃文件（需求與設計說明）
- `models/`（專案根目錄）：目前看到 `decision_tree_pipeline.joblib`、`xgboost_pipeline.joblib`

---

## 3) Frontend 理解
### 3.1 技術與設定
- Nuxt 3 專案（`frontend/package.json`）
- 透過 `nuxt.config.ts` 設定兩個後端 base URL：
  - `NUXT_PUBLIC_FEATURE_API_BASE`（預設 `http://localhost:8001`）
  - `NUXT_PUBLIC_MODEL_API_BASE`（預設 `http://localhost:8002`）

### 3.2 主要頁面與元件
- `app/pages/index.vue`：主流程頁
  - 送出交易欄位
  - 呼叫 feature API + model API
  - 呈現預測結果或錯誤
- `app/components/TransactionForm.vue`：交易輸入表單
- `app/components/PredictionCard.vue`：預測結果卡（機率 + 風險分級）

### 3.3 功能狀態
- MVP 已可完成單筆預測流程
- UI 已具備 loading/error/result 狀態顯示

---

## 4) Feature API 理解（`backend/feature_api`）
### 4.1 端點
- `GET /health`
- `POST /v1/features/transform`
- `POST /v1/features/transform-batch`

### 4.2 目前實作特徵
對齊 baseline notebook 的欄位與衍生特徵：
- 原始欄位：`step,type,amount,oldbalanceOrg,newbalanceOrig,oldbalanceDest,newbalanceDest,isFlaggedFraud`
- 衍生欄位：
  - `deltaOrig = oldbalanceOrg - newbalanceOrig`
  - `deltaDest = newbalanceDest - oldbalanceDest`
  - `isOrigBalanceZero`
  - `isDestBalanceZero`
- 回傳 `feature_version=baseline_v1`

### 4.3 CORS
已加上 `CORSMiddleware`，預設允許：
- `http://localhost:3000`
- `http://127.0.0.1:3000`

---

## 5) Model API 理解（`backend/model_api`）
### 5.1 端點
- `GET /health`
- `POST /v1/model/predict`
- `POST /v1/model/predict-batch`

### 5.2 推論邏輯
- 預設模型版本：`baseline_xgboost_v1`
- 閾值：`t_mid=0.10`、`t_high=0.30`
- 分級規則：
  - `HIGH`: `prob >= t_high`
  - `MEDIUM`: `t_mid <= prob < t_high`
  - `LOW`: `prob < t_mid`

### 5.3 XGBoost 載入策略
- 會嘗試載入 `backend/model_api/models/xgboost_model.json`
- 若沒有可用 artifact，會 fallback 到 heuristic scorer
- `/health` 會顯示 runtime 狀態（xgboost 或 fallback）

### 5.4 CORS
已加上 `CORSMiddleware`，同 feature API。

---

## 6) 目前觀察到的關鍵一致性重點
1. **模型 artifact 位置不一致風險**
   - 根目錄目前有 `models/xgboost_pipeline.joblib`
   - 但 model_api 目前預期的是 `backend/model_api/models/xgboost_model.json`
   - 代表現在多半會走 fallback（除非你已額外放 json artifact）

2. **文件與現況可再同步**
   - `backend/README.md` 仍提到 fallback 為主（與你要 XGBoost 預設一致，但可補充 artifact 格式）
   - `deploy/*.md` 屬規劃文件，與實作大方向一致

3. **前端結構採 `app/` 目錄**
   - 前端目前檔案在 `frontend/app/...`
   - 與舊規劃文件中 `pages/`、`components/` 根層建議略有差異，但功能可運作

---

## 7) 我對目前 codebase 的總結
這個專案已完成可運作的 **MVP 端到端骨架**（Nuxt -> Feature API -> Model API）。
下一個最關鍵的提升是：
- 將你訓練好的 XGBoost artifact 轉成並接上 `model_api` 真實推論格式（或調整 model_api 直接讀 `.joblib` pipeline），讓 runtime 穩定使用真實模型而非 fallback。
