# STARTWISE AI — Complete System Architecture & Engineering Specification

---

## 1. Executive Architecture Overview

**STARTWISE AI** is a production-grade, enterprise-ready Intelligent Startup Validation and Franchise Recommendation Platform. It empowers founders, franchise operators, investors, and startup advisors by transforming high-dimensional business parameters into rigorous, explainable, and multi-faceted quantitative assessments.

```
[ Client Tier ]
React 18 (Vite + TypeScript) + TailwindCSS + Framer Motion + Recharts + TanStack Query
                      │
                      │ HTTPS / JSON REST API (JWT Bearer Auth)
                      ▼
[ API Gateway & Ingress Tier ]
Nginx Reverse Proxy & Static Server / Uvicorn ASGI Server
Security Middlewares: RateLimiter, RequestLogger, SecurityHeaders, TrustedHost, CORS
                      │
                      ▼
[ Application & Business Logic Tier (FastAPI) ]
  ├── Auth & RBAC Subsystem (Passlib bcrypt, PyJWT, User/Admin Roles)
  ├── Startup Lifecycle Engine (CRUD, Parameters, Historical Snapshots)
  ├── ML Inference Engine (Scikit-Learn Preprocessors & Ensemble Models)
  ├── Explainable AI Subsystem (SHAP TreeExplainer & LinearExplainer)
  ├── Franchise Recommendation Engine (KNN NearestNeighbors & Heuristic Scoring)
  ├── Marketing Strategy Generator (Dynamic Budget Allocation & Channel Scoring)
  ├── BI & Aggregated Dashboard Service (Multi-Dimensional Metric Synthesis)
  ├── Executive PDF Generation Service (ReportLab Multi-Page Canvas Engine)
  ├── Transactional Email Service (Resend API Async Client)
  └── Admin Panel & Platform Governance (Audit Logging, Model Health, System Metrics)
                      │
                      ▼
[ Persistence & Data Tier ]
  ├── Neon Serverless PostgreSQL (AsyncSQLAlchemy 2.0 / aiosqlite fallback)
  ├── Serialized ML Artifacts (joblib models, preprocessors, feature metadata)
  └── Generated PDF Report File System Cache (reports/)
```

---

## 2. Technology Stack Specification

### Frontend Architecture
- **Framework**: React 18 with TypeScript 5 (Strict mode)
- **Bundler & Dev Server**: Vite 6
- **State Management & Caching**: TanStack React Query v5 (5-minute stale-time caching, optimistic updates)
- **Styling & Design System**: TailwindCSS v3 + Shadcn/UI Glassmorphic Design Token System
- **Animations**: Framer Motion 11
- **Data Visualization**: Recharts 2 (ResponsiveContainer, AreaChart, BarChart, Divergence Impact Charts)
- **HTTP Client**: Axios with centralized request/response interceptors for JWT token injection and automatic 401 handling

### Backend Architecture
- **Runtime & Web Framework**: Python 3.12+ / FastAPI 0.115+ (Asynchronous ASGI)
- **Data Modeling & Validation**: Pydantic V2 & Pydantic Settings
- **ORM & Database Layer**: SQLAlchemy 2.0 (Async Engine via `asyncpg`, Sync Engine for schema inspection)
- **Authentication**: JWT (JSON Web Tokens) with HS256 algorithm and bcrypt password hashing
- **Machine Learning & Data Science**: Scikit-Learn, Joblib, NumPy, Pandas
- **Explainability**: SHAP (SHapley Additive exPlanations v0.52.0)
- **Document Generation**: ReportLab 4.2+ (Vector PDF canvas generation)
- **Email Delivery**: Resend REST API Client
- **Testing**: Pytest, Pytest-Asyncio, HTTPX

---

## 3. Detailed Data Flow Architecture

