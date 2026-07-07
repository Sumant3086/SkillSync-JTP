# SkillSync

**Find the right collaborator, not just another profile.**

*Explainable Collaborator Matching Platform*

---

**Developed for the JTP 2026 Project Round**

## Project Overview

SkillSync is a full-stack web application that helps users find ideal project collaborators through intelligent, explainable matching. Unlike traditional platforms that rely solely on job titles or a handful of skills, SkillSync evaluates multiple compatibility dimensions to recommend the best collaborators for your project needs.

## Why This Project

I chose to build a **Matching/Recommendation Service** because successful collaboration depends on much more than technical skills alone. SkillSync addresses the real-world problem of finding compatible collaborators by considering:

- Complementary skill sets
- Shared project interests
- Working style compatibility
- Availability alignment
- Timezone compatibility
- Communication preferences
- Experience level matching

## What Makes SkillSync Special

### Explainable Matching
Every match comes with a complete breakdown showing exactly why a collaborator was recommended, including:
- Overall compatibility percentage
- Individual scoring dimensions
- Matched and complementary skills
- Shared interests
- Clear match reasons
- Honest trade-offs

### Deterministic & Transparent
No black-box algorithms or machine learning. The matching logic uses a weighted scoring system that produces consistent, explainable results that can be manually verified.

### Complete Self-Contained Solution
- Original synthetic dataset (40 diverse collaborator profiles)
- No external API dependencies
- Runs entirely offline after Docker images are built
- Plug-and-play architecture

## Technology Stack

**Frontend:**
- React 18 with TypeScript
- Vite (build tool)
- Original custom CSS
- Fetch API

**Backend:**
- Python 3.11
- FastAPI (REST API framework)
- SQLAlchemy (ORM)
- Pydantic (validation)
- Uvicorn (ASGI server)
- Pytest (testing)

**Database:**
- PostgreSQL 15

**Infrastructure:**
- Docker & Docker Compose
- Custom bridge network
- Persistent named volumes

## Docker Architecture

SkillSync uses a three-container architecture orchestrated by Docker Compose:

### Services

**database (PostgreSQL 15)**
- Stores collaborator profiles, skills, and interests
- Persistent volume: `skillsync-postgres-data`
- Health check: `pg_isready`
- Internal port: 5432

**backend (FastAPI + Python 3.11)**
- REST API and matching engine
- Exposed port: 8000
- Health check: `/api/health`
- Depends on: database (waits for healthy status)
- Connection retry: 30 attempts with 2s intervals

**frontend (React + Nginx)**
- Static React SPA served by Nginx
- Exposed port: 5173 (maps to internal 80)
- Multi-stage build (Node build → Nginx serve)
- Health check: HTTP GET to /

### Custom Network

All services communicate through `skillsync-network`, a custom Docker bridge network. This enables:
- Service discovery by name (e.g., `backend` can reach `database:5432`)
- Network isolation
- Container-to-container communication

### Volume Persistence

The `skillsync-postgres-data` volume ensures database persistence across container restarts. Seed data loads once and remains available.

## Design Decisions

### Why FastAPI?
- Modern Python framework with excellent async support
- Automatic OpenAPI documentation (/docs endpoint)
- Built-in Pydantic validation
- Fast and lightweight for API-only applications

### Why PostgreSQL?
- Robust relational database perfect for structured data
- Excellent support for many-to-many relationships
- Strong data integrity with foreign keys
- Industry standard with wide Docker support

### Why React + TypeScript?
- Component-based architecture for reusable UI
- Type safety prevents runtime errors
- Modern tooling and development experience
- Meets JTP requirement for modern JavaScript framework

### Why No Machine Learning?
- Explainability requirement—every score must be defensible
- Deterministic results build user trust
- No training data or model maintenance overhead
- Weighted algorithm is transparent and auditable

### Architecture Choices
- **Three-tier separation:** Clear boundaries between presentation, logic, and data
- **RESTful API:** Standard, well-understood interface
- **Docker Compose:** Reproducible environments, plug-and-play deployment
- **Custom CSS:** Original design, no templates or third-party UI libraries

## Quick Start

### Prerequisites
- Docker
- Docker Compose
- Git

### Installation & Running

1. Clone the repository:
```bash
git clone https://github.com/Sumant3086/SkillSync-JTP.git
cd SkillSync-JTP
```

