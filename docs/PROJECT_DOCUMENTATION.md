# SkillSync — Project Documentation

**Version:** 1.0.0  
**Project Round:** JTP 2026  
**Last Updated:** July 2026

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Technology Stack](#3-technology-stack)
4. [Database Design](#4-database-design)
5. [Backend — API Design](#5-backend--api-design)
6. [Matching Algorithm](#6-matching-algorithm)
7. [Frontend Architecture](#7-frontend-architecture)
8. [Deployment Architecture](#8-deployment-architecture)
9. [Security Considerations](#9-security-considerations)
10. [Performance Notes](#10-performance-notes)
11. [Testing Strategy](#11-testing-strategy)
12. [Known Limitations](#12-known-limitations)

---

## 1. Project Overview

### Purpose

SkillSync is a collaborator-matching platform for technical professionals. It solves the problem of finding a compatible project partner when "looking for a developer" is far too vague to be useful. The platform asks structured questions about skills, working style, and preferences, then runs a transparent, explainable scoring algorithm to surface the most compatible profiles from a pool of 40 synthetic collaborators.

### Goals

- **Explainability first** — every match shows _why_ it ranked where it did, not just a score.
- **Multi-dimensional compatibility** — skills alone are insufficient; availability, timezone, and working style matter equally in practice.
- **Deterministic results** — the same preferences always produce the same ranking. No randomness, no black-box ML.
- **Honest trade-offs** — the UI surfaces incompatibilities alongside strengths so users can make informed decisions.

### Scope

| In Scope | Out of Scope |
|---|---|
| Preference capture via 5-step wizard | User accounts / authentication |
| 8-dimension weighted scoring | Real-time chat or messaging |
| Top-10 ranked results with explanations | Profile editing by collaborators |
| Sort, filter, radar chart on results | Email notifications |
| Docker-based local deployment | Payments or subscriptions |
| Single-service Render cloud deployment | |

---

## 2. System Architecture

### High-Level Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Browser (Client)                     │
│              React 18 SPA — TypeScript + Vite               │
└───────────────────────────┬─────────────────────────────────┘
                            │  HTTP/HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    nginx Reverse Proxy                      │
│  /* → static React files  │  /api/* → uvicorn :8000        │
└───────────────────────────┬─────────────────────────────────┘
                            │  HTTP (internal)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│               FastAPI Backend  (uvicorn)                    │
│  endpoints.py → matching_engine.py → SQLAlchemy ORM        │
└───────────────────────────┬─────────────────────────────────┘
                            │  TCP :5432
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   PostgreSQL 15 Database                    │
│  collaborator_profiles · skills · project_interests        │
│  profile_skills (with proficiency) · profile_interests     │
└─────────────────────────────────────────────────────────────┘
```

### Local Docker Architecture

Three containers communicate on a private `skillsync-network` bridge network:

| Container | Image | Internal host | External port |
|---|---|---|---|
| `skillsync-database` | `postgres:15-alpine` | `database:5432` | — |
| `skillsync-backend` | `python:3.11-slim` | `backend:8000` | `8000` |
| `skillsync-frontend` | `node:18-alpine` → `nginx:alpine` | `frontend:80` | `5173` |

The browser only communicates with nginx (frontend container). The backend and database are not exposed to the host by default (the backend port `8000` is exposed for direct API inspection only).

### Request Flow: Match Request

```
User clicks "Find My Matches"
   │
   ▼
React: POST /api/matches (JSON body)
   │
   ▼
nginx: proxies /api/* → backend:8000
   │
   ▼
FastAPI: validates request body with Pydantic
   │
   ▼
matching_engine.find_matches()
   ├── Query: all 40 CollaboratorProfile rows
   ├── Query: skill rarity counts (1 aggregate query)
   ├── Query: all profile_skills proficiency rows (1 bulk query)
   └── For each profile:
       ├── calculate_skill_score()
       ├── calculate_interest_score()
       ├── calculate_availability_score()
       ├── calculate_timezone_score()
       ├── calculate_experience_score()
       ├── calculate_collaboration_score()
       ├── calculate_communication_score()
       ├── calculate_team_size_score()
       ├── weighted sum + consistency bonus
       ├── generate_match_reasons()
       └── generate_trade_offs()
   │
   ▼
Sort by: overall_score DESC → skill_score DESC → profile_id ASC
   │
   ▼
Return top 10 as MatchResponse JSON
   │
   ▼
React: renders ranked MatchCard components
```

---

## 3. Technology Stack

### Backend Dependencies (`requirements.txt`)

| Package | Version | Role |
|---|---|---|
| `fastapi` | 0.109.0 | REST API framework |
| `uvicorn[standard]` | 0.27.0 | ASGI server |
| `sqlalchemy` | 2.0.25 | ORM and query builder |
| `psycopg2-binary` | 2.9.9 | PostgreSQL driver |
| `pydantic` | 2.5.3 | Data validation |
| `pydantic-settings` | 2.1.0 | Environment-based configuration |
| `pytest` | 7.4.4 | Test runner |
| `httpx` | 0.26.0 | Async HTTP client (test helper) |
| `requests` | 2.31.0 | Sync HTTP client (health check) |

### Frontend Dependencies (`package.json`)

| Package | Version | Role |
|---|---|---|
| `react` | ^18.2.0 | UI framework |
| `react-dom` | ^18.2.0 | DOM renderer |
| `typescript` | ^5.2.2 | Type system |
| `vite` | ^5.0.8 | Build tool and dev server |
| `@vitejs/plugin-react` | ^4.2.1 | Vite React plugin |

No third-party UI component library is used. All components and styles are custom.

---

## 4. Database Design

### Entity Relationship Diagram

```
collaborator_profiles        profile_skills (association)        skills
─────────────────────        ─────────────────────────────       ──────────────
id (PK)                 ←──  profile_id (FK)                     id (PK)
name                         skill_id (FK)              ──────►  name (unique)
professional_title           proficiency_level                    category
bio                          (beginner/intermediate/
experience_level              advanced/expert)
years_of_experience
weekly_availability_hours    profile_interests (association)      project_interests
timezone                     ─────────────────────────────        ─────────────────
collaboration_style     ←──  profile_id (FK)                      id (PK)
communication_preference     interest_id (FK)           ──────►   name (unique)
preferred_team_size                                               description
created_at
```

### Table Descriptions

#### `collaborator_profiles`
The core entity. Each row represents one synthetic collaborator with 9 structured attributes plus a bio. Created at seed time; not modified at runtime.

#### `skills`
Lookup table of 55 unique skills, each tagged with a category (`frontend`, `backend`, `database`, `devops`, `data`, `design`, `mobile`, `tools`). Used to power the category filter in the wizard.

#### `project_interests`
Lookup table of 20 project domain strings (e.g., `"SaaS Products"`, `"Healthcare Tech"`). Used to populate interest pickers in the wizard.

#### `profile_skills`
Many-to-many association table that also stores a `proficiency_level` column (`beginner`, `intermediate`, `advanced`, `expert`). The extra column is why SQLAlchemy uses an explicit `Table()` object rather than a simple relationship secondary.

#### `profile_interests`
Standard many-to-many association table (no extra columns).

### Seed Data Summary

| Entity | Count |
|---|---|
| Collaborator profiles | 40 |
| Skills | 55 |
| Project interest domains | 20 |
| Skill categories | 8 |
| Profile–skill associations | ~200 (avg 5 per profile) |
| Profile–interest associations | ~120 (avg 3 per profile) |

The seed function (`init_db.py:seed_data`) is **idempotent** — it checks `Skill.count() > 0` before inserting and skips if data already exists. This makes container restarts safe.

---

## 5. Backend — API Design

### Application Startup (`main.py`)

FastAPI uses an `asynccontextmanager` lifespan hook that runs before the server accepts requests:

1. `wait_for_db()` — polls the DB with `SELECT 1` every 2 seconds (up to 30 retries) until healthy. Required because the database container may not be ready when the backend container starts.
2. `init_database()` — calls `Base.metadata.create_all()` to create tables (no-op if already exist).
3. `seed_data(db)` — inserts 40 profiles if the table is empty.

CORS middleware is added _after_ the router to allow browser requests from all expected origins (localhost variants and `*.onrender.com`).

### Endpoint Details

#### `GET /api/health`
Returns `{ "status": "healthy", "service": "SkillSync Backend", "database": "connected" }`.  
Used by Docker health checks, Render health check path, and the frontend pre-warm logic.

#### `GET /api/options`
Queries `Skill` and `ProjectInterest` tables and returns structured options for all form controls. Response is computed on each request (no caching) — acceptable at this scale. The frontend caches the result in React state for the session lifetime.

#### `POST /api/matches`
Main endpoint. Accepts `MatchPreferences`, calls `find_matches()`, serialises results into `MatchResponse` via Pydantic. All preference fields are optional — omitted fields use neutral scoring (50 pts) so partial inputs still produce useful results.

#### `GET /api/profiles` and `GET /api/profiles/{id}`
Read-only profile inspection endpoints. Not used by the primary user flow but useful for debugging and API exploration.

### Error Handling

- Pydantic validation errors → 422 Unprocessable Entity (automatic from FastAPI).
- Profile not found → 404 with `{ "detail": "Profile not found" }`.
- Matching engine exceptions → 500 with the original exception message (useful for debugging; should be sanitised in a production with real users).

---

## 6. Matching Algorithm

File: `backend/app/services/matching_engine.py`

### Overview

The algorithm is a **deterministic weighted scoring model** with eight dimensions. Every profile is scored independently — there is no relative ranking between profiles during scoring. The final rank emerges from sorting the independent scores.

### Scoring Weights

```python
SCORING_WEIGHTS = {
    "skills":              0.33,
    "interests":           0.18,
    "availability":        0.14,
    "collaboration_style": 0.09,
    "communication":       0.09,
    "team_size":           0.07,
    "timezone":            0.05,
    "experience":          0.05,
}
# Sum = 1.00
```

### Dimension Scorers

#### 1. Skills (33%)
The most heavily weighted dimension. Two sub-components:

**Needed-skill coverage (70% of skill score):**  
For each skill in `needed_skills`, the algorithm looks up whether the profile has that skill and at what proficiency. The contribution is:

```
contribution = proficiency_weight × rarity_weight
```

Where:
- `proficiency_weight` ∈ {0.40, 0.65, 0.85, 1.00} for {beginner, intermediate, advanced, expert}
- `rarity_weight` = 1.0 + (1.0 − profile_count / total_profiles) × 0.5 ∈ [1.0, 1.5]

Rarity is pre-computed with a single aggregate query before the profile loop.

**Complementary-skill bonus (up to 30% of skill score):**  
Skills the profile has that the user neither has nor explicitly requested. Each contributes `proficiency × rarity × 0.05`, capped at 0.30 total.

**Design rationale:** A profile that matches `expert Kubernetes` on a skill that only 2/40 profiles have should rank higher than one matching `beginner Python` on a skill that all profiles share. The rarity × proficiency product captures this.

#### 2. Interests (18%)
Uses an **F-beta score with β=1.5** (recall-weighted) rather than symmetric Jaccard similarity.

```
recall    = |intersection| / |user_interests|
precision = |intersection| / |profile_interests|
F₁.₅     = (1 + 1.5²) × (precision × recall) / (1.5² × precision + recall)
```

**Design rationale:** Jaccard penalises a profile that shares all of the user's interests but also has extras. The F-beta score rewards recall (covering what the user wants) more than precision (avoiding irrelevant domains).

#### 3. Availability (14%)
```
ratio = profile_hours / user_hours

score = 100         if ratio ∈ [1.0, 1.3]   (slight surplus: fine)
      = 100 − (ratio − 1.3) × 14.3          if ratio ∈ (1.3, 2.0]  (large surplus: mild penalty)
      = max(90 − (ratio − 2.0) × 20, 50)    if ratio > 2.0          (huge surplus: spreading thin)
      = ratio × 100                          if ratio < 1.0          (under-available: linear penalty)
```

**Design rationale:** A collaborator offering 21 h when you need 20 h is ideal. One offering 60 h when you need 10 h may be over-committed elsewhere — hence the graduated penalty for large surpluses.

#### 4. Timezone (5%)
Smooth exponential decay on the UTC offset difference:

```
score = 100 × exp(−0.08 × diff^1.5)

Examples:
  0 h difference  → 100
  2 h difference  → ~91
  5 h difference  → ~76
  8 h difference  → ~54
  12 h difference → ~28
```

Minimum score: 10 (no one is completely incompatible just due to timezone).

**Design rationale:** The previous step-band approach (0-3h = 100, 4-6h = 75, etc.) created arbitrary cliffs. Exponential decay is proportional — every hour of difference matters.

#### 5. Experience Level (5%)
Asymmetric ordinal distance on the scale `[junior, mid-level, senior, lead]`:

```
diff = profile_level_index - user_preference_index

score = 100  (exact match)
      = 85   (one level above requested — experienced collaborator is usually fine)
      = 70   (one level below — mild concern)
      = 65   (two above)
      = 40   (two below)
      = 35   (three above)
      = 20   (three below)
```

**Design rationale:** Over-experienced is generally less problematic than under-experienced for project collaboration, so asymmetric penalties reflect real-world dynamics.

#### 6. Collaboration Style (9%)
Compatibility matrix:

| User ↓ / Profile → | collaborative | flexible | independent |
|---|---|---|---|
| collaborative | 100 | 90 | 55 |
| flexible | 90 | 100 | 90 |
| independent | 55 | 90 | 100 |

#### 7. Communication Preference (9%)
Compatibility matrix:

| User ↓ / Profile → | async | hybrid | sync |
|---|---|---|---|
| async | 100 | 85 | 45 |
| hybrid | 85 | 100 | 85 |
| sync | 45 | 85 | 100 |

#### 8. Team Size (7%)
Step-distance scoring:

| Distance | Score |
|---|---|
| Exact match (e.g., both prefer `small`) | 100 |
| One step (small↔medium or medium↔large) | 65 |
| Two steps (small↔large) | 30 |

### Consistency Bonus

After computing the eight dimension scores, a ±3 point adjustment is applied based on score variance:

```
adjustment = 3.0 − (variance / 250.0)
clamped to [−3, +3]
```

A profile scoring ~80 on all dimensions (low variance) receives up to +3. A profile scoring 100 on skills and 10 on everything else (high variance) receives up to −3. This reflects the practical reality that a balanced collaborator is more dependable than a single-dimension specialist.

### Deterministic Sort

After scoring all profiles, results are sorted with a three-key tuple to guarantee a stable total order:

```python
key = (−overall_score, −skill_score, profile_id)
```

Ties on overall score are broken by skill score (descending), then by profile ID (ascending, arbitrary but stable).

---

## 7. Frontend Architecture

### Component Tree

```
App.tsx  (view router, options pre-fetch)
├── Landing.tsx           (view: 'landing')
├── MatchingWizard.tsx    (view: 'wizard')
│   └── MultiSelect.tsx   (reused on steps 1, 2, 3)
└── Results.tsx           (view: 'results')
    ├── RadarChart        (inline SVG component)
    ├── ScoreBar          (inline component)
    └── MatchCard         (inline component)
```

### State Management

No state management library is used. All state is managed with `useState` hooks:

- `App.tsx` holds: current view, match results, pre-fetched options, options error.
- `MatchingWizard.tsx` holds: current step, loading flag, form error, preferences object, skill category filter, cold-start wait timer.
- `Results.tsx` holds: expanded card IDs (Set), active sort key, minimum score filter.

### Options Pre-fetch Strategy

`App.tsx` calls `api.getOptions()` immediately on mount and stores the result in state. The options are passed as a prop to `MatchingWizard`. This means the backend `/api/options` request fires while the user reads the landing page, eliminating the cold-start wait that would otherwise appear on the wizard screen.

If the options haven't resolved by the time the user navigates to the wizard (e.g., on a genuinely cold Render free-tier backend), the wizard shows a loading screen with a timer-triggered message:
- After 4 seconds: "The service is waking up — first load can take 20–40 s on the free tier."
- After 20 seconds: "Still warming up, almost there…"

### API Client (`services/api.ts`)

Thin typed wrapper around `fetch`. The base URL is empty by default, so all requests go to the same origin (nginx handles routing). For local development, Vite's dev server proxy forwards `/api/*` to `localhost:8000`.

### nginx Reverse Proxy (`frontend/nginx.conf`)

```nginx
location /api/ {
    proxy_pass http://backend:8000;
}
location / {
    try_files $uri $uri/ /index.html;
}
```

The `try_files` directive with `/index.html` fallback enables React Router (client-side routing) — direct URL access to any route works correctly.

---

## 8. Deployment Architecture

### Local (Docker Compose)

```
Host machine
├── :5173 → skillsync-frontend (nginx:alpine) → React SPA + /api proxy
│                                             → skillsync-backend:8000
└── :8000 → skillsync-backend  (python:3.11-slim) → uvicorn → FastAPI
                                               → skillsync-database:5432
```

### Production (Render + Supabase)

```
Internet
└── Render Web Service (port 10000, Dockerfile.render)
    ├── nginx (port 10000)
    │   ├── /* → /app/frontend-dist (pre-built React SPA)
    │   └── /api/* → 127.0.0.1:8000
    └── uvicorn (port 8000, internal only)
        └── FastAPI → Supabase PostgreSQL (TCP, external)
```

The `render-start.sh` startup script starts nginx in the background and then starts uvicorn in the foreground (so the container stays alive as long as uvicorn runs).

**Why single-service for Render?** Render's free tier allows one free web service. A single Docker image that bundles both the static frontend and the Python backend avoids the need for a second paid service.

### Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | Yes (production) | `postgresql://skillsync_user:...@database:5432/skillsync_db` | Full PostgreSQL connection string |
| `PORT` | Render only | `10000` | Port Render assigns; used by nginx |
| `PYTHONUNBUFFERED` | Recommended | `1` | Enables real-time log streaming |

---

## 9. Security Considerations

### What is in place

- **Pydantic validation** — all API inputs are schema-validated; invalid types and out-of-range values are rejected with 422 before reaching business logic.
- **Field validators** — `preferred_experience`, `collaboration_style`, and `communication_preference` are validated against an allowlist of exact strings.
- **CORS allowlist** — origins are explicitly listed; wildcard `*` is not used.
- **SQLAlchemy ORM** — all database access uses parameterised queries via SQLAlchemy; raw string interpolation into SQL is not used.
- **Read-only data access** — no user can modify the collaborator profiles. The only write path is the internal seed function on startup.

### What is not in place (acceptable for this scope)

- No authentication or authorisation — the app has no user accounts.
- No rate limiting — acceptable for a demo/project round submission.
- No HTTPS enforcement at the application level — handled by Render's load balancer in production.
- Exception messages are returned in 500 responses — acceptable for a project submission; should be sanitised if deployed with real users.

---

## 10. Performance Notes

### Database Query Count per Match Request

| Query | Count |
|---|---|
| Load all 40 profiles (with skills/interests via lazy load) | 1 + up to 80 (lazy) |
| Skill rarity aggregate | 1 |
| All profile_skills proficiency (bulk pre-fetch) | 1 |
| **Total** | **~83 queries** |

The proficiency bulk pre-fetch was introduced to eliminate an N+1 pattern (previously 40 individual queries per match request, one per profile). This reduced match-request DB round-trips by ~40×.

Further optimisation (loading skills/interests eagerly with `joinedload`) would reduce queries to 3, but is not needed at this dataset size.

### Response Times (approximate)

| Operation | Warm backend | Cold start (Render free) |
|---|---|---|
| `GET /api/options` | 50–150 ms | 20–40 s |
| `POST /api/matches` | 100–300 ms | n/a (backend already warm) |
| Static asset (React SPA) | <10 ms | <10 ms (nginx, always warm) |

---

## 11. Testing Strategy

### Unit Tests (`backend/tests/test_matching_engine.py`)

Tests cover:

| Area | What is tested |
|---|---|
| `calculate_skill_score` | Exact match, partial match, no match, complementary bonus, proficiency weighting, rarity weighting |
| `calculate_interest_score` | Full overlap, partial, no overlap, empty input neutrality |
| `calculate_availability_score` | Under/over/exact, large surplus, edge cases |
| `calculate_timezone_score` | Same timezone, 2h/5h/8h/12h differences, parse edge cases |
| `calculate_experience_score` | Exact, one above/below, two above/below, empty preference |
| `calculate_collaboration_score` | All matrix combinations |
| `calculate_communication_score` | All matrix combinations |
| `calculate_team_size_score` | Exact, adjacent, opposite |
| `calculate_consistency_bonus` | Low variance (bonus), high variance (penalty) |
| `generate_match_reasons` | Reasons generated for high-scoring dimensions |
| `generate_trade_offs` | Trade-offs generated for low-scoring dimensions |

Run with:
```bash
cd backend && pytest tests/ -v
```

### Manual Testing Checklist

- [ ] 5-step wizard completes without error
- [ ] Each step validates and passes data correctly to review screen
- [ ] Match results display with correct scores and colours
- [ ] Radar chart renders for all expanded cards
- [ ] Sort pills reorder results correctly
- [ ] Minimum score slider filters results correctly
- [ ] "No matches above X%" empty state appears when filter is too strict
- [ ] "Adjust Preferences" returns to wizard with same results preserved
- [ ] SkillSync logo click returns to Landing
- [ ] API docs at `/docs` show all endpoints

---

## 12. Known Limitations

| Limitation | Impact | Notes |
|---|---|---|
| Render free tier cold starts | 20–40 s first-load delay | Mitigated by pre-fetch on landing page and UX warm-up message |
| 40 synthetic profiles | Small result pool | Sufficient for demonstration; real system would need profile submission flow |
| No user persistence | Preferences lost on refresh | Acceptable for project scope; could use localStorage |
| Lazy-loaded ORM relationships | ~80 DB queries per match | Acceptable at 40 profiles; use `joinedload` for larger datasets |
| Single scoring model | No personalisation over time | Appropriate for deterministic, explainable demo |
| No input sanitisation on error messages | 500 responses leak exception details | Acceptable for demo; sanitise for real-user deployment |
