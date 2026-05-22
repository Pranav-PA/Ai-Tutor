#!/bin/sh
set -e

# Start FastAPI backend in the background
python -m uvicorn backend.main:app --host 0.0.0.0 --port 18080 &
BACKEND_PID=$!

# Start Next.js frontend in the foreground (keeps container alive)
cd /app/frontend && ./node_modules/.bin/next start -p 38173 &
FRONTEND_PID=$!

# If either process exits, kill the other and exit
wait $BACKEND_PID $FRONTEND_PID