2. Start the application:
```bash
docker compose up
```

Or rebuild and start:
```bash
docker compose up --build
```

3. Access the application:
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

The application will automatically:
- Initialize the database schema
- Load synthetic collaborator profiles
- Configure all services
- Be ready to use

## Project Structure

```
SkillSync-JTP/
├── frontend/              # React TypeScript frontend
│   ├── src/
│   │   ├── components/   # Reusable UI components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API client
│   │   ├── types/        # TypeScript definitions
│   │   └── styles/       # CSS files
│   ├── Dockerfile
│   └── package.json
│
├── backend/              # Python FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── core/        # Configuration
│   │   ├── database/    # Database setup
│   │   ├── models/      # SQLAlchemy models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic (matching engine)
│   │   └── main.py      # Application entry point
│   ├── tests/           # Pytest tests
│   ├── Dockerfile
│   └── requirements.txt
│
├── docker-compose.yml    # Multi-container orchestration
├── .env.example         # Environment template
├── .gitignore
├── README.md
├── REVIEW_GUIDE.md
└── DEVELOPMENT_LOG.md
```

## Features

- **Multi-Step Preference Form:** Intuitive workflow for entering project needs and preferences
- **Intelligent Matching:** Weighted algorithm evaluating 7 compatibility dimensions
- **Multiple Ranked Results:** View all potential matches, not just the top one
- **Detailed Score Breakdown:** Understand exactly how each score was calculated
- **Match Explanations:** Clear reasons why each collaborator was recommended
- **Trade-Off Insights:** Honest assessment of potential compatibility concerns
- **Responsive Design:** Works on desktop and mobile devices
- **Error Handling:** Graceful handling of edge cases and failures

## Matching Algorithm

### Overview

SkillSync uses a deterministic, weighted scoring algorithm that evaluates collaborators across seven compatibility dimensions. No machine learning or AI is used—every score is calculable, explainable, and reproducible.

### Scoring Dimensions

| Dimension | Weight | Description |
|-----------|--------|-------------|
| **Skills** | 35% | Coverage of needed skills + complementary skills value |
| **Project Interests** | 20% | Shared domains using Jaccard similarity |
| **Availability** | 15% | Weekly hours compatibility |
| **Collaboration Style** | 10% | Working style compatibility matrix |
| **Communication** | 10% | Preference compatibility matrix |
| **Timezone** | 5% | UTC offset distance scoring |
| **Experience** | 5% | Level proximity scoring |

### Example Calculation

**User needs:** React, Node.js  
**Profile has:** React (advanced), Node.js (advanced), PostgreSQL, Docker

**Skills Score:**
- Needed coverage: 2/2 = 100%
- Complementary skills: 2 additional skills
- Formula: (100% × 0.7) + (2 × 0.05 × 0.3) = 73%
- Weighted: 73 × 0.35 = 25.55 points

This process repeats for all dimensions, and the final overall score = sum of weighted scores.

### Key Features

- **Deterministic:** Same inputs always produce same outputs
- **Explainable:** Every score includes breakdown and reasoning
- **Balanced:** Weights prevent any single factor from dominating
- **Transparent:** Users see exactly why a match was recommended

### Trade-offs and Considerations

Each match result includes:
- **Match Reasons:** Positive compatibility factors
- **Trade-offs:** Honest assessments of potential concerns
- **Matched Skills:** Directly needed skills the profile provides
- **Complementary Skills:** Additional valuable skills
- **Shared Interests:** Common project domains

## API Documentation

### Endpoints

**GET /api/health**  
Health check endpoint.

**GET /api/options**  
Returns all valid form options (skills, interests, experience levels, etc.).

**GET /api/profiles**  
Returns all collaborator profiles (limit: 50).

**GET /api/profiles/{id}**  
Returns a single profile by ID.

**POST /api/matches**  
Find matching collaborators based on preferences.

**Request Body:**
```json
{
  "user_skills": ["Python", "React"],
  "needed_skills": ["Node.js", "PostgreSQL"],
  "project_interests": ["Web Development"],
  "preferred_experience": "mid-level",
  "weekly_availability": 20,
  "timezone": "UTC+5:30",
  "preferred_team_size": "small (2-3)",
  "collaboration_style": "collaborative",
  "communication_preference": "hybrid"
}
```

**Interactive API Docs:** http://localhost:8000/docs

