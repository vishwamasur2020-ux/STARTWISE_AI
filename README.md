# STARTWISE AI 🚀

**Intelligent Startup Validation & Franchise Recommendation System**

> AI-powered platform for aspiring entrepreneurs to validate startup ideas, predict ROI, assess risks, and find franchise opportunities.

---

## Tech Stack

| Layer       | Technology |
|-------------|-----------|
| Frontend    | React 19, Vite, TailwindCSS, Framer Motion, Recharts |
| Backend     | FastAPI, Python 3.12, SQLAlchemy 2.0, Alembic |
| Database    | Neon PostgreSQL (serverless) |
| ML          | Scikit-Learn (Random Forest, Decision Tree, Linear Regression, KNN) |
| Auth        | JWT Access + Refresh Token |
| Deploy      | Docker, Docker Compose |

---

## Project Structure

```
STARTWISE_AI/
├── backend/                  # FastAPI application
│   ├── app/
│   │   ├── api/v1/           # REST API endpoints
│   │   ├── core/             # Config, security, logging
│   │   ├── database/         # SQLAlchemy session
│   │   ├── models/           # ORM models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   ├── repositories/     # Data access layer
│   │   ├── ml/               # ML models + trainers
│   │   ├── auth/             # JWT dependencies
│   │   └── middlewares/      # Rate limiter, logger
│   ├── alembic/              # DB migrations
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                 # React application
│   ├── src/
│   │   ├── components/       # UI + Layout components
│   │   ├── pages/            # Route pages
│   │   ├── hooks/            # Custom React hooks
│   │   ├── services/         # API service layer
│   │   ├── store/            # Zustand state
│   │   └── types/            # TypeScript types
│   ├── tailwind.config.js
│   └── Dockerfile
│
└── docker-compose.yml        # Full stack orchestration
```

---

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 22+
- Neon PostgreSQL account

### 1. Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your Neon DATABASE_URL and JWT_SECRET_KEY

# Run migrations
alembic upgrade head

# Start server
python run.py
```

Backend runs at: http://localhost:8000
API Docs at: http://localhost:8000/api/docs

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: http://localhost:5173

### 3. Docker (Full Stack)

```bash
# Edit backend/.env with real credentials first
docker-compose up --build
```

---

## API Endpoints (Step 1)

| Method | Endpoint              | Description |
|--------|-----------------------|-------------|
| POST   | /api/v1/auth/register | Register user |
| POST   | /api/v1/auth/login    | Login + get tokens |
| POST   | /api/v1/auth/refresh  | Refresh access token |
| GET    | /api/v1/auth/me       | Get current user |
| GET    | /api/v1/users/profile | Get profile |
| PATCH  | /api/v1/users/profile | Update profile |
| GET    | /health               | Health check |

---

## VTU Major Project — Module Steps

| Step | Module |
|------|--------|
| ✅ 1  | Project Initialization (current) |
| 2    | Startup Validation Form |
| 3    | ML Prediction Engine |
| 4    | Franchise Recommendation |
| 5    | Marketing Strategy |
| 6    | Analytics Dashboard |
| 7    | PDF Report Generator |

---

## License

Academic project for VTU Computer Science (AI & ML) Major Project, 2025-26.