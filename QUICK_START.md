# SkillSync - Quick Start Guide

**Get SkillSync running in 2 minutes!**

---

## Prerequisites

- **Docker Desktop** installed and running
- **Git** (to clone the repository)

---

## Step 1: Get the Code

```bash
git clone https://github.com/Sumant3086/SkillSync-JTP.git
cd SkillSync-JTP
```

---

## Step 2: Start the Application

```bash
docker-compose up --build
```

**What's happening:**
- PostgreSQL database starts first
- Backend API starts and connects to database
- Database gets seeded with 40 synthetic profiles
- Frontend nginx server starts
- All three containers connect via custom network

**Expected output:**
```
[+] Building ...
[+] Running 4/4
 ✔ Network skillsync-network   Created
 ✔ Container skillsync-database Started
 ✔ Container skillsync-backend  Started
 ✔ Container skillsync-frontend Started
```

**Wait for:**
```
skillsync-backend   | ✓ SkillSync backend ready!
```

---

## Step 3: Access the Application

Open your browser to:

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:5173 |
| **Backend API** | http://localhost:8000 |
| **API Docs** | http://localhost:8000/docs |

---

## Step 4: Test the Workflow

1. **Landing Page**
   - Open http://localhost:5173
   - Click **"Find My Matches"**

2. **Complete the Wizard** (5 steps):
   - **Step 1:** Select project interests (e.g., "Web Development", "SaaS Products")
   - **Step 2:** Select your skills (e.g., "React", "TypeScript")
   - **Step 3:** Select needed skills (e.g., "Python", "FastAPI")
   - **Step 4:** Configure preferences (availability, timezone, styles)
   - **Step 5:** Review and submit

3. **View Results**
   - See top 10 ranked matches
   - Check compatibility scores (color-coded)
   - Expand score breakdowns
   - Read match reasons
   - Review trade-offs

---

## Verify Everything Works

### Check Container Status

```bash
docker ps
```

You should see:
```
CONTAINER ID   IMAGE                     STATUS                    PORTS                    NAMES
...            skillsync-jtp-frontend    Up X minutes (healthy)    0.0.0.0:5173->80/tcp    skillsync-frontend
...            skillsync-jtp-backend     Up X minutes (healthy)    0.0.0.0:8000->8000/tcp  skillsync-backend
...            postgres:15-alpine        Up X minutes (healthy)    5432/tcp                skillsync-database
```

**Note:** If status shows "unhealthy", wait 30-40 seconds for health checks to complete, or rebuild:
```bash
docker-compose down
docker-compose up --build
```

### Test Backend API

```bash
# Health check
curl http://localhost:8000/api/health

# Should return:
# {"status":"healthy","service":"SkillSync Backend","database":"connected"}
```

### Test Frontend

Open http://localhost:5173 in your browser - you should see the SkillSync landing page.

---

## Common Commands

### Start (first time or after changes)
```bash
docker-compose up --build
```

### Start (subsequent runs)
```bash
docker-compose up
```

### Start in background
```bash
docker-compose up -d
```

### Stop
```bash
docker-compose down
```

### View logs
```bash
docker-compose logs -f
```

### Fresh start (removes all data)
```bash
docker-compose down -v
docker-compose up --build
```

### Run tests
```bash
docker exec skillsync-backend pytest tests/ -v
```

---

## Troubleshooting

### Port Already in Use

If you see errors about ports 5173, 8000, or 5432 being in use:

**Check what's using the port:**
```bash
# Windows
netstat -ano | findstr "5173"
netstat -ano | findstr "8000"

# Mac/Linux
lsof -i :5173
lsof -i :8000
```

**Solution:** Stop the conflicting service or change ports in `docker-compose.yml`

### Containers Won't Start

```bash
# Clean everything and rebuild
docker-compose down -v
docker system prune -a
docker-compose up --build
```

### Database Connection Errors

```bash
# Check database logs
docker logs skillsync-database

# Restart database
docker-compose restart database
```

### Frontend Shows Connection Errors

```bash
# Verify backend is running
curl http://localhost:8000/api/health

# Check frontend logs
docker logs skillsync-frontend
```

---

## What's Included

- **40 Synthetic Collaborator Profiles**
- **55+ Skills** across 8 categories
- **20 Project Interest Domains**
- **7-Dimension Matching Algorithm**
- **Explainable Results** with score breakdowns

---

## Next Steps

- Read **README.md** for detailed project information
- Check **DEPLOYMENT_GUIDE.md** for advanced deployment options
- Review **REVIEW_GUIDE.md** for technical deep-dive
- Explore **API documentation** at http://localhost:8000/docs

---

## Architecture at a Glance

```
┌─────────────────┐
│  Browser        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  nginx          │ Port 5173
│  (Frontend)     │
└────────┬────────┘
         │ /api requests
         ▼
┌─────────────────┐
│  FastAPI        │ Port 8000
│  (Backend)      │
└────────┬────────┘
         │ SQL
         ▼
┌─────────────────┐
│  PostgreSQL     │ Internal
│  (Database)     │
└─────────────────┘
```

All containers communicate through `skillsync-network`.

---

## Support

- **Repository:** https://github.com/Sumant3086/SkillSync-JTP
- **Issues:** Check DEPLOYMENT_GUIDE.md troubleshooting section
- **Documentation:** See README.md and other .md files

---

**That's it! You now have SkillSync running locally.**

🚀 Start matching collaborators at http://localhost:5173
