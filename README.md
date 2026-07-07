# SkillSync — Explainable Collaborator Matching Platform

> JTP 2026 Project Round · Matching / Recommendation Service

SkillSync is a full-stack web application that matches users with compatible project collaborators using a **deterministic, multi-criteria weighted scoring algorithm**. Unlike black-box recommendation engines, every match comes with a transparent score breakdown and human-readable explanations.

---

## Why This Project?

Finding the right collaborator is hard. Most platforms filter by job title or a handful of skills. SkillSync goes deeper — evaluating **complementary** skills (what each side brings), **shared project interests**, **availability alignment**, **working style compatibility**, and **timezone fit**. The algorithm is fully explainable: you can see exactly why each person was ranked where they were.

---

## Quick Start (Plug and Play)

**Requirements:** Docker Desktop installed and running.

```bash
git clone https://github.com/Sumant3086/SkillSync-JTP.git
cd SkillSync-JTP
docker-compose up --build
```

| Service      | URL                          |
|--------------|------------------------------|
| Frontend     | http://localhost:5173         |
| Backend API  | http://localhost:8000/api    |
| API Docs     | http://localhost:8000/docs    |

That is it. All three containers (database, backend, frontend) start automatically and connect through a custom Docker network (`skillsync-network`). The database is seeded with **40 synthetic profiles** on first run — no manual setup required.

---

## Architecture

```
Browser
  │
  └──► nginx (host :5173 → container :80)
         │
         ├── /api/* ──► FastAPI backend (container :8000)
         │                    │
         │                    └── PostgreSQL (container :5432)
         │
         └── /* ──────► React SPA (static files)
```

All three services communicate over the **`skillsync-network`** bridge network. The browser only talks to nginx — the backend and database are not directly reachable from outside Docker except for the exposed backend port (useful for inspecting the API directly).

### Container Breakdown

| Container             | Base Image                      | Role                                      |
|-----------------------|---------------------------------|-------------------------------------------|
| `skillsync-database`  | `postgres:15-alpine`            | Persistent data store                     |
| `skillsync-backend`   | `python:3.11-slim`              | FastAPI REST API + matching engine        |
| `skillsync-frontend`  | `node:18-alpine` → `nginx:alpine` | React SPA build + nginx reverse proxy   |

---

## Technology Stack

### Backend (Python)
- **FastAPI** — REST API framework with automatic OpenAPI documentation
- **SQLAlchemy 2.0** — ORM with PostgreSQL
- **Pydantic v2** — Request and response validation with field validators
- **psycopg2-binary** — PostgreSQL driver
- **Uvicorn** — ASGI server

### Frontend (TypeScript)
- **React 18** with TypeScript (strict mode)
- **Vite** — Build tool with dev-server proxy
- **nginx** — Production static file server + `/api` reverse proxy

### Infrastructure
- **Docker + Docker Compose** — Container orchestration with custom network
- **PostgreSQL 15** — Relational database with persistent volume

---

## Matching Algorithm

The matching engine (`backend/app/services/matching_engine.py`) uses a **weighted multi-criteria scoring model**. It is deterministic — the same preferences always produce the same ranked output.

### Scoring Dimensions and Weights

| Dimension            | Weight | Scoring Method                                                   |
|----------------------|--------|------------------------------------------------------------------|
| Skills               | 35 %   | Needed-skills coverage (70 %) + complementary skills bonus (30 %) |
| Interests            | 20 %   | Jaccard similarity on project domain sets                        |
| Availability         | 15 %   | Linear ratio of weekly hours (penalises large excess)            |
| Collaboration Style  | 10 %   | Pairwise compatibility matrix (collaborative / independent / flexible) |
| Communication        | 10 %   | Pairwise compatibility matrix (async / sync / hybrid)            |
| Timezone             | 5 %    | UTC offset distance mapped to a step-function score              |
| Experience Level     | 5 %    | Ordinal distance on a 4-level scale (junior → lead)              |

### Score Colour Coding

| Range   | Colour | Meaning                                              |
|---------|--------|------------------------------------------------------|
| 70–100% | Green  | Strong match — high compatibility across dimensions  |
| 45–69%  | Amber  | Moderate match — good on some, gaps on others        |
| 0–44%   | Red    | Weak match — significant compatibility concerns      |

