# STARTWISE AI — Production Deployment & DevOps Runbook

---

## 1. Deployment Architecture Overview

STARTWISE AI is designed as a cloud-native, horizontally scalable 3-tier architecture:

```
[ DNS & CDN Tier ]
Cloudflare / Custom Domain (SSL/TLS Termination)
         │
         ├── Frontend Client ──► Vercel / Netlify / Nginx Container (Static SPA)
         │
         └── API Gateway     ──► Render / Railway / AWS ECS / DigitalOcean (FastAPI Uvicorn)
                                      │
                                      ├── Neon Serverless PostgreSQL (Database)
                                      ├── Email Delivery (SMTP / Resend Provider Architecture)
                                      └── Local / Cloud Object Storage (PDF Decks)
```

---

## 2. Docker & Containerized Deployment

### Multi-Container Deployment with Docker Compose

1. **Configure Environment Variables**:
   Copy `.env.example` to `backend/.env` and update values:
   ```bash
   cp .env.example backend/.env
   ```

2. **Build and Run All Services**:
   ```bash
   docker compose build
   docker compose up -d
   ```

3. **Verify Service Health**:
   - Backend API Health: `http://localhost:8000/health`
   - Detailed Health Check: `http://localhost:8000/api/health`
   - Interactive Swagger Docs: `http://localhost:8000/api/docs`
   - Frontend Application: `http://localhost:80`

4. **Shutdown Containers**:
   ```bash
   docker compose down
   ```

---

## 3. Production Cloud Hosting Strategy

### Tier A: Frontend Deployment (Vercel / Netlify)

1. Connect your GitHub repository to Vercel/Netlify.
2. Configure build settings:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
3. Set Environment Variable:
   - `VITE_API_URL`: `https://your-backend-api.onrender.com/api/v1`

---

### Tier B: Backend Deployment (Render / Railway / AWS / DigitalOcean)

1. **Docker Deployment**: Deploy directly using `backend/Dockerfile` or native Python runtime (Python 3.12).
2. **Environment Variables**:
   - `DATABASE_URL`: `postgresql+asyncpg://<user>:<pwd>@<host>.neon.tech/<db>?sslmode=require`
   - `DATABASE_SYNC_URL`: `postgresql://<user>:<pwd>@<host>.neon.tech/<db>?sslmode=require`
   - `JWT_SECRET_KEY`: `<min-32-chars-random-cryptographic-key>`
   - `ALLOWED_ORIGINS`: `https://your-frontend.vercel.app`
   - `ALLOWED_HOSTS`: `your-backend.onrender.com`
   - `ENVIRONMENT`: `production`
   - `DEBUG`: `false`
   - `EMAIL_PROVIDER`: `smtp`
   - `EMAIL_ENABLED`: `true`
   - `SMTP_ENABLED`: `true`
   - `SMTP_HOST`: `smtp.gmail.com`
   - `SMTP_PORT`: `587`
   - `SMTP_USERNAME`: `<your-smtp-username>`
   - `SMTP_PASSWORD`: `<your-smtp-app-password>`
   - `SMTP_USE_TLS`: `true`
   - `SMTP_FROM_EMAIL`: `noreply@yourdomain.com`
   - `SMTP_FROM_NAME`: `STARTWISE AI`
   - `RESEND_API_KEY`: `re_your_api_key` (Optional fallback)
3. **Start Command**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

---

### Tier C: Database Management (Neon PostgreSQL)

1. Provision a serverless PostgreSQL database on [Neon.tech](https://neon.tech).
2. Copy the Connection String and enable pooled connection pooling (`sslmode=require`).
3. Run Alembic migrations:
   ```bash
   alembic upgrade head
   ```

---

## 4. Production Health Checks & Monitoring

- **Liveness Probe**: `GET /health` (Returns HTTP 200 `{"status": "healthy"}`)
- **Readiness Probe**: `GET /api/health` (Validates Database connection, Scikit-Learn Model loading, SHAP engine availability, and email service configuration)
- **Monitoring Metrics**: Prometheus/Grafana or Render metrics dashboard for response times, RAM utilization, and error rates.
