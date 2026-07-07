# SkillSync - Review Guide

**Developed for JTP 2026 Project Round**

---

## Quick Navigation

- [30-Second Introduction](#30-second-introduction)
- [60-Second Project Pitch](#60-second-project-pitch)
- [3-Minute Technical Walkthrough](#3-minute-technical-walkthrough)
- [Complete Architecture](#complete-architecture)
- [Matching Algorithm Explained](#matching-algorithm-explained)
- [Database Design](#database-design)
- [Docker Architecture](#docker-architecture)
- [Reviewer Q&A](#reviewer-qa-30-common-questions)

---

## 30-Second Introduction

SkillSync is an explainable collaborator matching platform that helps users find ideal project partners. Unlike traditional platforms that match only on job titles or a few skills, SkillSync evaluates seven compatibility dimensions—including complementary skills, shared interests, working styles, availability, and timezone—to recommend the best collaborators with clear, transparent reasoning for every match.

---

## 60-Second Project Pitch

**The Problem:**
Finding the right project collaborator is hard. Most platforms show you profiles based on keywords or job titles, but successful collaboration depends on much more—complementary skills, compatible working styles, aligned availability, and shared project interests.

**The Solution:**
SkillSync uses a deterministic, explainable weighted scoring algorithm (no AI/ML black boxes) to evaluate potential collaborators across seven dimensions. Every match comes with:
- Overall compatibility percentage
- Detailed score breakdown
- Matched and complementary skills
- Clear reasons why the match works
- Honest trade-offs to consider

**Why It Matters:**
Users get transparency. They understand exactly why someone was recommended, what strengths the collaborator brings, and what compromises might exist. This builds trust and leads to better collaboration decisions.

---

## 3-Minute Technical Walkthrough

### Stack
- **Frontend:** React 18 + TypeScript, Vite, original custom CSS
- **Backend:** Python FastAPI, SQLAlchemy ORM, Pydantic validation
- **Database:** PostgreSQL 15 with 40 original synthetic profiles
- **Infrastructure:** Docker Compose with custom network and persistent volume

### User Flow
1. User lands on SkillSync homepage
2. Clicks "Find My Matches"
3. Completes 5-step preference form:
   - Step 1: Project interests
   - Step 2: User's existing skills
   - Step 3: Needed skills + experience preference
   - Step 4: Working preferences (availability, timezone, team size, styles)
   - Step 5: Review and submit
4. Frontend sends POST request to `/api/matches`
5. Backend matching engine evaluates all 40 profiles
6. Each profile receives scores across 7 dimensions
7. Scores are weighted and combined into overall compatibility
8. Results are ranked deterministically
9. Frontend displays top 10 matches with full explanations

### Request Lifecycle
```
User Browser
    ↓ (User fills form)
React Frontend (Port 5173)
    ↓ POST /api/matches {preferences}
FastAPI Backend (Port 8000)
    ↓ find_matches()
Matching Engine (matching_engine.py)
    ↓ SQL queries
PostgreSQL Database (Port 5432)
    ↓ Profile data
Matching Engine (calculates scores)
    ↓ Ranked JSON response
FastAPI Backend
    ↓ JSON response
React Frontend (renders results)
    ↓
User sees ranked matches
```

---

## Complete Architecture

### Three-Tier Architecture

```
┌─────────────────────────────────────┐
│      User Browser                   │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  Frontend Container (React/TS)      │
│  - React 18 + TypeScript            │
│  - Vite build tool                  │
│  - Nginx server                     │
│  - Port: 5173 → 80                  │
└─────────────────┬───────────────────┘
                  │ REST API / JSON
                  ▼
┌─────────────────────────────────────┐
│  Backend Container (FastAPI)        │
│  - Python 3.11                      │
│  - FastAPI + Uvicorn                │
│  - SQLAlchemy ORM                   │
│  - Matching Engine                  │
│  - Port: 8000                       │
└─────────────────┬───────────────────┘
                  │ SQL
                  ▼
┌─────────────────────────────────────┐
│  Database Container (PostgreSQL)    │
│  - PostgreSQL 15                    │
│  - Persistent volume                │
│  - 40 synthetic profiles            │
│  - Port: 5432 (internal)            │
└─────────────────────────────────────┘
```

All containers communicate through a custom Docker bridge network named `skillsync-network`.

---

## Matching Algorithm Explained

### Why No AI/ML?

I intentionally avoided machine learning because:
1. I need to be able to explain every score during review
2. ML would be a black box I couldn't defend
3. The matching logic needs to be deterministic and auditable
4. A weighted scoring system is more transparent and trustworthy

### Seven Scoring Dimensions

The algorithm evaluates compatibility across seven dimensions with the following weights:

| Dimension | Weight | Purpose |
|-----------|--------|---------|
| **Skills** | 35% | Coverage of needed skills + complementary skills |
| **Interests** | 20% | Shared project domains using Jaccard similarity |
| **Availability** | 15% | Weekly hours compatibility |
| **Collaboration Style** | 10% | Working style compatibility matrix |
| **Communication** | 10% | Preference compatibility matrix |
| **Timezone** | 5% | UTC offset distance scoring |
| **Experience** | 5% | Level proximity scoring |
| **TOTAL** | **100%** | |


### Manual Score Calculation Example

**User Preferences:**
- Needed Skills: React, Node.js
- User Interests: Web Development, SaaS Products
- Weekly Availability: 20 hours
- Timezone: UTC+5:30
- Preferred Experience: mid-level
- Collaboration Style: collaborative
- Communication: hybrid

**Profile: Sarah Chen**
- Skills: React (advanced), Node.js (advanced), PostgreSQL (intermediate), Docker (intermediate)
- Interests: Web Development, SaaS Products, Startup MVPs
- Availability: 20 hours/week
- Timezone: UTC+8
- Experience: mid-level
- Collaboration: collaborative
- Communication: hybrid

**Calculation:**

1. **Skills (35%):**
   - Needed coverage: 2/2 = 100%
   - Complementary: PostgreSQL, Docker
   - Formula: (100% × 0.7) + (2 × 0.05 × 0.3) = 70% + 3% = 73%
   - Weighted: 73 × 0.35 = **25.55**

2. **Interests (20%):**
   - Shared: Web Development, SaaS Products = 2
   - Union: Web Development, SaaS Products, Startup MVPs = 3
   - Jaccard: 2/3 = 66.67%
   - Weighted: 66.67 × 0.20 = **13.33**

3. **Availability (15%):**
   - User wants 20, Profile has 20
   - Perfect match = 100%
   - Weighted: 100 × 0.15 = **15.00**

4. **Collaboration Style (10%):**
   - collaborative + collaborative = 100%
   - Weighted: 100 × 0.10 = **10.00**

5. **Communication (10%):**
   - hybrid + hybrid = 100%
   - Weighted: 100 × 0.10 = **10.00**

6. **Timezone (5%):**
   - Difference: |5.5 - 8| = 2.5 hours
   - Score: 100% (0-2 hours = 100)
   - Weighted: 100 × 0.05 = **5.00**

7. **Experience (5%):**
   - mid-level + mid-level = 100%
   - Weighted: 100 × 0.05 = **5.00**

**Overall Score:** 25.55 + 13.33 + 15.00 + 10.00 + 10.00 + 5.00 + 5.00 = **83.88%**

This profile would rank highly due to perfect needed skills coverage, good interest overlap, and excellent working compatibility.

---

## Database Design

### Schema

**collaborator_profiles**
- id (PK)
- name
- professional_title
- bio
- experience_level
- years_of_experience
- weekly_availability_hours
- timezone
- collaboration_style
- communication_preference
- preferred_team_size
- created_at

**skills**
- id (PK)
- name (unique)
- category

**project_interests**
- id (PK)
- name (unique)
- description

**profile_skills** (junction table)
- profile_id (FK)
- skill_id (FK)
- proficiency_level

**profile_interests** (junction table)
- profile_id (FK)
- interest_id (FK)

### Data Preparation

The database contains **40 original synthetic profiles** created specifically for this project. Each profile includes:
- Unique name and bio
- Varied skill sets (2-5 skills per profile)
- Multiple project interests
- Diverse experience levels (junior to lead)
- Different availability (10-35 hours/week)
- Various timezones (UTC-8 to UTC+9)
- Different working preferences

**Seeding Process:**
1. Application startup triggers `init_database()`
2. Creates all tables if they don't exist
3. Calls `seed_data()` which checks if data already exists
4. If empty, inserts skills, interests, and profiles
5. Seeds are idempotent—restarting doesn't duplicate data

---

## Docker Architecture

### Custom Network

All services communicate through `skillsync-network`, a custom Docker bridge network. This provides:
- Service discovery by name (e.g., `database`, `backend`)
- Network isolation from host
- Container-to-container communication

### Services

**database:**
- Image: postgres:15-alpine
- Environment: POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
- Volume: `skillsync-postgres-data` (persistent)
- Health check: `pg_isready`
- Network: skillsync-network

**backend:**
- Build: ./backend/Dockerfile
- Port: 8000:8000
- Depends on: database (waits for healthy)
- Health check: curl to /api/health
- Connection retry: 30 attempts with 2s intervals
- Network: skillsync-network

**frontend:**
- Build: ./frontend/Dockerfile (multi-stage)
- Port: 5173:80 (Nginx serves on port 80)
- Depends on: backend
- Health check: wget to localhost
- Network: skillsync-network

### Persistent Volume

`skillsync-postgres-data` ensures:
- Database survives container restarts
- Seed data persists
- No duplicate inserts on restart

### Commands

```bash
# Start all services
docker compose up

# Build and start (fresh build)
docker compose up --build

# Stop all services
docker compose down

# Stop and remove volumes (fresh start)
docker compose down -v

# View logs
docker compose logs -f

# Check health
docker compose ps
```

---

## API Endpoints

### GET /api/health
Returns backend and database status.

**Response:**
```json
{
  "status": "healthy",
  "service": "SkillSync Backend",
  "database": "connected"
}
```

### GET /api/options
Returns all valid form options.

**Response:**
```json
{
  "skills": ["React", "Node.js", ...],
  "skills_by_category": {
    "frontend": ["React", "Vue.js", ...],
    "backend": ["Python", "Node.js", ...]
  },
  "project_interests": ["Web Development", ...],
  "experience_levels": ["junior", "mid-level", "senior", "lead"],
  "collaboration_styles": ["collaborative", "independent", "flexible"],
  "communication_preferences": ["async", "sync", "hybrid"],
  "team_sizes": ["small (2-3)", "medium (4-6)", "large (7+)"],
  "timezones": ["UTC-8", "UTC+0", "UTC+8", ...]
}
```

### GET /api/profiles
Returns all collaborator profiles (limit: 50).

### GET /api/profiles/{id}
Returns a single profile by ID.

### POST /api/matches
Find matching collaborators.

**Request:**
```json
{
  "user_skills": ["Python", "React"],
  "needed_skills": ["Node.js", "PostgreSQL"],
  "project_interests": ["Web Development", "SaaS Products"],
  "preferred_experience": "mid-level",
  "weekly_availability": 20,
  "timezone": "UTC+5:30",
  "preferred_team_size": "small (2-3)",
  "collaboration_style": "collaborative",
  "communication_preference": "hybrid"
}
```

**Response:**
```json
{
  "total_profiles_evaluated": 40,
  "matches_returned": 10,
  "scoring_weights": {
    "skills": 0.35,
    "interests": 0.20,
    ...
  },
  "matches": [
    {
      "rank": 1,
      "profile_id": 3,
      "name": "Sarah Chen",
      "overall_score": 83.9,
      "score_breakdown": {
        "skills": 94.0,
        "interests": 90.0,
        ...
      },
      "matched_skills": ["React", "Node.js"],
      "complementary_skills": ["PostgreSQL", "Docker"],
      "shared_interests": ["Web Development", "SaaS Products"],
      "match_reasons": ["Strong match on 2 needed skills", ...],
      "trade_offs": []
    }
  ]
}
```

---

## Why This Tech Stack?

### Why FastAPI?
- Modern Python framework with automatic API docs
- Native async support
- Pydantic validation out of the box
- Fast development and excellent DX
- Built-in OpenAPI/Swagger documentation

### Why PostgreSQL?
- Robust relational database
- Excellent for structured data with relationships
- Strong data integrity with foreign keys
- Wide Docker support
- Industry standard for production applications

### Why React + TypeScript?
- Modern, component-based UI
- Type safety prevents runtime errors
- Excellent developer tooling
- Large ecosystem and community
- JTP requirement for modern framework

### Why Docker Compose?
- Ensures reproducible environment
- Plug-and-play deployment
- Service orchestration out of the box
- Network isolation and management
- Volume persistence for database

---

## Security Considerations

### What's Implemented:
- CORS configured for localhost development
- Environment variables for sensitive config
- `.env` files excluded from Git
- Database credentials not hardcoded
- Health checks for all services
- Connection retry logic for reliability

### Development vs Production:
- Current setup uses development-safe defaults
- For production, would add:
  - HTTPS/TLS
  - Secrets management (Docker secrets, Vault)
  - Rate limiting
  - Authentication/authorization
  - Input sanitization at all levels
  - Database connection pooling limits
  - Comprehensive logging and monitoring

---

## Limitations

### Known Constraints:
1. **Authentication:** No user accounts or authentication (out of scope for JTP requirements)
2. **Scalability:** Single-instance database, no load balancing (suitable for demo)
3. **Real-time:** No WebSocket or live updates (not required)
4. **Testing Coverage:** Unit tests for matching engine, limited integration tests (time constraint)
5. **Edge Cases:** Some unusual timezone formats may not parse correctly
6. **Profile Updates:** No admin interface for adding/editing profiles (static seed data)

### Intentional Scope Decisions:
- No machine learning (explainability requirement)
- No external APIs (offline-capable requirement)
- No cloud deployment (local Docker focus)
- No complex animations (completion priority)

---

## Future Improvements

If I had more time or were taking this to production:

1. **User Accounts:** Allow users to create profiles and search for each other
2. **Messaging:** In-app communication between matched collaborators
3. **Advanced Filters:** Filter by specific criteria before matching
4. **Save Searches:** Persist preferences and match history
5. **Match Notifications:** Alert users to new high-compatibility profiles
6. **Admin Dashboard:** Manage profiles, view analytics
7. **Weighted Customization:** Let users adjust dimension weights
8. **Integration Tests:** Full end-to-end testing with Playwright/Cypress
9. **Performance:** Caching, database indexing optimization
10. **Internationalization:** Multi-language support

---

## Reviewer Q&A: 30 Common Questions


### 1. Why did you choose a matching project?
I wanted to build something that solves a real problem I've experienced—finding compatible collaborators. Most platforms focus on job matching, but project collaboration has different needs: complementary skills, shared interests, and compatible working styles matter more than credentials.

### 2. What makes SkillSync special compared to LinkedIn or other platforms?
SkillSync provides explainable, multi-dimensional matching with score breakdowns. LinkedIn shows profiles, but doesn't explain compatibility. SkillSync evaluates seven dimensions and tells you exactly why someone is a good match and what trade-offs exist.

### 3. Why didn't you use machine learning?
Three reasons: (1) I need to explain every score during review, (2) ML would require training data I don't have, and (3) a deterministic algorithm is more transparent and trustworthy for users. The weighted scoring system is explainable and auditable.

### 4. How do you ensure the matching algorithm is fair?
The algorithm uses objective, quantifiable metrics across all dimensions. Weights are balanced to prevent any single factor from dominating. Every profile is evaluated with the same logic, and tie-breaking uses stable sorting (overall score, then skill score, then profile ID).

### 5. Walk me through the scoring weights. Why those percentages?
Skills (35%) is highest because it's the most concrete compatibility factor. Interests (20%) matter for project alignment. Availability (15%) is practical—you can't collaborate if schedules don't align. Collaboration/communication styles (10% each) affect working dynamics. Timezone (5%) and experience (5%) are lower because they're more flexible.

### 6. What if I disagree with the weights?
The weights are configurable in `SCORING_WEIGHTS` dictionary. In a production version, users could customize weights based on what matters most to them. The current weights represent a balanced default.

### 7. How does the skills scoring avoid rewarding quantity over quality?
Skills scoring has two components: needed skills coverage (70%) and complementary skills bonus (30%, capped). This means having 50 irrelevant skills won't help—only needed skills and genuinely complementary skills contribute to the score.

### 8. What's the Jaccard similarity you mentioned?
Jaccard similarity = size of intersection / size of union. For interests like {Web, Mobile, AI} and {Web, Mobile, Gaming}, the intersection is 2, union is 4, so Jaccard = 0.5 or 50%. It's a standard way to measure set similarity.

### 9. How do you handle edge cases like empty preferences?
Empty or missing preferences get neutral scores (typically 50%). This prevents penalizing flexible users while still allowing preferences to influence results when specified.

### 10. Is the matching deterministic?
Yes. Same input and same database state always produce the same ranked results. This is critical for debugging and user trust. Results are sorted by overall score, then skill score, then profile ID for stable tie-breaking.

### 11. How many profiles can the system handle?
Current implementation evaluates all profiles in memory. For 40 profiles, response time is <100ms. For production with thousands of profiles, I'd add database-level filtering and indexing before scoring, plus pagination.

### 12. Why FastAPI instead of Flask or Django?
FastAPI has automatic API documentation, native async support, and built-in Pydantic validation. It's faster than Flask for async workloads and lighter than Django for API-only applications. The auto-generated Swagger docs at /docs are incredibly useful.

### 13. Why PostgreSQL instead of MongoDB?
My data is highly relational—profiles have many-to-many relationships with skills and interests. PostgreSQL's foreign keys, joins, and ACID guarantees make this schema natural. MongoDB would require more complex application-level relationship management.

### 14. Explain your database schema.
Five tables: `collaborator_profiles` (main entity), `skills`, `project_interests`, and two junction tables (`profile_skills`, `profile_interests`) for many-to-many relationships. The junction tables enable efficient queries and avoid data duplication.

### 15. How is the seed data loaded?
On application startup, `init_database()` creates tables, then `seed_data()` checks if data exists. If the database is empty, it inserts 40 synthetic profiles with varied attributes. The function is idempotent—running it multiple times won't duplicate data.

### 16. Are the profiles real people?
No. All 40 profiles are original fictional personas created specifically for this project. No LinkedIn profiles, Kaggle datasets, or real individuals were used. This ensures originality and avoids any data privacy concerns.

### 17. Why Docker Compose?
Docker Compose provides reproducible, isolated environments with service orchestration. Running `docker compose up` handles network creation, volume mounting, service dependencies, and health checks automatically. It's the simplest way to ensure "plug and play" deployment.

### 18. Explain the custom Docker network.
`skillsync-network` is a bridge network that allows containers to communicate using service names (e.g., `backend` can reach `database:5432`). This provides DNS-based service discovery and isolates the application from other Docker networks on the host.

### 19. What happens if the database isn't ready when the backend starts?
The backend uses connection retry logic: it attempts to connect up to 30 times with 2-second intervals. Docker Compose also uses health checks and `depends_on: condition: service_healthy` to ensure database readiness before starting the backend.

### 20. Why is the frontend in a separate container?
Separation of concerns. The frontend is a static React SPA served by Nginx, while the backend is a Python API server. This allows independent scaling, deployment, and development. It also matches real-world architectures where frontend and backend are separate services.

### 21. How do frontend and backend communicate?
The frontend makes HTTP requests to `http://localhost:8000/api/*`. CORS is configured in FastAPI to allow requests from `localhost:5173`. In the Docker nginx config, there's also a proxy rule for `/api` requests for internal routing.

### 22. What testing did you implement?
Unit tests for the matching engine covering score boundaries, deterministic behavior, tie-breaking, and edge cases. Tests verify that weights sum to 100%, scores stay between 0-100, and identical inputs produce identical outputs. I prioritized testing the core matching logic over integration tests due to time constraints.

### 23. How would you test this in production?
I'd add: (1) integration tests with pytest-httpx for API endpoints, (2) frontend tests with React Testing Library, (3) end-to-end tests with Playwright, (4) load testing with Locust, and (5) database migration testing. I'd also implement CI/CD with GitHub Actions.

### 24. What happens when a user submits invalid data?
Pydantic validates all incoming requests. Invalid data returns a 422 Unprocessable Entity with detailed error messages indicating which fields failed validation and why. This prevents corrupt data from reaching the matching engine or database.

### 25. How do you prevent SQL injection?
SQLAlchemy ORM handles parameterization automatically. All queries use ORM methods or parameterized raw SQL, never string interpolation. User input never directly touches SQL query strings.

### 26. What are the environment variables?
Database connection string, API host/port, and CORS origins. These are documented in `.env.example` with safe development defaults. Production would use secrets management (Docker secrets, HashiCorp Vault, or cloud provider secret stores).

### 27. How do you ensure no secrets are committed to Git?
`.gitignore` explicitly excludes `.env`, `*.env` files (except `.env.example`), and other sensitive files. I reviewed Git status before every commit to verify no secrets were staged.

### 28. Can this run offline?
Yes, after `docker compose build`. All dependencies are bundled in the Docker images, and the synthetic dataset is self-contained. No external API calls are required for core functionality.

### 29. What's the most complex part of the code?
The matching engine's scoring logic. It balances multiple dimensions with different calculation methods (Jaccard similarity, timezone offset math, compatibility matrices), normalizes scores to 0-100, applies weights correctly, and generates human-readable explanations—all while remaining deterministic and efficient.

### 30. If you had one more day, what would you add?
Comprehensive integration tests, frontend unit tests with React Testing Library, more visual polish (animations, better mobile responsive design), and an admin panel for managing profiles. Also, I'd add more extensive error handling and user feedback for edge cases.

---

## Deployment Verification Checklist

Before demo/review, verify:

- [ ] `docker compose up --build` succeeds
- [ ] All three containers start and become healthy
- [ ] Frontend accessible at http://localhost:5173
- [ ] Backend accessible at http://localhost:8000
- [ ] Swagger docs accessible at http://localhost:8000/docs
- [ ] GET /api/health returns healthy
- [ ] GET /api/options returns data
- [ ] Landing page renders correctly
- [ ] Can navigate through all 5 form steps
- [ ] Can submit preferences and get matches
- [ ] Match results display with scores and breakdowns
- [ ] Expandable score breakdowns work
- [ ] "Adjust Preferences" button returns to form
- [ ] No console errors in browser
- [ ] No error logs in Docker containers
- [ ] Restarting containers doesn't duplicate database records

---

## Contact & Support

**Project:** SkillSync
**Category:** Matching / Recommendation Service
**Developed for:** JTP 2026 Project Round
**Repository:** https://github.com/Sumant3086/SkillSync-JTP

For questions during review, please refer to this guide or ask me to explain any specific component in detail. I can walk through the code, demonstrate features, or explain any technical decision.

---

**End of Review Guide**