Each result includes matched skills, complementary skills, shared interests, plain-English match reasons, and honest trade-off assessments.

---

## API Reference

Base URL: `http://localhost:8000`
Interactive Swagger docs: `http://localhost:8000/docs`

| Method | Endpoint               | Description                                    |
|--------|------------------------|------------------------------------------------|
| GET    | `/api/health`          | Service health check                           |
| GET    | `/api/options`         | All valid form options (skills, interests …)   |
| GET    | `/api/profiles`        | List all 40 collaborator profiles              |
| GET    | `/api/profiles/{id}`   | Single profile by ID                           |
| POST   | `/api/matches`         | Find ranked matches for given preferences      |

### POST /api/matches — Example Request

```json
{
  "user_skills": ["React", "TypeScript"],
  "needed_skills": ["Python", "FastAPI"],
  "project_interests": ["SaaS Products", "API Development"],
  "preferred_experience": "mid-level",
  "weekly_availability": 20,
  "timezone": "UTC+1",
  "preferred_team_size": "small (2-3)",
  "collaboration_style": "collaborative",
  "communication_preference": "hybrid"
}
```

---

## Database

Seeded automatically on first startup with **40 synthetic collaborator profiles** covering:

- **55 skills** across 8 categories (frontend, backend, database, devops, data, design, mobile, tools)
- **20 project interest domains** (Web Development, AI & Machine Learning, FinTech, Healthcare Tech …)
- **4 experience levels**: junior, mid-level, senior, lead
- **Global timezone spread**: UTC-8 through UTC+9
- **3 collaboration styles**: collaborative, independent, flexible
- **3 communication preferences**: async, sync, hybrid

All profiles are original synthetic data — no real user data or third-party databases were used.

---

## Project Structure

```
SkillSync-JTP/
├── backend/
│   ├── app/
│   │   ├── api/endpoints.py         # REST API endpoints
│   │   ├── core/config.py           # App settings and CORS configuration
│   │   ├── database/
│   │   │   ├── init_db.py           # Schema creation + 40 synthetic profiles
│   │   │   └── session.py           # SQLAlchemy engine, session, retry logic
│   │   ├── models/collaborator.py   # ORM models (profiles, skills, interests)
│   │   ├── schemas/matching.py      # Pydantic v2 schemas with field validators
│   │   ├── services/
│   │   │   └── matching_engine.py   # Core weighted matching algorithm
│   │   └── main.py                  # FastAPI app with lifespan context manager
│   ├── tests/
│   │   └── test_matching_engine.py  # 24 unit tests for all scoring functions
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/MultiSelect.tsx
│   │   ├── pages/
│   │   │   ├── Landing.tsx          # Hero, features, algorithm explanation
│   │   │   ├── MatchingWizard.tsx   # 5-step preference form with category filters
│   │   │   └── Results.tsx          # Ranked results with colour-coded score bars
│   │   ├── services/api.ts          # Typed API client (uses nginx proxy)
│   │   ├── styles/App.css           # Custom stylesheet
│   │   ├── types/index.ts           # TypeScript type definitions
│   │   └── App.tsx                  # Root component with view routing
│   ├── nginx.conf                   # nginx with /api proxy to backend
│   ├── Dockerfile                   # Multi-stage build (node → nginx)
│   └── vite.config.ts               # Vite config with dev-server /api proxy
├── docker-compose.yml               # Three-container orchestration
└── README.md
```

---

## Running Tests

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

24 unit tests cover all scoring functions, boundary conditions (0–100 range), and determinism guarantees.

---

## Local Development (without Docker)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
# Provide a local PostgreSQL instance via DATABASE_URL env var
DATABASE_URL=postgresql://user:pass@localhost:5432/skillsync uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev   # Vite's proxy forwards /api requests to localhost:8000
```

---

## AI Tools Disclosure

This project was developed with the assistance of Claude (Anthropic). All code was reviewed, understood, and can be explained by the submitter. The architecture, algorithm design, and data are original work.

---

## Data Sources

All 40 collaborator profiles are **original synthetic data** created specifically for this project. No real user data, third-party profile databases, or scraped content was used. Skill and interest names are generic industry terms.

---

## License

MIT License — see `LICENSE` for details.

---

*SkillSync — JTP 2026 Project Round · Matching / Recommendation Service*
