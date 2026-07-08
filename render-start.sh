#!/bin/bash
set -e

echo "🚀 Starting SkillSync on Render..."

# Use Render's dynamic PORT or default to 8080
PORT=${PORT:-8080}

echo "📝 Port: $PORT"
echo "📝 Database URL: ${DATABASE_URL:0:30}..."

# Update nginx config with Render's PORT
sed -i "s/listen 8080;/listen $PORT;/" /etc/nginx/sites-available/default

# Start nginx in background
echo "🌐 Starting nginx..."
nginx -g "daemon off;" &
NGINX_PID=$!

# Wait a moment for nginx to start
sleep 2

# Initialize database
echo "💾 Initializing database..."
python -c "
from app.database.session import wait_for_db
from app.database.init_db import init_database, seed_data
from app.database.session import SessionLocal

wait_for_db()
init_database()
db = SessionLocal()
try:
    seed_data(db)
finally:
    db.close()
print('✅ Database ready!')
"

# Start FastAPI backend
echo "🚀 Starting FastAPI backend..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
UVICORN_PID=$!

echo "✅ SkillSync is running!"
echo "   - Frontend: http://localhost:$PORT"
echo "   - Backend API: http://localhost:8000"

# Wait for both processes
wait $NGINX_PID $UVICORN_PID
