# SkillSync — Explainable Collaborator Matching Platform

> **JTP 2026 Project Round** · Deterministic weighted-scoring algorithm · 40 synthetic profiles

SkillSync is a full-stack web application that matches developers and technical professionals with compatible collaborators. Unlike platforms that filter by job title or a handful of skills, SkillSync evaluates **eight compatibility dimensions** — skills, interests, availability, collaboration style, communication preference, timezone, experience level, and team-size preference — and returns ranked results with per-dimension score breakdowns and plain-language explanations for every match.

---

## Table of Contents

- [Live Demo](#live-demo)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start (Docker)](#quick-start-docker)
- [Project Structure](#project-structure)
- [API Reference](#api-reference)
- [Matching Algorithm](#matching-algorithm)
- [Running Tests](#running-tests)
- [Documentation](#documentation)
- [Deployment](#deployment)
- [AI Tools Disclosure](#ai-tools-disclosure)
- [License](#license)

---

## Live Demo

**Deployed URL:** https://skillsync-jtp.onrender.com

> **Note:** The service runs on Render's free tier, which spins down after 15 minutes of inactivity. The first request after a cold start may take 20–40 seconds. The app shows a warm-up message automatically.

---

## Features

| Feature | Detail |
|---|---|
| **8-dimension matching** | Skills, interests, availability, collab style, communication, timezone, experience, team size |
| **Explainable results** | Per-match positive reasons and honest trade-off callouts |
| **Skill proficiency weighting** | beginner → intermediate → advanced → expert scoring |
| **Skill rarity bonus** | Rare skills score proportionally higher when matched |
| **Radar chart** | Visual per-dimension compatibility chart for each match |
| **Sort & filter** | Sort by any scoring dimension; filter by minimum score threshold |
| **Zero-config startup** | Full 3-container stack (DB + API + frontend) in one command |
| **Auto-seed** | 40 diverse synthetic profiles loaded automatically on first boot |
| **Render deployment** | Single-image `Dockerfile.render` for cloud deploy with no infra config |

---

## Tech Stack

### Frontend
| | |
|---|---|
| **React 18** + TypeScript | Component-based UI with strict typing |
| **Vite 5** | Build tooling and hot-reload dev server |
| **Custom CSS** | No UI framework — full design control |
| **nginx** | Static file serving + `/api` reverse proxy in production |

### Backend
| | |
|---|---|
| **FastAPI** | Async Python REST API with auto-generated OpenAPI docs |
| **SQLAlchemy 2** | ORM with connection pooling and health-check retry logic |
| **PostgreSQL 15** | Relational store with many-to-many skill/interest associations |
| **Pydantic v2** | Request/response validation with custom field validators |
| **Uvicorn** | ASGI server with standard extras |

### Infrastructure
| | |
|---|---|
| **Docker + Compose** | Local 3-service orchestration over a private bridge network |
| **Render** | Cloud hosting (single Docker Web Service) |
| **Supabase** | Managed PostgreSQL for production (always-on free tier) |

---

## Quick Start (Docker)

**Prerequisite:** [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

```bash
# 1. Clone
git clone https://github.com/Sumant3086/SkillSync-JTP.git
cd SkillSync-JTP

# 2. Build and start all services
docker compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000/api |
| Interactive API docs | http://localhost:8000/docs |

The database is seeded with 40 collaborator profiles on first run — no manual setup required.

```bash
# Stop services
docker compose down

# Stop and delete all data (full reset)
docker compose down -v
```

For native (non-Docker) setup and production deployment, see the [Installation Guide](docs/INSTALLATION_GUIDE.md).

---

## Project Structure

```
SkillSync-JTP/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── endpoints.py          # REST API routes (/health, /options, /matches, /profiles)
│   │   ├── core/
│   │   │   └── config.py             # Env-based settings (DATABASE_URL, CORS, version)
│   │   ├── database/
│   │   │   ├── init_db.py            # Table creation + 40-profile seed data
│   │   │   └── session.py            # Engine, session factory, DB readiness wait
│   │   ├── models/
│   │   │   └── collaborator.py       # ORM models + profile_skills association table
│   │   ├── schemas/
│   │   │   └── matching.py           # Pydantic v2 request/response schemas
│   │   ├── services/
│   │   │   └── matching_engine.py    # Core 8-dimension weighted scoring engine
│   │   └── main.py                   # FastAPI app, lifespan hook, CORS middleware
│   ├── tests/
│   │   └── test_matching_engine.py   # Unit tests for all scoring functions
│   ├── Dockerfile                    # python:3.11-slim image for local compose
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── MultiSelect.tsx       # Reusable multi-select tag picker
│   │   ├── pages/
│   │   │   ├── Landing.tsx           # Hero section, features, algorithm explainer
│   │   │   ├── MatchingWizard.tsx    # 5-step preference form
│   │   │   └── Results.tsx           # Ranked cards, radar chart, sort/filter
│   │   ├── services/
│   │   │   └── api.ts                # Typed fetch client (same-origin proxy)
│   │   ├── styles/
│   │   │   └── App.css               # Full custom stylesheet
│   │   ├── types/
│   │   │   └── index.ts              # Shared TypeScript interfaces
│   │   ├── App.tsx                   # Root view router + options pre-fetch
│   │   └── main.tsx                  # React entry point
│   ├── Dockerfile                    # Multi-stage: node build → nginx serve
│   ├── nginx.conf                    # nginx config for local Docker
│   └── package.json
│
├── docker-compose.yml                # 3-service local stack
├── Dockerfile.render                 # Combined image for Render (nginx + uvicorn)
├── render-nginx.conf                 # nginx config for Render single-service
├── render-start.sh                   # Startup script: launches nginx then uvicorn
├── render.yaml                       # Render Blueprint
└── docs/
    ├── PROJECT_DOCUMENTATION.md      # Architecture, data model, algorithm design
    ├── USER_MANUAL.md                # End-user guide (wizard walkthrough, results)
    └── INSTALLATION_GUIDE.md         # Setup instructions (Docker, native, Render)
```

---

## API Reference

**Local base URL:** `http://localhost:8000/api`  
**Interactive docs:** `http://localhost:8000/docs`

### Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/health` | Returns `{ "status": "healthy" }` |
| `GET` | `/api/options` | All valid form options (skills grouped by category, timezones, experience levels, etc.) |
| `POST` | `/api/matches` | Run the matching algorithm; returns top 10 ranked results |
| `GET` | `/api/profiles` | List all 40 collaborator profiles |
| `GET` | `/api/profiles/{id}` | Single profile by integer ID |

### POST /api/matches — Request body

```json
{
  "user_skills": ["React", "TypeScript"],
  "needed_skills": ["Python", "FastAPI", "PostgreSQL"],
  "project_interests": ["SaaS Products", "API Development"],
  "preferred_experience": "mid-level",
  "weekly_availability": 20,
  "timezone": "UTC+1",
  "preferred_team_size": "small (2-3)",
  "collaboration_style": "collaborative",
  "communication_preference": "hybrid"
}
```

All fields are optional. Omitted preference fields fall back to neutral scoring (50 pts).

### POST /api/matches — Response shape

```json
{
  "total_profiles_evaluated": 40,
  "matches_returned": 10,
  "scoring_weights": { "skills": 0.33, "interests": 0.18, ... },
  "matches": [
    {
      "rank": 1,
      "name": "Marcus Johnson",
      "overall_score": 84.3,
      "score_breakdown": {
        "skills": 91.5, "interests": 83.0, "availability": 100.0,
        "collaboration_style": 55.0, "communication": 85.0,
        "timezone": 54.2, "experience": 85.0, "team_size": 65.0
      },
      "matched_skills": ["Python", "FastAPI"],
      "complementary_skills": ["Redis", "AWS"],
      "shared_interests": ["API Development", "SaaS Products"],
      "match_reasons": ["Covers 2 required skills: Python, FastAPI", "Good availability alignment"],
      "trade_offs": ["Different preferred collaboration styles"]
    }
  ]
}
```

---

## Matching Algorithm

The engine (`backend/app/services/matching_engine.py`) is **deterministic** — the same input always produces the same ranked output. Weights sum to exactly 1.0.

| Dimension | Weight | Method |
|---|---|---|
| Skills | 33% | Proficiency × rarity-weighted coverage + complementary bonus |
| Interests | 18% | F-beta (β=1.5) recall-weighted overlap |
| Availability | 14% | Ratio-based; 0–30% surplus tolerated without penalty |
| Collaboration style | 9% | Pairwise compatibility matrix |
| Communication pref. | 9% | Pairwise compatibility matrix |
| Team size | 7% | Step-distance score (exact/adjacent/opposite) |
| Timezone | 5% | Smooth exponential decay on UTC hour difference |
| Experience level | 5% | Asymmetric ordinal distance (over-experienced < under-experienced penalty) |

A **consistency bonus** (±3 pts) rewards balanced profiles over single-dimension specialists.

**Score colour bands:**

| Band | Colour | Meaning |
|---|---|---|
| 70–100% | Green | Strong overall compatibility |
| 45–69% | Amber | Moderate match — good on some dimensions, gaps on others |
| 0–44% | Red | Weak match — notable compatibility concerns |

Full algorithm design is in [Project Documentation](docs/PROJECT_DOCUMENTATION.md#matching-algorithm).

---

## Running Tests

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

The test suite covers all 8 scoring functions, boundary conditions, the consistency bonus, and determinism guarantees.

---

## Documentation

| Document | Description |
|---|---|
| [Project Documentation](docs/PROJECT_DOCUMENTATION.md) | Full architecture, database schema, API contracts, algorithm design decisions |
| [User Manual](docs/USER_MANUAL.md) | End-user step-by-step guide — wizard walkthrough, reading results, FAQ |
| [Installation Guide](docs/INSTALLATION_GUIDE.md) | Local setup (Docker & native), environment variables, Render deployment |

---

## Deployment

The production deployment uses a single Render Web Service backed by Supabase PostgreSQL:

```
Browser
  └─► Render Web Service  (Dockerfile.render, port 10000)
        ├── nginx  →  serves React SPA (static files from /app/frontend-dist)
        └── nginx proxy /api/*  →  uvicorn :8000  →  FastAPI  →  Supabase DB
```

See [Installation Guide § Production Deployment](docs/INSTALLATION_GUIDE.md#5-production-deployment-on-render) for the full step-by-step.

---

## AI Tools Disclosure

This project was developed with the assistance of Claude (Anthropic). All code was reviewed and understood by the submitter. Architecture decisions, algorithm design, and synthetic profile data are original work.

---

## Data Sources

All 40 collaborator profiles are **original synthetic data** created specifically for this project. No real user data, third-party profile databases, or scraped content was used.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

*SkillSync — JTP 2026 Project Round · Explainable Collaborator Matching Platform*