```
                    ┌─────────────────────────┐
                    │      Founder User       │
                    └────────────┬────────────┘
                                 │
                     1. Submit Startup Details
                                 │
                                 ▼
                     ┌────────────────────────┐
                     │   FastAPI API Router   │
                     └───────────┬────────────┘
                                 │
                     2. Validate & Authorize
                                 │
                                 ▼
                     ┌────────────────────────┐
                     │   Startup Repository   │
                     └───────────┬────────────┘
                                 │
                     3. Persist to Neon DB
                                 │
                                 ▼
                     ┌────────────────────────┐
                     │  ML Prediction Engine  │
                     └───────────┬────────────┘
                                 │
                     4. Standardize & Transform (OneHotEncoder, StandardScaler)
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
         ▼                       ▼                       ▼
┌──────────────────┐    ┌──────────────────┐   ┌──────────────────┐
│  Success Model   │    │    Risk Model    │   │    ROI Model     │
│  (RandomForest)  │    │  (DecisionTree)  │   │ (LinearRegress.) │
└────────┬─────────┘    └────────┬─────────┘   └────────┬─────────┘
         │                       │                      │
         └───────────────────────┼──────────────────────┘
                                 │
                     5. Synthesize Feasibility Score
                                 │
                                 ▼
                     ┌────────────────────────┐
                     │  Explainable AI (SHAP) │
                     └───────────┬────────────┘
                                 │
                     6. TreeExplainer / LinearExplainer Attributions
                                 │
                     7. Persist Prediction & Explanation in DB
                                 │
         ┌───────────────────────┴───────────────────────┐
         ▼                                               ▼
┌────────────────────────┐                   ┌────────────────────────┐
│  Franchise Rec Engine  │                   │ Marketing Gen Service  │
│ (NearestNeighbors KNN) │                   │  (ROI Channel Engine)  │
└────────┬───────────────┘                   └───────────┬────────────┘
         │                                               │
         └───────────────────────┬───────────────────────┘
                                 │
                     8. Business Intelligence Dashboard
                                 │
                     9. Generate Executive Investor PDF Deck
                                 │
                     10. Deliver via Resend Transactional Email
```

---

## 4. Machine Learning & XAI Subsystem

### Estimator Ensemble

1. **Business Success Probability Model**:
   - **Algorithm**: `RandomForestClassifier` (200 trees, balanced subsample weighting)
   - **Target**: Binary classification (0: Failure, 1: Success)
   - **Inference**: Probability distribution via `.predict_proba(X)[:, 1]`
   - **XAI Method**: `shap.TreeExplainer(model)`

2. **Risk Rating Model**:
   - **Algorithm**: `DecisionTreeClassifier` (Max Depth 8, Gini impurity criterion)
   - **Target**: Multiclass classification (`Low Risk`, `Medium Risk`, `High Risk`)
   - **XAI Method**: `shap.TreeExplainer(model)`

3. **Return on Investment (ROI) Model**:
   - **Algorithm**: `LinearRegression` (Ordinary Least Squares)
   - **Target**: Continuous percentage forecast ($ROI \in [-100\%, +300\%]$)
   - **XAI Method**: `shap.LinearExplainer(model, masker=Independent(...))`

4. **Market Competition Model**:
   - **Algorithm**: `RandomForestClassifier` (100 estimators)
   - **Target**: Categorical competition density (`Low`, `Medium`, `High`)
   - **XAI Method**: `shap.TreeExplainer(model)`

---

## 5. Security & Access Control Architecture

- **Defense in Depth**: Every protected endpoint enforces server-side JWT verification via FastAPI dependencies (`get_current_user`, `get_current_active_admin`).
- **Strict In-Database IDOR Isolation**: All queries filter by `user_id == current_user.id`. Cross-user access returns `403 Forbidden` or `404 Not Found`.
- **SQL Injection Prevention**: 100% parameterized queries via SQLAlchemy 2.0 ORM expressions.
- **Production HTTP Security Headers**:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: SAMEORIGIN`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `X-XSS-Protection: 1; mode=block`
- **Rate Limiting**: Sliding window in-memory rate limiter per IP address.
- **Audit Logging**: Asynchronous logging of admin actions, login attempts, analysis executions, and PDF downloads in `audit_logs` table.