## Testing

### Running Backend Tests

```bash
cd backend
pip install -r requirements.txt
pytest
```

### Test Coverage

The test suite includes:
- Scoring weight validation (must sum to 100%)
- Individual dimension score calculations
- Score boundary checks (0-100 range)
- Deterministic behavior verification
- Edge case handling (empty inputs, mismatches)
- Tie-breaking logic

### Manual Testing Checklist

1. Start application: `docker compose up`
2. Access frontend: http://localhost:5173
3. Complete all 5 form steps
4. Submit and verify matches appear
5. Expand score breakdowns
6. Test "Adjust Preferences" button
7. Verify no console errors

## Database Schema

### Tables

**collaborator_profiles**
- Core profile information (name, title, bio, experience, availability, timezone, preferences)

**skills**
- Skill catalog with categories (frontend, backend, devops, etc.)

**project_interests**
- Project domain catalog with descriptions

**profile_skills** (junction table)
- Many-to-many relationship between profiles and skills
- Includes proficiency_level (beginner, intermediate, advanced, expert)

**profile_interests** (junction table)
- Many-to-many relationship between profiles and interests

### Data Seeding

The application includes 40 original synthetic collaborator profiles with:
- Diverse skill combinations across 55+ skills
- Multiple project interests from 20 domains
- Varied experience levels (junior to lead)
- Different availability (10-35 hours/week)
- Global timezone coverage
- Mixed working style preferences

Seeding is automatic and idempotent—the database initializes on first startup and persists through restarts.

## Known Limitations

1. **No Authentication:** No user accounts or login system (out of scope)
2. **Static Profiles:** Profiles are seeded, no admin interface to add/edit
3. **No Real-time Updates:** Results are request/response, not live
4. **Single Instance:** Database is single-instance, no replication or sharding
5. **Limited Mobile Optimization:** Responsive but optimized for desktop

## Future Improvements

- User account system and authentication
- Profile creation and management
- Messaging between matched collaborators
- Save search preferences and match history
- Advanced filtering before matching
- Customizable scoring weights
- Admin dashboard with analytics
- Comprehensive integration and E2E tests
- Performance optimizations (caching, indexing)
- Internationalization (i18n)

## Troubleshooting

**Problem:** Backend fails to connect to database  
**Solution:** Wait 30 seconds for database initialization, check `docker compose logs database`

**Problem:** Frontend shows "Failed to load options"  
**Solution:** Ensure backend is healthy: `curl http://localhost:8000/api/health`

**Problem:** Port already in use  
**Solution:** Stop conflicting services or change ports in `docker-compose.yml`

**Problem:** Seed data duplicated  
**Solution:** The seed function is idempotent. If duplicates appear, run `docker compose down -v` to reset volumes.

**Problem:** Frontend not updating after code changes  
**Solution:** Rebuild frontend: `docker compose up --build frontend`


## Originality Statement

This project was built entirely from scratch specifically for the JTP 2026 Project Round. All components are original work:

- **Code:** All backend Python code, frontend React/TypeScript code, and configuration files were written specifically for this project
- **UI Design:** Original custom CSS designed for SkillSync, no templates or third-party UI libraries used
- **Data:** 40 synthetic collaborator profiles created specifically for this project, no real profiles or external datasets used
- **Architecture:** Original system design and implementation
- **Documentation:** All documentation written for this project

No code was copied from GitHub repositories, online tutorials, or other projects. No third-party templates, cloned repositories, or downloaded UI kits were used.

## Compliance

- **Backend Language:** Python ✓
- **Frontend Framework:** React (modern JavaScript framework) ✓
- **Architecture:** Frontend, backend, and database in separate Docker containers ✓
- **Communication:** Frontend and backend communicate through REST API ✓
- **Docker Network:** Custom bridge network (skillsync-network) ✓
- **Startup Command:** `docker compose up` ✓
- **Git Version Control:** Complete commit history from project start ✓
- **Documentation:** README.md, REVIEW_GUIDE.md, code docstrings ✓
- **No AI/ML:** Deterministic weighted algorithm, no machine learning ✓
- **Original Dataset:** Synthetic profiles created for this project ✓

## License

MIT License - Created for JTP 2026 Project Round

---

**For detailed review preparation, see [REVIEW_GUIDE.md](./REVIEW_GUIDE.md)**
