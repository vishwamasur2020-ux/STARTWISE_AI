# STARTWISE AI 🚀

**Enterprise-Ready Intelligent Startup Validation & Franchise Recommendation Platform**

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3-61DAFB.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6.svg)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-6.0-646CFF.svg)](https://vitejs.dev/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.4+-F7931E.svg)](https://scikit-learn.org/)
[![SHAP](https://img.shields.io/badge/SHAP-0.52.0-blueviolet.svg)](https://shap.readthedocs.io/)
[![PostgreSQL](https://img.shields.io/badge/Neon-PostgreSQL-336791.svg)](https://neon.tech)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 1. Project Overview & Problem Statement

Aspiring entrepreneurs and early-stage founders face an alarming **90% startup failure rate** primarily caused by lack of market demand, miscalculated capital requirements, poor channel execution, and unexpected competitive intensity.

**STARTWISE AI** solves this problem by providing an automated, mathematical, and explainable **AI Validation Pipeline**:
- Evaluates startup viability before founders risk capital.
- Delivers calibrated multi-model forecasts: **Success Probability**, **Risk Rating**, **Estimated ROI**, **Market Competition**, and **Business Score**.
- Explains every outcome transparently using **Explainable AI (SHAP)**.
- Suggests personalized alternative **Franchise Opportunities** using hybrid KNN matching.
- Formulates optimized **Multi-Channel Go-To-Market Strategies** with budget distributions.
- Compiles professional **Investor PDF Decks** with one-click transactional email delivery.
- Enforces enterprise governance with a comprehensive **Admin Monitoring Panel**.

---

## 2. System Architecture & Tech Stack

```
Frontend:   React 18 + Vite 6 + TypeScript + TailwindCSS + Framer Motion + Recharts + TanStack Query
Backend:    FastAPI + Python 3.12 + SQLAlchemy 2.0 + Pydantic V2 + Joblib + SHAP + ReportLab
Database:   Neon Serverless PostgreSQL (Async Engine with asyncpg)
ML Models:  RandomForestClassifier (Success), DecisionTreeClassifier (Risk), LinearRegression (ROI), KNN (Franchise)
Security:   JWT Authentication (HS256), bcrypt hashing, RBAC, IDOR scoping, Security Headers
Deploy:     Docker, Multi-stage Nginx container, Uvicorn ASGI Server
```

---

## 3. End-to-End System Workflow

```
1. Registration & JWT Authentication (bcrypt hashing)
2. Startup Creation (parameters: capital, revenue, expenses, sector, location, experience)
3. Offline-Trained Machine Learning Inference
   ├── Business Success Probability (%)
   ├── Multiclass Risk Level (Low, Medium, High)
   ├── Continuous ROI Projection (%)
   ├── Sector Competition Density (Low, Medium, High)
   └── Synthesized Business Feasibility Score (0–100)
4. Explainable AI (SHAP TreeExplainer & LinearExplainer Attributions)
5. AI Franchise Matcher (Top 5 Ranked Franchise Profiles)
6. Automated Marketing Strategy Generator (Channel Budget Allocations & CAC Projections)
7. Dynamic Business Intelligence Dashboard (Interactive Recharts Visualizations)
8. Multi-Page Investor PDF Report Generation (ReportLab Canvas)
9. Transactional Email Dispatch (Resend API)
10. Admin Governance (User Management, Audit Logs, ML Health Monitoring)
```

---

## 4. Machine Learning & Explainable AI (XAI) Architecture

| Model | Machine Learning Algorithm | Target Variable | Explainability Method |
|---|---|---|---|
| **Success Probability** | `RandomForestClassifier` (200 Trees) | Binary Outcome ($P \in [0, 1]$) | `shap.TreeExplainer` |
| **Risk Rating** | `DecisionTreeClassifier` (Depth 8) | Categorical (`Low`, `Med`, `High`) | `shap.TreeExplainer` |
| **Projected ROI** | `LinearRegression` (OLS) | Continuous Percentage | `shap.LinearExplainer` |
| **Competition Density**| `RandomForestClassifier` (100 Trees) | Categorical (`Low`, `Med`, `High`) | `shap.TreeExplainer` |
| **Franchise Matching** | `NearestNeighbors` (KNN Cosine) | Top-5 Similarity Ranking | Distance Proximity Metrics |

---

## 5. Project Directory Structure

```
STARTWISE_AI/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/    # REST Endpoints (auth, startups, predictions, xai, admin, etc.)
│   │   ├── auth/                # JWT dependencies, security, password hashing
│   │   ├── core/                # Pydantic Settings, structured logging, model manager
│   │   ├── database/            # SQLAlchemy session, engine, declarative base
│   │   ├── middlewares/         # Rate limiting, request logging, security headers
│   │   ├── ml/artifacts/        # Serialized joblib models & feature metadata
│   │   ├── models/              # SQLAlchemy database entities
│   │   ├── repositories/        # In-database CRUD data access layer
│   │   ├── schemas/             # Pydantic V2 DTOs & validation schemas
│   │   ├── services/            # Core business logic (prediction, xai, franchise, marketing)
│   │   └── tests/               # Pytest unit & integration test suite (48 tests)
│   ├── alembic/                 # Database migration versions
│   ├── reports/                 # Local filesystem PDF storage directory
│   ├── requirements.txt         # Pinned Python production dependencies
│   ├── Dockerfile               # Production multi-stage Python container
│   └── run.py                   # Local development runner
│
├── frontend/
│   ├── src/
│   │   ├── components/          # Glassmorphic UI components, modals, charts, layout
│   │   ├── hooks/               # TanStack Query custom hooks
│   │   ├── pages/               # Route views (Dashboard, Validation, Franchise, Admin, etc.)
│   │   ├── services/            # Axios API clients
│   │   └── types/               # TypeScript type definitions
│   ├── nginx.conf               # Production Nginx reverse proxy & SPA fallback
│   ├── Dockerfile               # Multi-stage frontend Docker build
│   └── package.json             # NPM package manifest
│
├── xai/
│   └── README.md                # Academic & viva documentation on SHAP theory
├── docker-compose.yml           # Full-stack container orchestration
├── .env.example                 # Comprehensive environment variable template
├── PROJECT_ARCHITECTURE.md      # Detailed system engineering specification
├── VIVA_NOTES.md                # Academic viva defense question & answer guide
├── FINAL_TEST_REPORT.md         # Final test execution & verification report
├── DEPLOYMENT.md                # Cloud deployment runbook
└── README.md                    # Main project documentation
```

---

## 6. Installation & Quick Start

### Prerequisites
- **Python 3.12+**
- **Node.js 20+** / **npm 10+**
- **Neon PostgreSQL Account** or local PostgreSQL instance

### Option A: Local Development Setup

#### 1. Backend Setup
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env with your DATABASE_URL and JWT_SECRET_KEY

# Start backend server
python run.py
```
- Backend runs at: `http://localhost:8000`
- Interactive API Docs at: `http://localhost:8000/api/docs`
- Health Check at: `http://localhost:8000/health`

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
- Frontend application runs at: `http://localhost:5173`

---

### Option B: Containerized Deployment (Docker Compose)

```bash
# Copy and configure environment variables
cp .env.example backend/.env

# Build and start all services
docker compose build
docker compose up -d
```
- Full application accessible at: `http://localhost:80`
- API Backend accessible at: `http://localhost:8000`

---

## 7. Running the Automated Test Suite

```bash
# Run all 48 backend integration & unit tests
cd backend
venv\Scripts\python -m pytest -v app/tests

# Run frontend TypeScript type checking
cd frontend
npx tsc --noEmit

# Run frontend production build
npm run build
```

---

## 8. Demonstration Scenario

1. **Authentication**: Sign up a new founder account or log in as Admin (`admin@startwise.ai`).
2. **Startup Concept Creation**:
   - **Name**: ChaiCraft Artisanal Tea Cafe
   - **Category**: Food & Beverage
   - **Location**: Bengaluru
   - **Investment**: ₹12,00,000
   - **Monthly Revenue**: ₹3,50,000
   - **Monthly Expenses**: ₹2,10,000
   - **Experience**: 4 Years
3. **ML Prediction Engine**: Generates live Success Probability (86.4%), Risk Rating (Low Risk), Estimated ROI (38.2%), and Business Score (88.1).
4. **Explainable AI (XAI)**: Click *"Why this result?"* to inspect exact SHAP attributions, positive profit margin drivers, and local competition resistance factors.
5. **Franchise Matching**: View top 5 compatible franchises matching the ₹12L capital budget.
6. **Marketing Strategy**: Review algorithmic multi-channel budget breakdown (Instagram Ads, Local Food Bloggers, In-Store QR Campaigns).
7. **Executive Export**: Download the multi-page vector investor PDF or dispatch it directly to email.

---

## 9. Security & Governance

- **Zero Plaintext Secrets**: Passwords hashed with salted bcrypt (cost factor 12).
- **IDOR Protection**: In-database tenant scoping on all user-owned records.
- **Enterprise RBAC**: Server-side role validation for all administrative interfaces.
- **Defense in Depth**: Automatic security headers, CORS origin whitelisting, and sliding-window rate limiting.

---

## 10. License

This project is licensed under the **MIT License**.