# SkillSync - Deployment Guide

This guide provides complete instructions for deploying and running SkillSync in various environments.

---

## Table of Contents

1. [Quick Start (Docker)](#quick-start-docker)
2. [Prerequisites](#prerequisites)
3. [Environment Configuration](#environment-configuration)
4. [Deployment Methods](#deployment-methods)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)
7. [Maintenance](#maintenance)

---

## Quick Start (Docker)

**Easiest way to run SkillSync - works on Windows, Mac, and Linux:**

```bash
# Clone the repository
git clone https://github.com/Sumant3086/SkillSync-JTP.git
cd SkillSync-JTP

# Start all services
docker-compose up --build
```

That's it! The application will be available at:
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## Prerequisites

### For Docker Deployment (Recommended)

- **Docker Desktop** (version 20.10 or higher)
  - Windows: [Download Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)
  - Mac: [Download Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/)
  - Linux: [Install Docker Engine](https://docs.docker.com/engine/install/)
- **Docker Compose** (usually included with Docker Desktop)
- **Git** (to clone the repository)

**Minimum System Requirements:**
- RAM: 4GB (8GB recommended)
- Disk Space: 2GB free
- CPU: 2 cores minimum

### For Local Development (Without Docker)

- **Backend:**
  - Python 3.11 or higher
  - PostgreSQL 15 or higher
  - pip (Python package manager)

- **Frontend:**
  - Node.js 18 or higher
  - npm or yarn

---

## Environment Configuration

### Docker Deployment (Default)

No configuration needed! The `docker-compose.yml` file includes all necessary environment variables with secure defaults.

If you want to customize, you can create a `.env` file in the root directory:

```env
# Database Configuration
POSTGRES_USER=skillsync_user
POSTGRES_PASSWORD=skillsync_password
POSTGRES_DB=skillsync_db

# Backend Configuration
BACKEND_PORT=8000

# Frontend Configuration (leave empty for Docker)
VITE_API_BASE_URL=
```

### Local Development Configuration

#### Backend `.env` file (backend/.env):

```env
DATABASE_URL=postgresql://skillsync_user:skillsync_password@localhost:5432/skillsync_db
```

#### Frontend `.env` file (frontend/.env):

```env
# Point to local backend
VITE_API_BASE_URL=http://localhost:8000
```

---

## Deployment Methods

### Method 1: Docker Compose (Recommended)

**Step-by-step:**

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Sumant3086/SkillSync-JTP.git
   cd SkillSync-JTP
   ```

2. **Start the application:**
   ```bash
   docker-compose up --build
   ```

   The `--build` flag ensures fresh builds. For subsequent runs, you can use:
   ```bash
   docker-compose up
   ```

3. **Run in detached mode (background):**
   ```bash
   docker-compose up -d
   ```

4. **View logs:**
   ```bash
   docker-compose logs -f
   ```

5. **Stop the application:**
   ```bash
   docker-compose down
   ```

6. **Stop and remove all data (fresh start):**
   ```bash
   docker-compose down -v
   ```

**What happens during startup:**
- PostgreSQL container starts first
- Database is initialized with schema
- 40 synthetic collaborator profiles are seeded
- Backend API starts and connects to database
- Frontend nginx server starts
- All services connect through `skillsync-network`

---

### Method 2: Local Development (Without Docker)

**For development and debugging:**

#### Step 1: Setup PostgreSQL

Install PostgreSQL 15 and create a database:

```bash
# On Mac (using Homebrew)
brew install postgresql@15
brew services start postgresql@15

# On Ubuntu/Debian
sudo apt-get install postgresql-15
sudo systemctl start postgresql

# On Windows
# Download and install from https://www.postgresql.org/download/windows/
```

Create the database:

```sql
CREATE USER skillsync_user WITH PASSWORD 'skillsync_password';
CREATE DATABASE skillsync_db OWNER skillsync_user;
GRANT ALL PRIVILEGES ON DATABASE skillsync_db TO skillsync_user;
```

#### Step 2: Start Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with DATABASE_URL
echo "DATABASE_URL=postgresql://skillsync_user:skillsync_password@localhost:5432/skillsync_db" > .env

# Run the backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at http://localhost:8000

#### Step 3: Start Frontend

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
echo "VITE_API_BASE_URL=http://localhost:8000" > .env

# Run development server
npm run dev
```

The frontend will be available at http://localhost:5173

---

## Verification

### Step 1: Check Container Status (Docker)

```bash
docker ps
```

You should see three containers running:
- `skillsync-database` (healthy)
- `skillsync-backend` (healthy)
- `skillsync-frontend` (healthy)

**Note:** If you see "unhealthy" status after rebuilding with the fixed Dockerfiles, containers are still working. The health check will turn healthy after 30-40 seconds.

### Step 2: Test Backend API

Open http://localhost:8000/docs in your browser or use curl:

```bash
# Health check
curl http://localhost:8000/api/health

# Should return:
# {"status":"healthy","service":"SkillSync Backend","database":"connected"}

# Get options
curl http://localhost:8000/api/options

# Get profiles
curl http://localhost:8000/api/profiles
```

### Step 3: Test Frontend

Open http://localhost:5173 in your browser. You should see:
- SkillSync landing page
- "Find My Matches" button
- Clean, professional UI

### Step 4: Complete User Flow Test

1. Click **"Find My Matches"**
2. Complete the 5-step wizard:
   - Select project interests
   - Select your skills
   - Select needed skills
   - Configure working preferences
   - Review and submit
3. View ranked match results
4. Expand score breakdowns
5. Check match reasons and trade-offs

**Expected behavior:**
- No console errors
- All steps load smoothly
- Results display with scores
- Score breakdowns are accurate
- Loading states appear during API calls

---

## Troubleshooting

### Issue: Containers won't start

**Solution 1:** Check if ports are available:
```bash
# Check if ports 5173, 8000, or 5432 are in use
# On Windows:
netstat -ano | findstr "5173"
netstat -ano | findstr "8000"
netstat -ano | findstr "5432"

# On Mac/Linux:
lsof -i :5173
lsof -i :8000
lsof -i :5432
```

If ports are in use, either stop the conflicting service or modify `docker-compose.yml` to use different ports.

**Solution 2:** Clean Docker environment:
```bash
docker-compose down -v
docker system prune -a
docker-compose up --build
```

### Issue: Backend shows "unhealthy" status

This is usually because `curl` is missing from the container. The fixed Dockerfiles include curl/wget.

**Rebuild containers:**
```bash
docker-compose down
docker-compose up --build
```

Wait 30-40 seconds for health checks to pass.

### Issue: Database connection errors

**Check database logs:**
```bash
docker logs skillsync-database
```

**Restart database:**
```bash
docker-compose restart database
```

**Fresh database start:**
```bash
docker-compose down -v
docker-compose up --build
```

### Issue: Frontend shows connection errors

**Check if backend is accessible:**
```bash
curl http://localhost:8000/api/health
```

**Check nginx logs:**
```bash
docker logs skillsync-frontend
```

**Verify environment variables:**
```bash
# Inside frontend container
docker exec skillsync-frontend env | grep VITE
```

### Issue: "Permission denied" errors on Linux

Run Docker commands with `sudo` or add your user to the docker group:
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Issue: Database not seeding

**Check backend logs:**
```bash
docker logs skillsync-backend
```

Look for messages like:
- "✓ Database tables created successfully"
- "✓ Seeded database with 40 collaborator profiles"

**Manual verification:**
```bash
# Connect to database
docker exec -it skillsync-database psql -U skillsync_user -d skillsync_db

# Check profiles
SELECT COUNT(*) FROM collaborator_profiles;
# Should return 40 or more

# Exit
\q
```

---

## Maintenance

### Viewing Logs

**All services:**
```bash
docker-compose logs -f
```

**Specific service:**
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f database
```

**Last N lines:**
```bash
docker logs --tail 50 skillsync-backend
```

### Restarting Services

**All services:**
```bash
docker-compose restart
```

**Specific service:**
```bash
docker-compose restart backend
```

### Updating the Application

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up --build
```

### Database Backup

**Export database:**
```bash
docker exec skillsync-database pg_dump -U skillsync_user skillsync_db > backup.sql
```

**Restore database:**
```bash
cat backup.sql | docker exec -i skillsync-database psql -U skillsync_user -d skillsync_db
```

### Cleaning Up

**Stop and remove containers:**
```bash
docker-compose down
```

**Remove containers and volumes (data loss):**
```bash
docker-compose down -v
```

**Clean Docker system:**
```bash
docker system prune -a
```

---

## Production Deployment Considerations

If deploying to production, consider:

### Security
- Change default database credentials
- Use environment secrets (Docker secrets, Vault)
- Enable HTTPS with SSL certificates
- Configure firewall rules
- Implement rate limiting
- Add authentication/authorization

### Scaling
- Use PostgreSQL replication
- Add Redis for caching
- Deploy multiple backend instances behind a load balancer
- Use CDN for frontend static files

### Monitoring
- Add application logging (ELK stack, Datadog)
- Set up health monitoring (Prometheus, Grafana)
- Configure alerts for failures
- Track performance metrics

### Backup
- Automated database backups
- Point-in-time recovery setup
- Off-site backup storage
- Regular restore testing

### Infrastructure
- Use Docker Swarm or Kubernetes for orchestration
- CI/CD pipeline for automated deployments
- Blue-green or canary deployment strategy
- Infrastructure as Code (Terraform, CloudFormation)

---

## Deployment on Cloud Platforms

### AWS (Elastic Beanstalk)

1. Install AWS CLI and EB CLI
2. Initialize application:
   ```bash
   eb init
   ```
3. Create environment:
   ```bash
   eb create skillsync-prod
   ```
4. Deploy:
   ```bash
   eb deploy
   ```

### Google Cloud (Cloud Run)

1. Build and push images:
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT-ID/skillsync-backend ./backend
   gcloud builds submit --tag gcr.io/PROJECT-ID/skillsync-frontend ./frontend
   ```
2. Deploy:
   ```bash
   gcloud run deploy skillsync-backend --image gcr.io/PROJECT-ID/skillsync-backend
   gcloud run deploy skillsync-frontend --image gcr.io/PROJECT-ID/skillsync-frontend
   ```

### Azure (Container Instances)

1. Create resource group
2. Deploy containers:
   ```bash
   az container create --resource-group skillsync-rg \
     --name skillsync-backend \
     --image skillsync-backend \
     --ports 8000
   ```

### Heroku

1. Install Heroku CLI
2. Create apps:
   ```bash
   heroku create skillsync-backend
   heroku create skillsync-frontend
   ```
3. Add PostgreSQL:
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```
4. Deploy:
   ```bash
   git push heroku main
   ```

---

## Support

For issues, questions, or contributions:
- **Repository:** https://github.com/Sumant3086/SkillSync-JTP
- **Documentation:** README.md, REVIEW_GUIDE.md
- **API Docs:** http://localhost:8000/docs (when running)

---

## Quick Command Reference

```bash
# Start application
docker-compose up --build

# Start in background
docker-compose up -d

# Stop application
docker-compose down

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Fresh start (removes data)
docker-compose down -v && docker-compose up --build

# Check status
docker ps

# Test backend
curl http://localhost:8000/api/health

# Test frontend
curl http://localhost:5173
```

---

**SkillSync - Explainable Collaborator Matching Platform**  
*JTP 2026 Project Round*
