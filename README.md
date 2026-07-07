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

## Architecture

SkillSync uses a modern three-tier architecture with complete service separation:

```
User Browser
     ↓
Frontend Container (React + TypeScript)
     ↓ REST API / JSON
Backend Container (Python FastAPI)
     ↓ SQL
Database Container (PostgreSQL)
```

All containers communicate through a custom Docker network (`skillsync-network`) with proper health checks and dependency management.

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

*[Detailed algorithm documentation will be added]*

## Testing

*[Testing instructions will be added]*

## Originality Statement

This project was built from scratch specifically for the JTP 2026 Project Round. All code, UI design, and synthetic data are original work created for this submission. No third-party templates, cloned repositories, or copied projects were used.

## License

MIT License - Created for JTP 2026 Project Round
