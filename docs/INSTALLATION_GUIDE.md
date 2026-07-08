# SkillSync — Installation Guide

**Version:** 1.0.0  
**Last Updated:** July 2026

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Installation Method Overview](#2-installation-method-overview)
3. [Option A: Docker Compose (Recommended)](#3-option-a-docker-compose-recommended)
4. [Option B: Native (No Docker)](#4-option-b-native-no-docker)
5. [Production Deployment on Render](#5-production-deployment-on-render)
6. [Environment Variables Reference](#6-environment-variables-reference)
7. [Verifying the Installation](#7-verifying-the-installation)
8. [Running the Test Suite](#8-running-the-test-suite)
9. [Common Issues and Fixes](#9-common-issues-and-fixes)

---

## 1. Prerequisites

### For Docker Compose (Option A)

| Requirement | Version | Check |
|---|---|---|
| Docker Desktop (or Docker Engine + Compose plugin) | 24+ / Compose v2+ | `docker --version` |
| 2 GB free RAM | — | System monitor |
| Ports 5173 and 8000 free on your machine | — | See §9 |

Docker Desktop includes Docker Compose. No other tools are required.

### For Native Setup (Option B)

| Requirement | Version | Check |
|---|---|---|
| Python | 3.11+ | `python --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |
| PostgreSQL | 14+ | `psql --version` |

### For All Options

| Tool | Purpose |
|---|---|
| Git | Cloning the repository |
| A terminal / command prompt | Running commands |

---

## 2. Installation Method Overview

| Method | Best for | Effort |
|---|---|---|
| Docker Compose | Any developer; zero config; exactly reproduces production environment | Low |
| Native | Faster iteration when modifying backend or frontend code; no Docker overhead | Medium |
| Render (production) | Deploying a publicly accessible live instance | Low (after initial setup) |

---

## 3. Option A: Docker Compose (Recommended)

This method starts three containers (PostgreSQL, FastAPI backend, React frontend served by nginx) with a single command. No other software needs to be installed or configured.

### Step 1: Clone the Repository

```bash
git clone https://github.com/Sumant3086/SkillSync-JTP.git
cd SkillSync-JTP
```

### Step 2: Start All Services

```bash
docker compose up --build
```

What this does:
1. Builds the backend Docker image (`python:3.11-slim` with all Python dependencies).
2. Builds the frontend Docker image (compiles the React app with Vite, then serves it with nginx).
3. Pulls `postgres:15-alpine` from Docker Hub.
4. Creates the `skillsync-network` bridge network.
5. Creates the `skillsync-postgres-data` persistent volume.
6. Starts all three containers.
7. The backend waits for the database to pass its health check before starting.
8. On first run, the database is seeded with 40 synthetic collaborator profiles automatically.

### Step 3: Open the Application

| Service | URL |
|---|---|
| Frontend (React app) | http://localhost:5173 |
| Backend REST API | http://localhost:8000/api |
| Interactive API docs | http://localhost:8000/docs |

### Step 4: Stop the Services

```bash
# Stop containers (data is preserved)
docker compose down

# Stop containers AND delete all data (full reset)
docker compose down -v
```

### Running in the Background (Detached Mode)

```bash
docker compose up --build -d
```

View logs:
```bash
docker compose logs -f            # all containers
docker compose logs -f backend    # backend only
docker compose logs -f frontend   # frontend only
```

### Rebuilding After Code Changes

```bash
docker compose up --build
```

The `--build` flag always rebuilds images from source. Omit it for faster startup when only data has changed.

---

## 4. Option B: Native (No Docker)

Use this method if you want to run the backend and frontend directly on your machine without Docker. You need PostgreSQL installed separately.

### Step 1: Clone the Repository

```bash
git clone https://github.com/Sumant3086/SkillSync-JTP.git
cd SkillSync-JTP
```

### Step 2: Set Up PostgreSQL

Create a local database and user:

```sql
-- Connect to PostgreSQL as superuser (e.g., psql -U postgres)
CREATE USER skillsync_user WITH PASSWORD 'skillsync_password';
CREATE DATABASE skillsync_db OWNER skillsync_user;
GRANT ALL PRIVILEGES ON DATABASE skillsync_db TO skillsync_user;
```

Note your connection string: `postgresql://skillsync_user:skillsync_password@localhost:5432/skillsync_db`

### Step 3: Set Up the Backend

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set the database connection string
# Windows
set DATABASE_URL=postgresql://skillsync_user:skillsync_password@localhost:5432/skillsync_db

# macOS / Linux
export DATABASE_URL=postgresql://skillsync_user:skillsync_password@localhost:5432/skillsync_db

# Start the backend server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The `--reload` flag enables hot-reload on file changes. On first start, the backend creates the database tables and seeds 40 profiles automatically.

Expected output:
```
Starting SkillSync backend...
✓ Database connection established successfully
Creating database tables...
✓ Database tables created successfully
Seeding database with synthetic collaborator profiles...
✓ Seeded database with 40 collaborator profiles
SkillSync backend ready!
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 4: Set Up the Frontend

Open a **second terminal**:

```bash
cd SkillSync-JTP/frontend

# Install dependencies
npm install

# Start the Vite dev server
npm run dev
```

Expected output:
```
  VITE v5.x.x  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

Vite's dev server automatically proxies `/api/*` requests to `localhost:8000`, so no CORS configuration is needed.

### Step 5: Open the Application

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api
- Interactive docs: http://localhost:8000/docs

### Building the Frontend for Production (Native)

```bash
cd frontend
npm run build
# Output is in frontend/dist/
```

To preview the production build locally:
```bash
npm run preview
```

---

## 5. Production Deployment on Render

SkillSync is configured for single-click deployment to [Render](https://render.com) using a combined Docker image (`Dockerfile.render`) that bundles nginx, the React SPA, and the FastAPI backend into one container.

### Prerequisites

- A GitHub account with this repository pushed (either forked or your own copy).
- A [Render account](https://dashboard.render.com) (free tier is sufficient).
- A [Supabase account](https://supabase.com) (free tier) for the PostgreSQL database.

### Step 1: Set Up Supabase Database

1. Log in to [supabase.com](https://supabase.com) and create a new project.
2. After the project initialises (~2 minutes), go to **Settings → Database**.
3. Under **Connection string**, select the **URI** tab and copy the connection string. It looks like:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxxxxxxx.supabase.co:5432/postgres
   ```
4. Keep this connection string — you will need it in Step 3.

### Step 2: Push the Repository to GitHub

If you have not already:

```bash
# From the SkillSync-JTP directory
git remote add origin https://github.com/YOUR_USERNAME/SkillSync-JTP.git
git push -u origin main
```

### Step 3: Create the Render Web Service

**Option A — Using the Deploy Button**

Click the deploy button in the README and follow the prompts. Skip to Step 4.

**Option B — Manual Setup**

1. Go to the [Render Dashboard](https://dashboard.render.com) and click **New +** → **Web Service**.
2. Select **Connect a repository** and authorise Render to access your GitHub account.
3. Select your SkillSync-JTP repository.
4. Configure the service:

| Setting | Value |
|---|---|
| Name | `skillsync` (or any name you prefer) |
| Region | Frankfurt EU (Central) — or closest to your users |
| Branch | `main` |
| Runtime | **Docker** |
| Dockerfile Path | `./Dockerfile.render` |
| Health Check Path | `/api/health` |

5. Under **Environment Variables**, click **Add Environment Variable**:

| Key | Value |
|---|---|
| `DATABASE_URL` | Your Supabase connection string from Step 1 |
| `PYTHONUNBUFFERED` | `1` |
| `PORT` | `10000` |

6. Click **Create Web Service**.

### Step 4: Wait for the Build

Render will:
1. Pull your repository.
2. Build `Dockerfile.render` (this takes 3–8 minutes on first build).
3. Start the container.
4. Run the FastAPI lifespan hook, which connects to Supabase and seeds the database.
5. Mark the service healthy once `/api/health` returns 200.

You can watch the build progress in the Render Dashboard under **Logs**.

### Step 5: Access Your Deployment

Once the service is marked **Live**, your app is accessible at:
```
https://<your-service-name>.onrender.com
```

The URL is shown in the Render Dashboard under your service name.

### Subsequent Deployments

Every push to your `main` branch triggers an automatic redeploy on Render. No manual action is required.

### Important: Render Free Tier Limitations

| Limitation | Detail |
|---|---|
| Sleep after inactivity | Service spins down after 15 min of no traffic |
| Cold start time | 20–40 seconds for the first request after sleep |
| Monthly hours | 750 free hours (sufficient for one always-on service) |
| Build minutes | 500 per month |

The frontend (nginx) wakes instantly because it is served from within the same container. Only the Python backend (uvicorn) and database connection have a warm-up delay, which the app handles gracefully by prefetching data from the landing page.

---

## 6. Environment Variables Reference

| Variable | Required | Where used | Default | Description |
|---|---|---|---|---|
| `DATABASE_URL` | Yes (production) | Backend | `postgresql://skillsync_user:skillsync_password@database:5432/skillsync_db` | Full PostgreSQL connection URI. In Docker Compose, the default points to the database container. In production, set to your Supabase URI. |
| `PORT` | Render only | `render-nginx.conf`, `render-start.sh` | `10000` | The port Render assigns to your container. Render sets this automatically; only override if instructed. |
| `PYTHONUNBUFFERED` | Recommended | Backend | `1` | Disables Python output buffering so logs appear in real time. |

### Setting Variables in Docker Compose

The `docker-compose.yml` file hard-codes the local database URL in the `backend` service environment. You can override any variable by creating a `.env` file in the project root:

```env
# .env (not committed to git)
DATABASE_URL=postgresql://skillsync_user:skillsync_password@database:5432/skillsync_db
```

Docker Compose automatically reads `.env` from the project root.

### Setting Variables in Render

1. Open your service in the Render Dashboard.
2. Go to **Environment** → **Environment Variables**.
3. Add or edit key-value pairs.
4. Click **Save Changes** — the service will automatically redeploy.

---

## 7. Verifying the Installation

After starting the application, run these checks to confirm everything is working correctly.

### Health Check

```bash
curl http://localhost:8000/api/health
# Expected: {"status":"healthy","service":"SkillSync Backend","database":"connected"}
```

### Options Endpoint

```bash
curl http://localhost:8000/api/options
# Expected: JSON with "skills", "project_interests", "timezones", etc.
```

### Profile Count

```bash
curl http://localhost:8000/api/profiles | python -m json.tool | grep -c '"id"'
# Expected: 40
```

### Match Request

```bash
curl -X POST http://localhost:8000/api/matches \
  -H "Content-Type: application/json" \
  -d '{"needed_skills": ["Python", "FastAPI"], "timezone": "UTC+1", "weekly_availability": 20}'
```

Expected: JSON with `"total_profiles_evaluated": 40` and `"matches"` array containing 10 results.

### Frontend

Open http://localhost:5173 in a browser. You should see the SkillSync landing page. Click **Start Matching →** and confirm the wizard loads without error.

---

## 8. Running the Test Suite

```bash
# Activate your virtual environment first (native setup)
cd backend

# Run all tests with verbose output
pytest tests/ -v

# Run a specific test file
pytest tests/test_matching_engine.py -v

# Run with coverage (requires pytest-cov)
pip install pytest-cov
pytest tests/ -v --cov=app --cov-report=term-missing
```

Expected output summary:
```
tests/test_matching_engine.py::test_skill_score_exact_match PASSED
tests/test_matching_engine.py::test_skill_score_partial_match PASSED
...
========================== XX passed in X.XXs ==========================
```

---

## 9. Common Issues and Fixes

### Port Already in Use

**Symptom:** `Error: bind: address already in use` when starting Docker Compose.

**Fix:** Find and stop the process using the port.

```bash
# Windows
netstat -ano | findstr :5173
# Then: taskkill /PID <PID> /F

# macOS / Linux
lsof -ti:5173 | xargs kill
lsof -ti:8000 | xargs kill
```

Alternatively, change the host ports in `docker-compose.yml`:
```yaml
ports:
  - "3000:80"   # change 5173 to any free port
```

---

### Docker Build Fails with Pip Install Error

**Symptom:** `ERROR: Could not find a version that satisfies the requirement ...`

**Fix:** Your Docker cache may have an old layer. Force a clean build:
```bash
docker compose build --no-cache
docker compose up
```

---

### Backend Fails to Connect to Database (Native Setup)

**Symptom:** `sqlalchemy.exc.OperationalError: could not connect to server`

**Fixes:**
1. Confirm PostgreSQL is running: `pg_ctl status` or check your system services.
2. Verify the `DATABASE_URL` is correct and exported in your terminal.
3. Confirm the database and user exist (see Option B, Step 2).
4. Check that PostgreSQL is listening on port 5432: `psql -h localhost -U skillsync_user -d skillsync_db`.

---

### Database Not Seeded (0 Profiles)

**Symptom:** `GET /api/profiles` returns an empty array.

**Fix:** The seed function ran but found 0 rows, or it was never called.

Check backend logs for:
```
Seeding database with synthetic collaborator profiles...
✓ Seeded database with 40 collaborator profiles
```

If the seed ran but returned 0, the database tables may have been created but the transaction was rolled back. Restart the backend — the seed function is idempotent and safe to run again.

For Docker: `docker compose restart backend`
For native: Stop uvicorn and restart it.

---

### Render Deployment: Health Check Fails

**Symptom:** Render marks the service as failed and shows health check errors in logs.

**Common causes and fixes:**

| Cause | Fix |
|---|---|
| `DATABASE_URL` not set | Add it to Render Environment Variables and redeploy |
| Supabase connection string has wrong password | Reset the Supabase DB password and update the env var |
| Build took too long and the health check timed out | Usually resolves on the next deploy; if persistent, check build logs for Python install errors |
| Port mismatch | Confirm `PORT=10000` is set and `render-nginx.conf` listens on `$PORT` |

---

### "CORS Error" in Browser Console (Native Dev)

**Symptom:** Browser console shows `Access to fetch at 'http://localhost:8000/api/...' has been blocked by CORS policy`.

**Fix:** You are making requests directly to `localhost:8000` instead of through the Vite proxy. Make sure:
1. You are using `http://localhost:5173` (the Vite dev server), not `http://localhost:8000`.
2. The `VITE_API_BASE_URL` environment variable is not set, or is set to an empty string.

Vite's dev proxy (configured in `vite.config.ts`) forwards all `/api/*` requests to the backend. Do not override the base URL unless you have a specific reason.

---

### Frontend Build Fails (`npm run build`)

**Symptom:** TypeScript errors during `tsc && vite build`.

**Fix:**
```bash
# Ensure you are using the correct Node.js version
node --version   # should be 18+

# Clear the npm cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Run the build again
npm run build
```
